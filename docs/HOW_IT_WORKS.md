# 翻译机制详解（HOW IT WORKS）

本文说明 `antigravity-zh` 到底往客户端里放了什么、翻译是怎么一步步发生的、
以及怎样安全地加词条和规则。

- 面向使用者：看 [README](../README.md) 就够了
- 面向想改代码 / 加词条 / 排查问题的人：看这里

---

## 1. 总览：三层结构

```
┌──────────────────────────────────────────────────────────┐
│ install.py      安装器：解包 asar → 注入代码 → 重新打包   │
│                 （同时负责备份 / 还原 / 状态检查）         │
├──────────────────────────────────────────────────────────┤
│ dicts/engine.js 翻译引擎：DOM 监听 + 翻译流水线 + 动态规则 │
├──────────────────────────────────────────────────────────┤
│ dicts/zh_cn.json 词典：6297 条 "英文原文": "中文译文"      │
└──────────────────────────────────────────────────────────┘
```

关键点：**不改动客户端的业务代码**。安装器只在几个入口文件末尾追加一段自包含的
IIFE（立即执行函数），它运行时是只读的旁观者——不拦截网络、不改业务状态。

---

## 2. 补丁是怎么打进 app.asar 的

### 2.1 asar 是什么

Electron 的 `app.asar` 是一个简单的归档格式：

```
[4 字节 pickle 长度][pickle 头(JSON 结构表)][4 字节 payload 长度][文件内容拼接]
```

`asar.py` 用纯 Python 实现了解包与打包（与官方 `@electron/asar` 格式一致），
因此**不需要安装 Node.js**。

### 2.2 注入流程

```python
# install.py（简化）
asar.extract(asar_path, tmp)                 # 1. 解包到临时目录
inject_preload(tmp)                          # 2. 注入渲染引擎
inject_wizard_preload(tmp)                   #    安装向导
inject_native(tmp)                           # 3. 菜单 / 托盘 / 原生弹窗 / 加载画面
asar.pack(tmp, staged_asar)                  # 4. 重新打包到同目录
os.replace(staged_asar, asar_path)           # 5. 原子替换（失败自动回滚）
```

几个关键设计：

| 设计 | 解决的问题 |
| --- | --- |
| 首次安装把原版复制为 `app.asar.bak` | 永远有干净的还原源，多次重装不会覆盖备份 |
| 打包到**同目录**再 `os.replace` | 避免跨盘复制中断产生损坏文件 |
| `chrome-devtools-mcp` 保持 unpacked | 官方自带的 unpacked 模块不能被塞进 asar |
| 锚点 + 从锚点到文件尾整体重建 | 旧版引擎残留会重复翻译，这里一并清除 |
| 检查 `Antigravity.exe` 进程 | 文件被占用时替换会失败 |

### 2.3 注入位置

| 目标文件 | 运行环境 | 作用 |
| --- | --- | --- |
| `dist/preload.js` | 渲染进程（主窗口） | 全部界面文本 |
| `dist/ideInstall/wizardPreload.js` | 渲染进程（安装向导） | 首次启动向导 |
| `dist/menu.js` | 主进程 | 原生菜单栏 |
| `dist/tray.js` | 主进程 | 托盘菜单 |
| `dist/main.js` | 主进程 | 原生对话框（退出确认等） |
| `dist/loadingOverlay.js` | 主进程 | 启动加载画面 |

每段注入代码都带一个标记常量，便于识别与清理：

```js
/* Antigravity Chinese Translation Injection v3-full */
```

---

## 3. 渲染引擎：翻译流水线

引擎是一个纯函数 `translate(text)`，加上一层 DOM 监听。核心逻辑位于
`dicts/engine.js` 的 `translateStringUncached()`。

### 3.1 初始化：三张 Map

安装时词典会被**内嵌**进 `preload.js`（`__DICT_ITEMS__` 占位符替换），
同时启动后还会尝试读取外部词典覆盖：

```
coreWords（少量内置） + dictionary（6297 条） + ~/.antigravity-zh/zh-CN.json
                ↓
exactLookup   : 原文 → 译文（区分大小写，O(1)）
lowerLookup   : 小写 → 译文（忽略大小写，先到先得）
tokenLookup   : 单个单词 → 译文（仅短句逐词兜底用）
translationCache : 600 字符内的结果缓存（上限 8000 条）
```

> `lowerLookup` 采用「先到先得」：词典按 key 小写排序，因此同名不同大小写的词条
> 需要在词典里显式声明（见 3.4）。

### 3.2 逐级匹配顺序

```
输入 "2 projects"
 ├─ 1. 纯标点?            no
 ├─ 2. 不含英文字母?      no
 ├─ 3. 纯快捷键组合?      no
 ├─ 4. 缓存命中?          no
 ├─ 5. 动态日志块?        no
 ├─ 6. exactLookup        "2 projects" 未命中
 ├─ 7. lowerLookup        "2 projects" 未命中
 ├─ 8. 去尾部标点重试      "2 projects" 未命中
 ├─ 9. 时长短语预处理     无数字单位，跳过
 ├─ 10. 动态规则          /^(\d+)\s+projects?$/ → "$1 个项目"  ✅ 命中
 └─ 返回 "2 个项目"
```

顺序的意义：

- **先词典后规则**：已校对过的固定文案不会被正则改写
- **先精确后忽略大小写**：允许 `Projects` 与 `projects` 共存
- **规则放最后**：动态规则只处理词典覆盖不到的、含变量的文案

### 3.3 动态块（模型日志状态）

这类文本由客户端运行时拼接，格式固定但数值变化，用**快速路径**处理：

```js
if (/^Worked for [\d smhd.]+$/.test(trimmed)) {
  return '已工作 ' + fmtDuration(...);   // Worked for 1h2m → 已工作 1 小时 2 分
}
if (/^Edited .* \+\d+ -\d+$/.test(trimmed)) { ... }   // 编辑了 file (+3 -1)
if (/^\d+ files? changed$/.test(trimmed)) { ... }     // 3 个文件已更改
if (/^Explored/.test(trimmed)) { ... }                // 浏览了 12 个文件
```

`fmtDuration` 负责紧凑时长的单位替换与补空格：

```
1d2h3m4.5s  →  1 天 2 小时 3 分 4.5 秒
```

### 3.4 大小写敏感的精确匹配

React 会把界面拆成多个文本节点，例如侧边栏标题 `Projects`，
而设置页的计数是 `" projects"`（前面带空格）单独成节点。

词库里两条同时存在：

```json
"Projects": "项目",
"projects": "个项目"
```

- `exactLookup.get("Projects")` 命中「项目」
- `exactLookup.get(" projects")` 未命中 → `lowerLookup.get(" projects")` 命中「个项目」

如果只保留忽略大小写的单表，两条会互相覆盖（旧版本就出现过后加的译名失效）。

### 3.5 尾部标点单独处理

英文句号、问号常被 React 拆成独立文本节点。引擎分两步处理：

1. 纯标点节点：`?` → `？`（快捷键上下文除外，避免 `Ctrl+,` 变成 `Ctrl+，`）
2. 整句末尾标点：先剥掉再查词，命中后按原标点补全角：

```
"Loading..."  →  "正在加载…"
"Delete?"     →  "删除？"
```

### 3.6 拆分句合并（父子句兜底）

React 有时把一句话拆成 3 个文本节点：

```html
<p class="text-lg">否 自动化 yet</p>   ← 逐节点翻译的恶果
```

引擎在翻译单个文本节点前，会先看一眼父节点：

```js
if (parent.childElementCount === 0 && parent.childNodes.length >= 2) {
  const combined = parent.textContent.replace(/\s+/g, ' ').trim();  // No automations yet
  const hit = exactLookup.get(combined) ?? lowerLookup.get(combined.toLowerCase());
  if (hit) {
    // 译文写到第一个文本节点，其余置空（保留节点结构，不影响 React 协调）
    ...
  }
}
```

结果：`No automations yet` → `暂无自动化任务`。

### 3.7 安全护栏：宁可不翻，也不给中英夹杂

| 规则 | 目的 |
| --- | --- |
| 整句 > 3 个单词且未命中词典 → 原样返回 | 避免「已失败 to 运行」 |
| 文本已含中文 → 原样返回 | 保证幂等，防止二次翻译 |
| 短句逐词兜底要求**每个** ≥2 字母单词都在词典里 | `Failed to run` 不会变成「已失败 to 运行」 |
| 纯快捷键组合 → 原样返回 | `Ctrl+Shift+P` 保持可读 |
| 代码/思考链/预览区域 → 整块跳过 | 自由文本不该逐词机翻 |

### 3.8 动态规则与二次查词

`dynamicRules` 是「整串锚定」的正则数组（189 条），匹配成功的返回值支持 `$1` 与回调：

```js
[/^Turn (\d+) of (\d+)$/i, '第 $1 轮（共 $2 轮）'],
[/^Version (.+)$/i, '版本 $1'],
[/^See\s+(\d+)\s+more$/i, '查看另外 $1 项'],
[/^Toggle\s+(.+)$/i, function (m, name) { return '切换 ' + translateCaptured(name); }],
```

`translateCaptured()` 会对捕获到的名称再做一次词典查询，避免出现：

```
❌ 「New Conversation」的快捷键：Ctrl+Shift+O
✅ 「新建对话」的快捷键：Ctrl+Shift+O
```

---

## 4. DOM 层：监听、队列、跳过

### 4.1 监听配置

```js
new MutationObserver(handleMutations).observe(document.documentElement, {
  childList: true,
  subtree: true,
  characterData: true,
  attributes: true,
  attributeFilter: ['placeholder', 'title', 'aria-label', 'value']
});
```

- **childList / characterData**：新出现的文本
- **attributes**：按钮的无障碍标签、输入框占位符（React 常用 aria-label 存文案）

### 4.2 两个队列 + 空闲调度

| 队列 | 来源 | 优先级 |
| --- | --- | --- |
| `priorityQueue` | 新增节点、属性变化、弹窗内容 | 先处理 |
| `pendingQueue` | 首次全量扫描 | 后处理 |

`requestIdleCallback` 每片只处理 2–10ms，处理不完就继续排队；
窗口被后台化时 `requestIdleCallback` 会被节流，因此有 `setTimeout(250ms)` 兜底。

这就是设置页有上千个文本节点、打开却不卡的原因——翻译被摊到多个空闲片里。

### 4.3 跳过规则（SKIP）

```js
const SKIP_TAGS = { SCRIPT:1, STYLE:1, CODE:1, PRE:1, NOSCRIPT:1, KBD:1, SAMP:1, VAR:1 };
const SKIP_SELECTOR = [
  '[data-testid="thinking-collapsible"]',     // 思考链正文
  '[data-testid="planner-response-text"]',    // 模型回复正文
  '[data-testid="artifact-view"]',            // 工件预览
  ...
];
```

另外会跳过类名含 `code-line`、`select-contain`、`monaco`、`hljs`、`shiki`、
`diff` 等代码/预览区域。

例外：思考链容器里的「已思考 12 秒」「已工作 1 分」触发药丸是系统 UI，
通过 `TRIGGER_SELECTOR` 放行翻译。

### 4.4 Shadow DOM

遇到元素带 `shadowRoot` 时递归入队，保证 Web Component 内部也能翻译。

### 4.5 幂等性

翻译结果不含英文字母 → `characterData` 回调里 `/[A-Za-z]/` 判断不成立 →
不会再次入队。这条规则避免了「翻译 → 观察到变化 → 再翻译」的死循环。

---

## 5. 热重载词典

安装时 `install.py` 会把词典复制到：

```
~/.antigravity-zh/zh-CN.json
```

引擎启动时读取它并**覆盖**内嵌词典；同时 `fs.watch` 监听文件：

```js
fs.watch(extPath, { persistent: false }, () => setTimeout(loadExternalDict, 200));
```

修改并保存后：

1. 200ms 防抖后重新解析
2. `rebuildDict()` 重建三张 Map 并清空翻译缓存
3. 把 `document.body` 重新入队 → 界面逐片重翻

所以**补词条不需要重装、不需要重启客户端**。适合快速试译。

> 注意：热重载只影响「词典」，不影响 `engine.js` 里的动态规则——
> 改规则仍需重新运行安装器。

---

## 6. 调试方法

### 6.1 启动调试端口

```powershell
Stop-Process -Name Antigravity -Force
& "$env:LOCALAPPDATA\Programs\Antigravity\Antigravity.exe" --remote-debugging-port=9222
```

### 6.2 找到隔离上下文

翻译引擎运行在 `preload` 的隔离世界（`Electron Isolated Context`），
普通页面 `console` 里访问不到 `window.__AG_ZH__`。通过 CDP：

```js
// Runtime.evaluate，contextId = Electron Isolated Context
window.__AG_ZH__.translate('2 projects')   // → '2 个项目'
window.__AG_ZH__.translate('Projects')     // → '项目'
```

引擎在隔离世界暴露了调试入口，可用它验证单条翻译：

```js
window.__AG_ZH__.version      // 'v4'
window.__AG_ZH__.dictSize     // 6297
window.__AG_ZH__.translate('2 projects')   // → '2 个项目'
window.__AG_ZH__.pending()    // 队列里还剩多少节点没翻译
```

### 6.3 定位漏翻文本

在页面上下文里遍历文本节点，把仍含英文字母的节点与词典比对：

```js
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
// 收集 t，过滤 t.toLowerCase() 已存在于词典的项
```

对设置页这类大面板，建议按标签页分别抓取再对比，避免一次返回上千条。

---

## 7. 加词条 / 加规则的实操

### 加一条固定文案

1. 打开 `dicts/zh_cn.json`
2. 插入 `"原文": "译文"`（保持文件按 key 小写排序，减少 diff 噪音）
3. 运行 `install-windows.bat`，或直接改 `~/.antigravity-zh/zh-CN.json` 热重载预览

### 加一条动态文案

在 `dicts/engine.js` 的 `dynamicRules` 数组里加一行，**必须整串锚定**（`^...$`）：

```js
[/^(\d+) tasks? (?:are )?running$/i, '正在运行 $1 个任务'],
```

捕获到名称时用 `translateCaptured(name)` 再查词。

### 加一条「这类区域不要翻译」

在 `SKIP_SELECTOR` 里加 `[data-testid="..."]`，或在 `shouldSkipNode()` 里加类名判断。

### 改完怎么验证

```bash
# 1. 校验词典 JSON 语法
python -c "import json;json.load(open('dicts/zh_cn.json',encoding='utf-8'))"

# 2. 重新注入（会自动重建引擎块并刷新外部词典）
install-windows.bat

# 3. 确认已注入
python install.py --status
```

---

## 8. 已知限制

| 限制 | 原因 | 现状 |
| --- | --- | --- |
| 模型回复正文保持英文 | 自由文本无法整句对齐 | 设计如此 |
| 第三方插件营销长文保留英文 | 逐词硬翻质量差 | 设计如此 |
| 新版本新增文案可能漏翻 | 词典滞后于客户端 | 提 Issue / 补词条 |
| 极少数 React 重渲染可能短暂回英文 | 组件重挂载优先于观察回调 | 下一个空闲片会重翻 |
| 动态规则改动需重装 | 规则在引擎里而非外部词典 | 有意为之（避免误伤） |

---

## 9. 安全说明

- 注入代码是**只读**的：只读取 DOM 文本并回写文本，不修改业务逻辑、不发网络请求
- 不包含、不分发 Antigravity 的任何二进制内容（发布包里只有本项目的源码与词典）
- 首次安装自动备份 `app.asar.bak`，`--restore` 可完全还原官方状态
- 修改 `app.asar` 可能违反官方服务条款，风险自负

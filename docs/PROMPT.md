# 项目复现提示词（Prompt）

把下面整段内容交给任意一个具备文件读写、命令行执行能力的 AI 编程智能体，
它就能从零复现这个项目。建议按「阶段」让它分批交付，每阶段单独验证。

---

## 精简版（一句话启动）

> 帮我做一个 Google Antigravity 桌面客户端的中文汉化插件：不要改业务代码，用纯 Python
> 解包 `app.asar`，往 `dist/preload.js` 等入口注入一层 DOM 翻译引擎（词典 + 动态规则），
> 再打成「解压双击即装」的插件包，并且要能在客户端自动更新、备份被清掉之后仍然一键还原。

---

## 完整版（可直接复制）

### 0. 角色与目标

你是一名熟悉 Electron 打包格式（asar）、DOM 注入与桌面端分发的工程师。

目标：为 **Google Antigravity 桌面客户端（Electron，Agent Manager）** 做一套中文汉化方案，
满足三条硬性要求：

1. **不改业务代码**——只往 Electron 的关键入口追加只读的翻译运行时，不拦截网络、不改状态。
2. **零依赖安装**——安装器只用 Python 标准库，不需要 Node / npm / asar CLI。
3. **用户只做三步**——下载 zip、解压、双击。客户端自动更新后同样只需双击一次即可恢复汉化。
4. **随时可还原**——即使客户端更新把安装目录里的备份清空，也必须有第二条还原路径。

### 1. 环境与路径

客户端安装位置（自动探测，按顺序）：

- Windows：`%LOCALAPPDATA%\Programs\Antigravity\resources\app.asar`
- macOS：`/Applications/Antigravity.app/Contents/Resources/app.asar`
- Linux：`/opt/Antigravity/resources/app.asar`、`~/.local/share/Antigravity/resources/app.asar`

基线版本：Antigravity 2.31.x。`app.asar` 内需要关注的入口：

| 文件 | 运行环境 | 职责 |
| --- | --- | --- |
| `dist/preload.js` | 渲染进程 | 主界面全部 DOM 文本 |
| `dist/ideInstall/wizardPreload.js` | 渲染进程 | 首次启动向导 |
| `dist/menu.js` | 主进程 | 原生菜单栏 |
| `dist/tray.js` | 主进程 | 托盘菜单 |
| `dist/main.js` | 主进程 | 原生对话框（退出确认等） |
| `dist/loadingOverlay.js` | 主进程 | 启动加载画面 |

### 2. 阶段一：纯 Python 实现 asar 读写（`asar.py`）

asar 结构：

```
[4 字节 little-endian: pickle 长度]
[pickle: {"files": {...目录结构...}}]
[4 字节 little-endian: payload 长度]
[文件内容按结构表里的 offset 拼接]
```

要求：

- `extract(path, dest)`：还原出完整目录树，并把 `*.unpacked` 目录内容合并回对应位置。
- `pack(src_dir, out_path, unpack_glob)`：重新生成 asar，命中的 glob（本项目的
  `**/node_modules/chrome-devtools-mcp/**`）保持为 `app.asar.unpacked`，**不能塞进 asar**。
- 校验头部：首字段是 pickle payload 长度而非版本号，要做合理性检查。
- 目标是与官方 `@electron/asar` 产物交叉验证一致（文件数、解包后内容一致即可）。

### 3. 阶段二：安装器（`install.py`）

流程：

```
检查客户端是否在运行 → 解包到临时目录 → 判断是否已注入 → 备份官方原版
→ 注入引擎/菜单/托盘/弹窗/加载画面 → 重新打包 → 同目录暂存 + os.replace 原子替换
→ （macOS）ad-hoc 重签名 → 复制词典到 ~/.antigravity-zh/zh-CN.json
```

关键设计（照做）：

- **标记常量**：`TAG = "Antigravity Chinese Translation Injection v3-full"`，每段注入代码都带上，
  用于识别与清理。
- **幂等重建**：注入采用「锚点定位 + 从锚点到文件尾整体重建」。锚点取引擎块开头
  （例如 `  const combinedDict = Object.assign({}, coreWords, dictionary);`），
  这样重复安装不会产生第二个引擎块（旧块在前会导致新词典永不生效），旧格式也能一并清除。
- **原子替换**：先在同目录写 `app.asar.agzh_new`，再 `os.replace`；`app.asar.unpacked`
  同步 rename/回滚，避免中断产生损坏文件。
- **进程占用检查**：Windows 用 `tasklist /FI "IMAGENAME eq Antigravity.exe"`，
  macOS 只匹配 `Antigravity.app/Contents/MacOS` 路径，避免误报。
- **客户端版本**：从解包出的 `package.json` 读 `version`，写进备份元数据。

### 4. 阶段三：翻译引擎（`dicts/engine.js`）—— 本项目最核心的部分

引擎是注入到 `preload.js` 的一个 IIFE，暴露 `window.__AG_ZH__`（含 `translate` / `dictSize` / `pending`）。

#### 4.1 词典索引

安装时把 `dicts/zh_cn.json` 内嵌进引擎（`__DICT_ITEMS__` 占位符替换），启动后再读取
`~/.antigravity-zh/zh-CN.json` 覆盖。构建四份结构：

```
exactLookup      : 原文 → 译文（区分大小写，O(1)）
lowerLookup      : 小写 → 译文（忽略大小写，先到先得）
tokenLookup      : 单个单词 → 译文（仅供短句逐词兜底）
translationCache : 600 字符以内结果缓存（上限 8000 条）
```

为什么必须区分大小写优先：React 常把 `2 projects` 拆成 `2` + ` projects`。
`Projects`（侧边栏标题）= 项目，`projects`（计数单位）= 个项目，两条件必须共存。

#### 4.2 十二级流水线（顺序不可调换，命中即返回）

1. 纯标点节点 → 转全角（快捷键上下文除外）
2. 不含英文字母 → 原样返回（保证幂等）
3. 纯快捷键组合（修饰键 + 单键）→ 原样返回
4. 结果缓存（≤600 字符，LRU 8000 条）
5. 动态日志块：`Worked for 1h2m` / `Edited x +3 -1` / `N files changed` / `Explored N files`
6. **精确匹配** `exactLookup`
7. **忽略大小写** `lowerLookup`
8. 去掉尾部标点再匹配，命中后按原标点补全角
9. 时长短语预处理：`6 days, 23 hours` → `6 天 23 小时`
10. **动态正则规则**（整串锚定，约 189 条）
11. 安全护栏：>3 个单词未命中 / 已含中文 → 保持英文
12. 短文本逐词兜底：仅当每个 ≥2 字母的单词都在词典中，才整句逐词替换

设计意图：先词典后规则 → 已校对文案不被正则劫持；先精确后忽略大小写 → 同词不同义共存；
第 11 级保证「宁可不翻也不输出中英夹杂」（绝不能出现「已失败 to 运行」）。

#### 4.3 拆分句合并

React 会把一句话拆成多个文本节点，逐节点翻译会得到「否 自动化 yet」这种残句。规则：

- 父节点没有元素子节点、且文本节点 ≥ 2；
- 父节点 `textContent` 按空白归一后，若整句命中词典；
- 把译文写入第一个文本节点，其余置空（保留节点结构，不影响 React 协调）。

#### 4.4 动态块与规则

- `fmtDuration`：`1d2h3m4.5s` → `1 天 2 小时 3 分 4.5 秒`（相邻单位补空格）。
- `dynamicRules` 是 `[正则, 译文模板或回调]` 数组，**必须整串锚定**（`^...$`），例如
  `[/^Turn (\d+) of (\d+)$/i, '第 $1 轮（共 $2 轮）']`。
- `translateCaptured(name)`：对正则捕获到的名称二次查词，避免
  「「New Conversation」的快捷键」这类半句英文。

#### 4.5 DOM 层

- `MutationObserver` 监听 `childList` / `characterData` / `attributes`，
  属性白名单：`placeholder`、`title`、`aria-label`、`value`。
- 两个队列：新增节点/属性变化进**优先队列**，首次全量扫描进**普通队列**。
- `requestIdleCallback` 每片处理 2–10ms；后台化被节流时用 `setTimeout(250ms)` 兜底。
- 递归遍历 `shadowRoot`。
- 幂等：译文不含英文字母，`characterData` 回调判断不成立，天然不会二次入队。

#### 4.6 不翻译什么

| 跳过 | 原因 |
| --- | --- |
| `SCRIPT/STYLE/CODE/PRE/KBD/SAMP/VAR` | 代码、快捷键保持原样 |
| `[data-testid="thinking-collapsible"]`、`planner-response-text`、`artifact-view` | 模型自由文本，逐词机翻会乱码 |
| 类名含 `monaco`/`hljs`/`shiki`/`code-line`/`diff` | 代码与预览区 |
| 长句未整句命中 | 宁保留英文 |
| 第三方插件/技能营销长文 | 硬翻质量差 |

例外：思考链容器里的「已思考 X 秒」「已工作 X 分」触发药丸是系统 UI，需放行。

### 5. 阶段四：原生层汉化

- `menu.js` / `tray.js`：构建菜单时用「英文 → 中文」映射替换 `label`（含 `Workspace` → 工作区）。
- `tray.js` 注意新版改成了多行字符串拼接，用正则兜底。
- `main.js`：退出确认等原生对话框。
- `loadingOverlay.js`：v2.31 版只有 Logo 没有文字，直接在其 HTML 里插入
  `<div>正在加载 Antigravity</div>`。

### 6. 阶段五：词典（`dicts/zh_cn.json`）

- 结构就是最简单的 `{"英文原文": "中文译文"}`，本项目约 6297 条。
- 含变量的文案**不写进词典**，改用 `dynamicRules`。
- 同词不同义用大小写区分（`Projects` / `projects`）。
- 合并社区词典时必须过滤：URL、占位符与原文不匹配、超长条目、空 key。
- 统一术语：工件 Artifact、工作树 Worktree、沙箱 Sandbox、审查 Review、分叉 Fork、
  智能体 Agent、子智能体 Subagent、配额 quota、额度 credits、自定义 Customizations。

### 7. 阶段六：备份与还原（双保险，务必实现）

| 位置 | 作用 |
| --- | --- |
| `<resources>/app.asar.bak` | 就地还原 |
| `~/.antigravity-zh/backup/app.asar.orig` + `meta.json` | 持久备份（客户端版本、大小、SHA256、时间） |

- 安装时若当前 asar 是官方原版，两处都写；若已是汉化版则不覆盖官方备份。
- 还原顺序：`.bak` → 用户目录备份。
- **候选备份要先校验未被注入**（asar 内容不压缩，直接字节搜索 TAG 即可，速度很快），
  避免把补丁当原版还原回去。
- 两处都没有时：如果当前 asar 本来就是官方原版，输出「无需还原」并正常退出，
  而不是报错——这是旧版最容易被用户投诉的点（客户端更新会清空 `resources/`）。

### 8. 阶段七：插件包（`build_release.py`）

产物：`dist/Antigravity-zh-plugin-<ver>.zip`（约 11 MB）+ `.sha256`。

```
Antigravity汉化插件-v<ver>/
├── 安装汉化插件.bat      ← 双击这个
├── 还原官方原版.bat
├── 使用说明.txt
├── install.py / asar.py
├── dicts/  docs/  README.md  LICENSE  VERSION
├── install-macos.sh / restore-macos.sh
└── runtime/              ← Windows 版 Python embeddable（用户机器无需装 Python）
```

要求：

- `.bat` 全部转 CRLF，`.sh` 转 LF，`.sh` 置 755。
- 包内文件名可以中文，但 **GitHub Release 的资产名只能是 ASCII**（中文会被替换成 `.`），
  所以 zip 用 `Antigravity-zh-plugin-<ver>.zip`，包内文件夹保留中文名。
- 启动脚本优先用包内 `runtime\python.exe`，找不到再回退 `python` / `py -3`。
- 构建时校验词典 JSON、输出文件数与 SHA256。

### 9. 阶段八：文档与发布

- `README.md`：快速开始必须是「下载 → 解压 → 双击」三步，不要以命令行开篇。
- `docs/HOW_IT_WORKS.md`：注入点、流水线、DOM 调度、跳过规则、热重载、调试、加词条实操。
- 发布到 GitHub：public 仓库 + Release 附 zip 与 `.sha256`，Release 说明里写清安装/还原步骤。

### 10. 必须提前知道的坑（照做，别重犯）

1. `.bat` **必须 CRLF**，否则 cmd 会把多行连成一条命令，出现 `'ERR]' 不是内部或外部命令`。
2. `timeout /t N` 在 stdin 被重定向时直接报错，改用 `ping -n N 127.0.0.1 >nul`。
3. `start "" "app.exe"` 要加 `>nul 2>&1`，否则会占住调用方管道导致卡住。
4. 批处理里 `chcp 65001` 之外，还要给 Python 设 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`，
   否则重定向日志是乱码。
5. 客户端自动更新会整体替换 `resources/`，`.bak` 会消失 → 必须做用户目录持久备份。
6. GitHub Release 资产名不支持中文 → 用 ASCII 文件名。
7. 注入后 asar 体积会从约 5.27 MB 涨到约 6.5 MB（词典内嵌），这是正常的。
8. 旧引擎块不清干净会导致「新词典永不生效」——必须从锚点到文件尾整体重建。
9. 不要用 PyInstaller 赌 Python 版本兼容性，内置 official embeddable runtime 更稳。
10. 用户机器上的 git 代理可能失效（例如指向已关闭的端口），
    `git clone` 报 `Failed to connect to github.com:443 over proxy ...` 时，
    先清掉全局代理配置或改成实际在监听的端口。

### 11. 验收标准（逐条自测）

- [ ] `python install.py --status` 输出「汉化：已注入」，且两处备份都存在。
- [ ] 主界面、设置（各标签页）、项目设置、命令面板、插件市场、自动化页、加载画面、
      原生菜单、托盘菜单均无英文残留。
- [ ] `Ctrl+Shift+P`、`/goal`、模型名（如 `Claude Sonnet 4.6 (Thinking)`）保持原样。
- [ ] 模型回复正文、代码块、diff 保持英文。
- [ ] `2 projects` → `2 个项目`，侧边栏 `Projects` → `项目`（两条件共存）。
- [ ] 删除 `resources/app.asar.bak` 后，双击还原仍成功（走用户目录备份）。
- [ ] 当前已是官方原版时执行还原，提示「无需还原」且退出码为 0。
- [ ] 解压插件包 → 双击 `安装汉化插件.bat`，退出码 0，客户端自动启动且界面为中文。
- [ ] 从 Release 下载的 zip 的 SHA256 与本地构建一致。

### 12. 输出要求

- 按阶段交付，每阶段给出可独立运行的验证方法（命令 + 期望输出）。
- 代码保持纯标准库、单文件可读、注释用中文，路径与常量集中在文件头部。
- 词典与规则分离：固定文案进 JSON，含变量的进 `dynamicRules`。
- 最后附一段「已知限制」：模型正文保持英文、新版本新增文案可能漏翻、
  动态规则改动需重装、修改 `app.asar` 可能违反服务条款。

# 🀄 Antigravity 汉化插件

为 **Google Antigravity** 桌面客户端（Agent Manager）注入中文界面的**汉化插件包**。

解压后双击一次即可安装：不用 git、不用命令行、不用自己装 Python。
官方客户端自动更新后，**再双击一次**就能恢复汉化。

> ⚠️ 非官方语言包。本工具会修改本地 `app.asar`，安装前自动备份为 `app.asar.bak`，
> 可随时用「还原官方原版」恢复。与 Google 及 Antigravity 官方团队无关。

本仓库基于 [zhonghugo/antigravity-zh](https://github.com/zhonghugo/antigravity-zh)
继续维护（MIT 协议），主要新增：Antigravity 2.31 适配、拆分句合并、
插件式一键安装包、还原备份双保险。

| 项目 | 说明 |
| --- | --- |
| 当前版本 | **v1.4.1** |
| 已验证客户端 | Antigravity **2.31.2**（Windows / macOS 通用逻辑） |
| 词典规模 | **6297 条**整句词条 + **189 条**动态正则规则 |
| 插件包大小 | 约 **11 MB**（Windows 版内置 Python 运行时，开箱即用） |
| 许可证 | [MIT](LICENSE) |

---

## 目录

- [快速开始](#-快速开始)
- [软件更新后怎么快速恢复汉化](#-软件更新后怎么快速恢复汉化)
- [翻译是怎么做的](#-翻译是怎么做的)
- [词典维护与贡献](#-词典维护与贡献)
- [项目结构](#-项目结构)
- [打包发布](#-打包发布)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

## 🚀 快速开始

### 第一步：下载插件包

打开 [Releases](https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin/releases/latest)，
下载 **`Antigravity-zh-plugin-v1.4.1.zip`**（约 11 MB），解压到任意位置
（解压出来的文件夹叫「Antigravity汉化插件-v1.4.1」）。

> 插件包已内置 Python 运行时，**不需要 git、不需要命令行、不需要自己装 Python**。

### 第二步：双击安装

1. 完全退出 Antigravity（含托盘图标；脚本也会自动关闭）
2. 双击 **`安装汉化插件.bat`**
3. 脚本自动完成：关闭客户端 → 注入汉化 → 重新启动
4. 界面变成中文即安装成功

还原英文原版：双击 **`还原官方原版.bat`**。

macOS / Linux 解压后执行 `./install-macos.sh` / `./restore-macos.sh`（需系统自带 python3）。

> **建议把这个 zip 留在硬盘上**——客户端每次自动更新后，双击一次即可恢复汉化。

### 给开发者：从源码运行

```bash
git clone https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin.git
cd antigravity-zh-plugin

python install.py                 # 安装汉化（自动探测安装路径）
python install.py --status        # 查看状态：是否已注入、两处备份是否在
python install.py --restore       # 还原官方原版
python install.py --asar "/path/to/resources/app.asar"   # 手动指定路径
```

> 安装前必须**完全退出** Antigravity，否则脚本会拒绝执行（Windows 下可用
> `Stop-Process -Name Antigravity -Force`）。

---

## 🔄 软件更新后怎么快速恢复汉化

Antigravity 每次自动更新都会用官方 `app.asar` 覆盖补丁——这是正常现象，不是装坏了。

**最快的恢复方式（15 秒）：**

1. 打开上次解压出来的插件包目录（或重新下载最新插件包）
2. 双击 `安装汉化插件.bat`
   - 如果客户端正在运行，脚本会先强制关闭
   - 注入完成后自动重新启动客户端
3. 完成。备份和词典都还在，不需要重新下载任何东西

**备份是双保险的：**

| 位置 | 作用 |
| --- | --- |
| `Antigravity\resources\app.asar.bak` | 安装时自动生成，方便就地还原 |
| `%USERPROFILE%\.antigravity-zh\backup\app.asar.orig` | 用户目录持久备份，**客户端更新清空 resources 也不会丢** |

所以即使官方更新把 `.bak` 删了，双击 `还原官方原版.bat` 依然能还原，
绝不会出现「找不到备份」而卡住的情况。

**如果词典也过期了（新版客户端出现新的英文）：**

重新下载最新插件包 → 双击安装即可（词典随包更新）。

**零成本增量更新（不重装）：**

安装时词典会被复制一份到 `~/.antigravity-zh/zh-CN.json`，翻译引擎在启动时读取它，
并用 `fs.watch` 监听文件变化。修改这个文件后**无需重新打包、无需重启**，界面会自动重翻。
所以日常补词条只要编辑这个文件即可。

---

## 🧩 翻译是怎么做的

整体思路：**不改动客户端业务代码，只往 Electron 的关键入口注入一层"翻译运行时"**，
让它在渲染进程里监听 DOM、在原生进程里替换菜单文案。

### 1. 注入点

`install.py` 解包 `app.asar` 后，只往这几个文件追加注入代码：

| 文件 | 作用 | 翻译对象 |
| --- | --- | --- |
| `dist/preload.js` | 渲染进程翻译引擎（主界面） | 全部 DOM 文本、`placeholder`、`title`、`aria-label` |
| `dist/ideInstall/wizardPreload.js` | 安装向导进程 | 首次启动向导界面 |
| `dist/menu.js` | 主进程原生菜单 | 文件 / 编辑 / 视图 / 窗口 / 工作区 等 |
| `dist/tray.js` | 系统托盘菜单 | 托盘右键菜单 |
| `dist/main.js` | 主进程原生弹窗 | 退出确认等原生对话框 |
| `dist/loadingOverlay.js` | 启动加载画面 | 在 Logo 下插入「正在加载 Antigravity」 |

打包时 `chrome-devtools-mcp` 保持 unpacked（官方自带模块，本补丁不碰），
注入采用**锚点定位 + 整体重建**：重复安装不会产生重复引擎块，旧版本引擎会被清理。

### 2. 渲染进程的翻译流水线

引擎在 `preload` 的隔离世界中运行，核心是一个纯函数 `translate(text)`，
**按固定顺序**逐级尝试，命中即返回：

| 顺序 | 阶段 | 说明 | 例子 |
| --- | --- | --- | --- |
| 1 | 纯标点节点 | 英文标点转全角，但快捷键上下文例外 | `?` → `？` |
| 2 | 无英文字母 | 中文 / 数字 / 符号直接跳过（保证幂等，不会反复翻译） | `已完成` 原样返回 |
| 3 | 纯快捷键组合 | 只由修饰键 + 单键组成时保留原样 | `Ctrl+Shift+P` 原样返回 |
| 4 | 结果缓存 | 600 字符以内走 LRU（上限 8000 条），设置页大量重复文案 | — |
| 5 | 动态块 | `Worked for 1h2m`、`Edited x +3 -1`、`N files changed`、`Explored N files` 等日志状态 | → `已工作 1 小时 2 分` |
| 6 | **精确匹配（区分大小写）** | `exactLookup` Map，O(1) | `Projects` → `项目` |
| 7 | **大小写不敏感匹配** | `lowerLookup` 兜底 | `projects` → `个项目` |
| 8 | 去尾部标点再匹配 | 保留原标点并转全角 | `Loading...` → `正在加载…` |
| 9 | 时长短语预处理 | `6 days, 23 hours` → `6 天 23 小时` | — |
| 10 | **动态正则规则** | 189 条整串锚定规则，处理计数、日期、配额、快捷键等 | `Turn 1 of 3` → `第 1 轮（共 3 轮）` |
| 11 | 安全护栏 | 超过 3 个单词的句子、或已含中文的文本，**保持英文不硬翻** | 模型生成的正文永不逐词机翻 |
| 12 | 短文本逐词兜底 | 仅当**每个** ≥2 字母的单词都在词典中才整句逐词替换 | `Sign in required` → `需要登录` |

**为什么要区分大小写优先？**
React 常把 `2 projects` 拆成 `2` + ` projects` 两个文本节点。
`Projects`（侧边栏标题）应译为「项目」，而小写 `projects`（计数单位）应译为「个项目」。
先精确、再忽略大小写，两个词条可以共存。

### 3. 拆分句合并（v1.4 新增）

React 会把一句话拆成多个文本节点，逐节点翻译就会得到
`否 自动化 yet` 这种残句。引擎现在会检查父节点：

- 父节点没有元素子节点（纯文本）且文本节点 ≥ 2 个
- 把父节点文本按空白归一后，若**整句**命中词典
- 就把译文写入第一个文本节点、其余置空（保留节点结构，不影响 React 协调）

于是 `No automations yet` → `暂无自动化任务`。

### 4. DOM 层：监听与调度

- `MutationObserver` 监听 `childList / characterData / attributes`
  （属性白名单：`placeholder`、`title`、`aria-label`、`value`）
- 新节点进**优先队列**（设置弹窗、菜单、对话流优先），历史节点进普通队列
- 用 `requestIdleCallback` 分片处理（每片 2–10ms），后台化时有 `setTimeout` 兜底
- 支持 Shadow DOM（递归遍历 `shadowRoot`）
- 翻译写回后是中文，不含英文字母，天然不会触发二次翻译（幂等）

### 5. 不翻译什么（避免中英混排）

| 跳过范围 | 原因 |
| --- | --- |
| `SCRIPT / STYLE / CODE / PRE / KBD / SAMP / VAR` | 代码与快捷键应该保持原样 |
| `thinking-collapsible`、`planner-response-text`、`artifact-view` 容器内正文 | 模型生成的自由文本，逐词机翻会变成乱码；但「已思考 X 秒」这类系统药丸放行 |
| 代码 / 预览 / diff 相关类名 | `monaco`、`hljs`、`shiki`、`code-line` 等 |
| 长句未整句命中 | 宁可保留英文，也不输出「已失败 to 运行」式中英夹杂 |
| 第三方插件/技能的营销长文 | 逐词硬翻质量差，保留原文更易读 |

### 6. 词典格式

`dicts/zh_cn.json` 就是最简单的键值对：

```json
{
  "New Conversation": "新建对话",
  "Projects": "项目",
  "projects": "个项目",
  "Sign in required": "需要登录"
}
```

- **键** = 界面上的英文原文（整句，含原有标点可省略）
- **值** = 中文译文
- 同一英文在不同语境有不同译法时，用大小写区分（`Projects` / `projects`）
- 含变量的文案**不要**写进词典，改用 `dicts/engine.js` 里的动态规则

### 7. 动态规则

计数、日期、剩余时间、快捷键标签这类会变的文案，用整串锚定的正则：

```js
[/^Turn (\d+) of (\d+)$/i, '第 $1 轮（共 $2 轮）'],
[/^See\s+(\d+)\s+more$/i, '查看另外 $1 项'],
[/^Toggle\s+(.+)$/i, function (m, name) { return '切换 ' + translateCaptured(name); }],
```

`translateCaptured()` 会把捕获到的名字（如快捷键动作名 `New Conversation`）
再查一次词典，输出「「新建对话」的快捷键：Ctrl+Shift+O」而不是半句英文。

规则在词典精确匹配**之后**执行，所以不会劫持已校对过的固定词条。

### 8. 原生层翻译

`menu.js` / `tray.js` 用「英文 → 中文」映射表在构建菜单时替换 `label`；
`loadingOverlay.js` 在 v2.31 新版（只有 Logo、没有文字）的 HTML 里插入一行
`<div>正在加载 Antigravity</div>`。这些都在主进程执行，与渲染引擎互不影响。

---

## 📝 词典维护与贡献

1. 在客户端里看到未翻译的英文，先确认它是不是**整句**（React 可能拆分节点）
2. 在 `dicts/zh_cn.json` 补一条 `"英文原文": "中文译文"`
3. 重装一次（`安装汉化插件.bat`，源码目录下为 `install-windows.bat`）让词典进入 asar；或直接编辑
   `~/.antigravity-zh/zh-CN.json` 热重载预览效果
4. 涉及数字/日期/计数的文案，改为在 `dicts/engine.js` 的 `dynamicRules` 里加规则
5. 提交 PR 时请附上「界面位置 + 原文 + 译文」，便于校对

术语约定（保持全项目一致）：

| 英文 | 译名 |
| --- | --- |
| Artifact | 工件 |
| Worktree | 工作树 |
| Sandbox | 沙箱 |
| Review | 审查 |
| Fork | 分叉 |
| Agent | 智能体 |
| Subagent | 子智能体 |
| Quota / Credits | 配额 / 额度 |
| Customizations | 自定义（扩展） |

---

## 📁 项目结构

```
antigravity-zh-plugin/
├── install.py                # 安装器：注入 / 还原 / 状态
├── asar.py                   # 纯 Python asar 解包与打包
├── build_release.py          # 生成插件包（zip + sha256）
├── VERSION                   # 版本号
├── install-windows.bat       # 源码版一键安装（包里改名为「安装汉化插件.bat」）
├── restore-windows.bat       # 源码版一键还原（包里改名为「还原官方原版.bat」）
├── install-macos.sh          # macOS / Linux 一键安装
├── restore-macos.sh          # macOS / Linux 一键还原
├── runtime/                  # Windows 免安装 Python 运行时（不进 Git，打包时下载）
├── dicts/
│   ├── zh_cn.json            # 6297 条整句词典
│   └── engine.js             # DOM 翻译引擎模板（含动态规则）
├── docs/
│   ├── HOW_IT_WORKS.md       # 翻译机制详解（进阶阅读）
│   └── PROMPT.md             # 项目复现提示词（交给 AI 从零重做）
├── SKILL.md                  # 供 AI 智能体调用的技能说明
├── README.md
└── LICENSE                   # MIT
```

---

## 📦 打包发布

```bash
python build_release.py           # 生成 dist/Antigravity-zh-plugin-v1.4.1.zip（内置 Python）
python build_release.py --slim    # 不内置运行时（约 250 KB，需系统已装 Python）
```

插件包结构（解压即用）：

```
Antigravity汉化插件-v1.4.1/
├── 安装汉化插件.bat      ← 双击这个
├── 还原官方原版.bat
├── 使用说明.txt
├── install.py / asar.py
├── dicts/  docs/
└── runtime/              ← 免安装 Python，用户机器无需任何环境
```

脚本同时输出 zip 的 SHA256 与 `.sha256` 校验文件。

首次构建前若需要内置运行时，把 Windows 版
[Python embeddable](https://www.python.org/downloads/windows/)（`python-3.12.x-embed-amd64.zip`）
解压到仓库根目录的 `runtime/` 即可（该目录已在 `.gitignore` 中）。

---

## ❓ 常见问题

**Q：汉化后界面没变化？**
A：确认是**完全退出**（含托盘）后重新启动；可用 `python install.py --status` 检查「汉化：已注入」。

**Q：官方更新后汉化消失了？**
A：正常。双击 `安装汉化插件.bat` 重新注入即可，备份和词典都还在。

**Q：双击「还原官方原版.bat」提示找不到备份？**
A：旧版才有这个问题——客户端更新会清空 `resources\` 目录，把 `.bak` 一起删掉。
v1.4.1 起官方原版会另存一份到 `%USERPROFILE%\.antigravity-zh\backup\`，
即使 `resources\app.asar.bak` 没了也能还原。若当前本来就是官方原版，脚本会直接提示「无需还原」。

**Q：提示「应用已损坏，无法打开」（macOS）？**
A：`sudo xattr -rd com.apple.quarantine /Applications/Antigravity.app`；
安装器已自动做 ad-hoc 重签名。

**Q：部分界面仍是英文？**
A：新版客户端可能新增词条。欢迎补 `dicts/zh_cn.json` 并提 PR，或在 Issues 反馈原文。

**Q：会不会影响客户端功能 / 被风控？**
A：只改字符串与注入只读翻译层，不触碰网络请求与业务逻辑；但修改 `app.asar`
可能违反官方服务条款，请自行评估。

**Q：如何彻底恢复？**
A：双击 `还原官方原版.bat`（或 `python install.py --restore`）。

---

## 📜 更新日志

### v1.4.1（2026-11-12）

* **插件化打包**：发布物改为 `Antigravity-zh-plugin-v1.4.1.zip`（GitHub 资产名只支持 ASCII，包内文件夹与脚本仍为中文名），内置 Python 运行时，
  解压后双击 `安装汉化插件.bat` 即可，**无需 git、无需命令行、无需自装 Python**
* **还原双保险**：安装时除 `resources\app.asar.bak` 外，再另存一份官方原版到
  `%USERPROFILE%\.antigravity-zh\backup\`（含客户端版本、SHA256、时间）。
  客户端更新清空 `resources\` 后依然能还原
* **修复**：`.bak` 被更新清掉时，「还原」会直接报错退出——现在会先回退到用户目录备份；
  若当前已是官方原版，则明确提示「无需还原」而不是报失败
* **修复**：批处理调用 Python 时强制 UTF-8 输出，控制台不再出现乱码
* `--status` 显示两处备份的状态与客户端版本
* 已验证客户端 **2.31.2**

### v1.4.0（2026-11-11）

* **适配 Antigravity 2.31.0**：官方自动更新覆盖补丁后完整复验主界面、设置、项目设置、
  命令面板、插件市场、自动化页
* 词典：5982 → **6297 条**（新增 v2.31 界面词条、插件市场与内置技能说明）
* 引擎：**精确匹配优先于忽略大小写匹配**（`exactLookup` + `lowerLookup`），
  修复 `Projects` / `projects`（计数）无法共存、`Models` 被旧译名遮蔽的问题
* 引擎：**拆分句合并**——父节点整句命中词典时统一改写，修复 `否 自动化 yet` 类残句
* 引擎：快捷键判定收紧为「纯组合」正则，`Ctrl+Shift+O for New Conversation`
  这类多修饰键标签恢复翻译；新增 `translateCaptured()` 对捕获名二次查词
* 引擎：新增 v2.31 动态规则（问候语、`Version X`、`Turn N of M`、`N projects`、
  `See N more`、`Toggle X`）
* 插件市场：`安装 X` / `添加 X` / `X 详情` / `X 的更多操作` / `精选插件` 等
  aria-label 全部汉化；`Sign in required` → 需要登录；`Context7` 不再被误译为「上下文7」
* 内置技能说明补全：`/swarm`、`/swarm_monitor`、`/migrate-agent-settings`、
  `/run-workflow`；第三方工具免责声明译为中文
* 加载画面：v2.31 纯 Logo 版式下插入「正在加载 Antigravity」
* 原生菜单：`Workspace` → 工作区
* 新增一键安装/还原脚本（Windows / macOS）与 `build_release.py` 发布打包
* 新增 `docs/HOW_IT_WORKS.md` 翻译机制详解

### v1.3.1（2026-10-21）

* 思考链正文保持英文：`thinking-collapsible` / `planner-response-text` / `artifact-view`
  容器与 `.cursor-edit` 编辑预览整块跳过翻译——模型生成的自由文本不逐词硬翻，
  无法整句翻译时保持英文原样，避免中英夹杂；「已思考 X 秒」触发药丸是系统 UI，放行汉化
* 修复：`fmtDuration` 相邻单位间缺空格（`1 小时2 分` → `1 小时 2 分`），
  `Worked for` / `Thought for` 动态块改走 `fmtDuration`，支持 `1d2h3m4.5s` 混合单位
* 修复：`Permanently delete ...` 尾部 ASCII 句点未转全角（`永久删除 Old Tasks.` → `永久删除 Old Tasks。`）

### v1.3.0（2026-10-13）

* 词典：1855 → 5982 条。系统性对比 7 个社区汉化项目（Antigravity-Chinese-Localization、
  Antigravity-Hans、Antigravity-zh-CN、antigravity-chinese、antigravity-chinese-locale、
  antigravity-chinese-Zero-Touch、AntigravityCN），合并其词典精华并统一术语
  （工件/审查/沙箱/分叉/自定义扩展/额度/智能体），过滤 URL、占位符不匹配、
  超长条目与污染 key
* 引擎新增动态正则规则层（dynamicRules）：约 100 条整串锚定规则，覆盖 N 前/重置倒计时、
  配额提示、日期时间（Jan 5 - Mar 10、10:30 AM）、永久删除确认、快捷键提示、
  分屏/终端/模型选择等动态文案；在词典精确匹配之后执行，不劫持已校对词条
* 引擎新增 `fmtDuration`：`Worked for 1h2m` → `已工作 1 小时 2 分`（紧凑时长自动补空格）
* 引擎短句翻译门槛改为"全部单词已知"（词均在词典中才输出翻译），消除
  "Failed to run" → "已失败 to 运行"式中英夹杂
* 吸收 Zero-Touch 项目补充规则：`5m ago` 紧凑时间、`showing X of Y`、`Fold lines`、
  `Run command: X`、`Load older messages` 等；`Close (Esc)` 等缺失词条
* 吸收 AntigravityCN 项目补充规则：`Thinking (X)`、`N searches`、`N% remaining`、
  纯数量短语（`45 minutes` / `3 days`）等；补齐 Hourly/Daily Limit 剩余额度等缺失词条
* 修复：统一「子代理」→「子智能体」（保留网络代理 Proxy 语义的 15 条不受影响）
* 修复（重要）：install.py 旧格式引擎升级时会产生**重复引擎块**——旧引擎在前先翻译，
  新词典永不生效。现改为从第一个引擎起点到文件尾整体重建，历史重复块一并清除

### v1.2.0（2026-10-06）

* 词典：1583 → 1831 条。基于实际 UI 代码（main bundle）提取漏翻词条，补齐插件市场、
  反馈问卷、加载/状态提示、查找替换栏、附件标签、调度频率等场景
* 修复：统一核心术语——Artifact 工件、Worktree 工作树、Sandbox 沙箱、Review 审查、
  Fork 分叉、订阅 plan 套餐，并区分 quota（配额）与 credits（额度）
* 修复：清除约 20 条冗余英文括注（如"默认 (Default)"），主题名 Catppuccin/Dracula 保留原名
* 修复：引擎内置词典与 `zh_cn.json` 多处同键不同值（内置优先导致词典修改不生效），已全部对齐
* 修复：coreWords 移除 `for→持续`、`worked→工作了`、`thought→思考了`、`explored→浏览了`、
  `js→Js` 等易把正常语句拼成乱码的词条（对应的动态状态正则已覆盖）
* 修复：`Worked for 2m 30s` / `Thought for 1h` 类时长状态支持分钟/小时并转换单位（此前仅支持秒）
* 词典：1831 → 1855 条。补齐设置页技能/插件的描述翻译（Gemini API、
  Antigravity SDK、Sepia、agy-customizations 等本机已装项），以及
  Plugins/Plugin/Automations/Preview 栏目标题与"Plugin: xxx"徽章
* 修复：设置页技能/插件英文描述被逐词替换成中英夹杂（如"multi-回合聊天"、
  "their 正在加载 priority"）。引擎新增覆盖率门槛——长句命中不足 65%、
  短句不足 80% 时保持原文不再硬翻；连字符复合词（agy-customizations、
  text-to-video 等）不再被拆词误翻
* 修复：词典更新后重装不生效——重装时按 TAG 判断"已注入"直接跳过，导致新旧词典
  同标签时永不更新。现改为整体重建追加的引擎块（顺带刷新内置词典 / coreWords / 动态规则），
  内容无变化时才跳过
* 修复：`• Asks for Review` 词条错贴为另一条描述的译文

### v1.1.1（2026-09-07）

* 修复：macOS 重签名目标路径错误（多算一层目录导致签名到 /Applications 而非 .app，签名始终失败）
* 修复：`app.asar` 替换改为同目录暂存 + `os.replace` 原子替换，失败自动回滚 unpacked，避免中断产生损坏文件
* 修复：asar 文件头校验语义（首字段是 pickle payload 长度而非版本号），增加 pickle_size 合理性检查
* 修复：`check_app_running` 误报（`pgrep -f Antigravity` 会匹配命令行含该词的任意进程，如打开本仓库的编辑器）
* 优化：翻译引擎预排序词典缓存，避免每次翻译重复 `Object.keys/filter/sort`
* 词典：`Operation not permitted` 去除冗余英文括注

### v1.1.0（2026-09-06）

- 修复：命令权限弹窗标题/警告行未翻译（补 8 条词条）
- 修复：动态拼接选项（如 `Yes, and always allow '<cmd>' in this conversation`）部分翻译
- 修复：长文本子串匹配仅支持 >3 词，放宽到 >=4 字符
- 修复：从零注入时 `extraDict` 未合并到 `dictionary` 导致全英文
- 修复：分词正则 `/s+/` 缺少反斜杠导致词数计算错误
- 词典：1566 → 1583 条

### v1.0.0（2026-09-05）

- 首次发布：零依赖纯 Python 安装器
- 纯 Python asar 解包/打包（与官方 @electron/asar 交叉验证一致）
- 1566 条中英词典 + DOM 翻译引擎
- 原生菜单 / 托盘菜单翻译
- 一键安装 / 还原 / 状态检测

---

## ⚖️ 免责声明

本项目与 Google 及 Antigravity 官方团队无关，不包含 Antigravity 任何二进制内容。
修改 `app.asar` 可能违反官方服务条款，请自行评估使用风险。

## 📄 License

[MIT](LICENSE)

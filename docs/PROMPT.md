# 项目复现提示词（Prompt）

把下面整段内容交给任意一个具备文件读写、命令行执行能力的 AI 编程智能体，它就能从零复现这个项目。
建议按「阶段」让它分批交付，每阶段单独验证。本版本对应插件 **v1.5.0**，重点是把「装完客户端打不开」从架构上消灭。

---

## 精简版（一句话启动）

> 帮我做一个 Google Antigravity 桌面客户端的中文汉化插件：不要改业务代码，用纯 Python 解包 `app.asar`，
> 只往 `dist/preload.js` 等入口**末尾追加**带标记、整体 `try/catch` 的翻译补丁（渲染进程 DOM 引擎 +
> 主进程菜单 / 托盘 / 弹窗运行时包装）；安装后**真启动一次客户端做冒烟测试**，失败自动回滚官方原版；
> 再打成「解压双击即装」的插件包，客户端自动更新后双击一次或登录时自动修复；还原时必须校验客户端版本。

---

## 完整版（可直接复制）

### 0. 角色与目标

你是一名熟悉 Electron 打包格式（asar）、DOM 注入、Windows 批处理与桌面端分发的工程师。

目标：为 **Google Antigravity 桌面客户端（Electron，Agent Manager）** 做一套中文汉化方案，满足六条硬性要求：

1. **不改业务代码**——只往 Electron 的关键入口追加只读的翻译运行时，不拦截网络、不改状态。
2. **零依赖安装**——安装器只用 Python 标准库，不需要 Node / npm / asar CLI。
3. **用户只做三步**——下载 zip、解压、双击。客户端自动更新后同样只需双击一次即可恢复汉化。
4. **随时可还原**——即使客户端更新把安装目录里的备份清空，也必须有第二条还原路径；且还原前必须校验版本。
5. **绝不能把客户端装坏**——只追加 + `try/catch` 失败隔离 + 安装后冒烟测试 + 失败自动回滚。
6. **更新后自愈**——提供智能模式（需要才重新注入）、登录自动修复（HKCU 注册表 Run 项）和桌面快捷方式。

### 1. 环境与路径

客户端安装位置（自动探测，按顺序）：

- Windows：`%LOCALAPPDATA%\Programs\Antigravity\resources\app.asar`，其次 `%ProgramFiles%\Antigravity\resources\app.asar`
- macOS：`/Applications/Antigravity.app/Contents/Resources/app.asar`
- Linux：`/opt/Antigravity/resources/app.asar`、`~/.local/share/Antigravity/resources/app.asar`

基线版本：Antigravity **2.32.1**。`app.asar` 内需要关注的入口：

| 文件 | 运行环境 | 职责 |
| --- | --- | --- |
| `dist/preload.js` | 渲染进程 | 主界面全部 DOM 文本 |
| `dist/ideInstall/wizardPreload.js` | 渲染进程 | 首次启动向导 |
| `dist/menu.js` | 主进程 | 原生菜单栏、托盘菜单 |
| `dist/tray.js` | 主进程 | 托盘菜单（v1.5.0 不直接改，由菜单包装覆盖） |
| `dist/main.js` | 主进程 | 原生对话框（退出确认、文件选择、错误框） |
| `dist/loadingOverlay.js` | 主进程 | 启动加载画面 |

### 2. 阶段一：纯 Python 实现 asar 读写（`asar.py`）

asar 结构：

```text
[4 字节 uint32 = 4（size pickle 的 payload 长度）]
[4 字节 uint32 = header pickle 总长 = 8 + align4(json_size)]
[4 字节 uint32 = 4 + align4(json_size)]
[4 字节 int32  = json_size]
[json_size 字节 JSON 结构表，补齐到 4 字节对齐]
[文件内容按结构表里的 offset 拼接]
```

要求：

- `extract(path, dest)`：还原完整目录树，并把 `*.unpacked` 目录内容合并回对应位置。
- `pack(src_dir, out_path, unpack_glob)`：重新生成 asar，命中的 glob（本项目的
  `**/node_modules/chrome-devtools-mcp/**`）保持为 `app.asar.unpacked`，**不能塞进 asar**。
- 为每个文件写 `integrity`（整文件 SHA256 + 每 4 MB 分块 SHA256），与官方 `@electron/asar` 一致。
- 校验头部：首字段是 pickle payload 长度（恒为 4）而非版本号，要做合理性检查。
- 额外提供 `list_files()` / `read_file()` / `read_json()` / `file_count()`，供安装器做**替换前结构校验**与版本读取。
- 目标是与官方 `@electron/asar` 产物交叉验证一致（文件数、解包后内容一致即可）。

### 3. 阶段二：安装器（`install.py`）主流程

流程：

```text
探测路径 → 读词典/算哈希 → 客户端在运行就关闭
→ 解包到临时目录 → 检查 dist/preload.js 存在 → 读版本 / 判断是否已注入
→ 备份官方原版（两处）→ 只追加补丁块 → 重新打包 → 替换前结构校验
→ 同目录暂存 + os.replace 原子替换（保留替换前副本）
→ 复制外部词典 → 冒烟测试（Windows 默认）
→ 成功：删除保留副本、写 state.json、启动客户端
→ 失败：回滚替换前副本、启动官方版、退出码 3
```

关键设计（照做）：

- **标记块 + 只追加**：每个补丁块写成
  `// ===== AG_ZH_BEGIN:<name> =====` … `// ===== AG_ZH_END:<name> =====`，整体包在 `try/catch` 里，
  只在文件末尾追加，**不对 `menu.js` / `tray.js` / `main.js` 做就地字符串替换**。
- **失败隔离**：补丁初始化异常只 `console.error`，绝不向上抛；`menu.js` / `main.js` 注入失败只打印跳过，不终止安装。
- **重装清理**：`apply_blocks()` 先按标记清理旧块（新格式的 `AG_ZH_BEGIN:` 前缀、历史 TAG 注释、旧菜单块起点、
  旧引擎起点 `const dictionary = {`），再从锚点截断到文件尾、重新追加，保证引擎 / 菜单块永远只有最新一份。
- **冒烟测试**：替换后清空 `ELECTRON_RUN_AS_NODE` 等变量启动客户端；先记录
  `%APPDATA%\Antigravity\logs\main.log` 的字节偏移，60 秒内轮询「新增日志出现 `Starting app (v`」且进程稳定存活；
  失败 → 杀进程 → 用替换前保留的 `app.asar` + `app.asar.unpacked` 回滚 → 启动官方原版 → 退出码 3。
- **原子替换可回退**：先把当前 `app.asar` 复制为 `app.asar.agzh_keep.asar`、unpacked 改名为 `.agzh_old`，
  新 asar 写同目录暂存文件后 `os.replace`；成功才删除保留副本。
- **替换前结构校验**：`verify_new_asar()` 检查头部可读、文件数与源目录一致、`package.json` 的 `main` 入口存在、
  每个被注入文件确实含对应 BEGIN 标记；失败退出码 2，且**未改动客户端文件**。
- **进程占用检查**：Windows 用 `tasklist /FI "IMAGENAME eq Antigravity.exe"`，macOS 只匹配
  `Antigravity.app/Contents/MacOS` 路径，避免误报；关不掉时以退出码 1 结束。
- **客户端版本**：从解包出的 `package.json` 读 `version`，写进备份元数据与 `state.json`。
- **外部词典**：安装成功后把 `dicts/zh_cn.json` 复制到 `%USERPROFILE%\.antigravity-zh\zh-CN.json` 供热重载。

退出码约定（重要，验收会看）：

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功；还原时表示无需还原 |
| `1` | 前置条件 / 参数错误（找不到 asar、客户端无法关闭、解包失败等） |
| `2` | 注入或结构校验失败，安装中止（未改动客户端文件） |
| `3` | 冒烟测试失败，已自动回滚 |
| `4` | 还原被拒（没有可用备份，或备份版本与当前客户端不一致） |

### 4. 阶段三：翻译引擎（`dicts/engine.js`）—— 本项目最核心的部分

引擎是注入到 `preload.js` 的 IIFE，暴露 `window.__AG_ZH__`（含 `translate` / `version` / `dictSize` / `pending`）。

#### 4.1 词典索引

安装时把 `dicts/zh_cn.json` 内嵌进引擎（`__DICT_ITEMS__` 占位符替换），启动后再读取
`%USERPROFILE%\.antigravity-zh\zh-CN.json` 覆盖。构建四份结构：

```text
exactLookup      : 原文 → 译文（区分大小写，O(1)）
lowerLookup      : 小写 → 译文（忽略大小写，先到先得）
tokenLookup      : 单个单词 → 译文（仅供短句逐词兜底）
translationCache : 600 字符以内结果缓存（上限 8000 条）
```

为什么必须区分大小写优先：React 常把 `2 projects` 拆成 `2` + ` projects`。
`Projects`（侧边栏标题）= 项目，`projects`（计数单位）= 个项目，两条必须共存。

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
10. **动态正则规则**（整串锚定，约 200 条）
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
  `[/^Turn (\d+) of (\d+)$/i, "第 $1 轮（共 $2 轮）"]`。
- `translateCaptured(name)`：对正则捕获到的名称二次查词，避免「「New Conversation」的快捷键」这类半句英文。

#### 4.5 DOM 层

- `MutationObserver` 监听 `childList` / `characterData` / `attributes`，
  属性白名单：`placeholder`、`title`、`aria-label`、`value`。
- 两个队列：新增节点 / 属性变化进**优先队列**，首次全量扫描进**普通队列**。
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
| 第三方插件 / 技能营销长文 | 硬翻质量差 |

例外：思考链容器里的「已思考 X 秒」「已工作 X 分」触发药丸是系统 UI，需放行（`TRIGGER_SELECTOR`）。

### 5. 阶段四：原生层汉化——v1.5.0 的运行时包装

> 重要：**不要**再就地替换 `menu.js` / `tray.js` / `main.js` 里的字符串。官方一改结构，替换就失效，
> 更糟的是可能改坏主进程代码导致客户端打不开。v1.5.0 改为「末尾追加运行时包装」。

- **`menu.js`**：追加一个 IIFE，`require("electron")` 拿到 `Menu`，包装 `Menu.setApplicationMenu` 与
  `Menu.buildFromTemplate`，递归翻译菜单项的 `label`；没有 `label` 时按 `role` 补中文。
  维护 `MENU_LABELS` 与 `MENU_ROLES` 两张表，动态文案用正则（`N active agents`、`Open X`）兜底。
- **托盘（`tray.js`）**：托盘菜单由 `Menu.buildFromTemplate(actions)` 构建，已被上面的包装覆盖，
  **不需要也不应该**单独改 `tray.js`；托盘标签进 `MENU_LABELS` 即可。
- **`main.js`**：追加两个块——`menu`（同样的菜单包装，兜底主进程其他位置的菜单）和
  `dialog`（包装 `showMessageBox` / `showMessageBoxSync` / `showOpenDialog(Sync)` /
  `showSaveDialog(Sync)` / `showErrorBox`，翻译 `title` / `message` / `detail` / `buttons` 等字段）。
  兼容 `(options)` 与 `(browserWindow, options)` 两种调用签名。
- **`loadingOverlay.js`**（唯一例外）：它是 HTML 模板字符串里的一行文案，只能在模板里替换 / 插入。
  优先替换 `<div class="text">Loading Antigravity</div>`；新版只有 Logo 时在 `</svg>` 后插入中文行 +
  `<!-- AG_ZH_LOADING -->` 标记。插入文本**禁止包含** `$`、`` ` ``、`\`，锚点缺失就跳过。

所有包装器都要：整体 `try/catch`、用 `Menu.__AG_ZH_MENU__` / `dialog.__AG_ZH_DIALOG__` 标记防重复包装。

### 6. 阶段五：词典（`dicts/zh_cn.json`）

- 结构就是最简单的 `{"英文原文": "中文译文"}`，v1.5.0 目标 6500+ 条。
- 含变量的文案**不写进词典**，改用 `dynamicRules`。
- 同词不同义用大小写区分（`Projects` / `projects`）。
- 合并社区词典时必须过滤：URL、占位符与原文不匹配、超长条目、空 key、隐私信息（邮箱 / 用户名 / 本机路径）。
- 统一术语：工件 Artifact、工作树 Worktree、沙箱 Sandbox、审查 Review、分叉 Fork、
  智能体 Agent、子智能体 Subagent、配额 quota、额度 credits、自定义 Customizations。

### 7. 阶段六：备份、还原与版本校验（双保险，务必实现）

| 位置 | 作用 |
| --- | --- |
| `<resources>/app.asar.bak` | 就地还原 |
| `%USERPROFILE%\.antigravity-zh\backup\app.asar.orig` + `meta.json` | 持久备份（客户端版本、大小、SHA256、时间） |

- 安装时若当前 asar 是官方原版，两处都写；若已是汉化版则不覆盖官方备份。
- 候选备份要先校验未被注入（asar 不压缩，直接字节搜索 TAG / `AG_ZH_BEGIN:` 即可），避免把补丁当原版还原回去。
- **还原前必须做版本校验**：读取当前 asar 与每个备份 asar 内 `package.json` 的 `version`，
  只接受与当前客户端版本一致的备份；不一致时拒绝并提示先重装 / 修复或以 `--force` 强制（退出码 4）。
  旧版 asar 装到新客户端上会打不开——这是「还原把应用弄坏」的根因。
- 当前已是官方原版时：输出「无需还原」并退出码 0，而不是报错。
- 还原流程：关闭客户端 → 同目录暂存 + `os.replace` 原子替换 → 删除 `state.json` → 不修改 `.unpacked`。

### 8. 阶段七：快速重新汉化（更新后自愈）

`%USERPROFILE%\.antigravity-zh\state.json`：

```json
{
  "app_version": "2.32.1",
  "dict_sha256": "…",
  "injected_sha256": "…",
  "injected_at": "2026-11-14 10:30:00",
  "toolkit_version": "1.5.0"
}
```

- `--auto`：客户端在运行 → 直接聚焦 / 启动；否则若「已注入 + `dict_sha256` 一致 + `app_version` 一致」→
  直接启动（<1 秒），否则重新注入后启动。
- `--auto-silent`：同样判断，但只注入不启动（内部跳过冒烟测试），供登录自动修复使用。
- `--install-task` / `--remove-task`：写 / 删 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 下的
  `REG_SZ` 值 `AntigravityZhAutoRepair`，数据为
  `"<插件目录>\runtime\pythonw.exe" "<插件目录>\install.py" --auto-silent`
  （优先 pythonw，无黑框；没有内置运行时则退回当前解释器）。
  不写「启动」文件夹、不建计划任务（前者会被安全软件拦截），不需要管理员权限；
  `--remove-task` 同时清理旧方案残留（启动文件夹里的 `.bat`、旧的同名计划任务）。
  安装成功后若检测到已注册，会自动刷新数据为当前插件目录；值里记录插件目录绝对路径，移动目录后需重新注册。
- `--create-shortcut`：在桌面创建「Antigravity 汉化版」快捷方式，目标指向 `汉化并启动.bat`，图标取客户端 exe。
- `--launch`：注入完成后启动客户端；`--no-smoke`：跳过冒烟测试（不推荐）。

### 9. 阶段八：插件包（`build_release.py`）

产物：`dist/Antigravity-zh-plugin-v1.5.0.zip`（约 11 MB）+ `.sha256`。

```text
Antigravity汉化插件-v1.5.0/
├── 安装汉化插件.bat          ← 双击这个（完整安装 + 冒烟 + 启动）
├── 还原官方原版.bat          → install.py --restore
├── 汉化并启动.bat            → install.py --auto
├── 创建桌面快捷方式.bat       → 创建「Antigravity 汉化版」快捷方式，指向 汉化并启动.bat
├── 注册开机自动修复.bat       → install.py --install-task
├── 取消开机自动修复.bat       → install.py --remove-task
├── 使用说明.txt
├── install.py / asar.py
├── dicts/  docs/  README.md  LICENSE  VERSION
├── install-macos.sh / launch-macos.sh / restore-macos.sh
└── runtime/                  ← Windows 版 Python embeddable（用户机器无需装 Python）
```

要求：

- `.bat` 全部转 CRLF，`.sh` 转 LF，`.sh` 置 755。
- 包内文件名可以中文，但 **GitHub Release 的资产名只能是 ASCII**（中文会被替换成 `.`），
  所以 zip 用 `Antigravity-zh-plugin-<ver>.zip`，包内文件夹保留中文名。
- 启动脚本优先用包内 `runtime\python.exe`，找不到再回退 `python` / `py -3`。
- 构建时校验词典 JSON、输出文件数与 SHA256。
- 发布前把文档里的词典条数占位符替换成真实数字。

### 10. 阶段九：文档与发布

- `README.md`：快速开始必须是「下载 → 解压 → 双击」三步，不要以命令行开篇；
  必须有「更新后怎么办」「命令与参数」「工作原理」「故障排查」「FAQ」「术语表」「更新日志」。
- `docs/HOW_IT_WORKS.md`：注入点、只追加与失败隔离、冒烟测试与回滚、`state.json` 快速判定、
  流水线、DOM 调度、热重载、调试、加词条实操、已知限制。
- `SKILL.md`：供 AI 智能体调用的技能说明，含参数表、退出码、验收流程。
- 发布到 GitHub：public 仓库 + Release 附 zip 与 `.sha256`，说明里写清安装 / 还原 / 更新后恢复步骤。

### 11. 必须提前知道的坑（照做，别重犯）

1. `.bat` **必须 CRLF**，否则 cmd 会把多行连成一条命令，出现 `'ERR]' 不是内部或外部命令`。
2. `timeout /t N` 在 stdin 被重定向时直接报错，改用 `ping -n N 127.0.0.1 >nul`。
3. `start "" "app.exe"` 要加 `>nul 2>&1`，否则会占住调用方管道导致卡住。
4. 批处理里 `chcp 65001` 之外，还要给 Python 设 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`，否则重定向日志是乱码。
5. 客户端自动更新会整体替换 `resources/`，`.bak` 会消失 → 必须做用户目录持久备份。
6. GitHub Release 资产名不支持中文 → 用 ASCII 文件名。
7. 注入后 asar 体积会从约 5.7 MB 涨到约 6.9 MB（词典内嵌），这是正常的。
8. 旧引擎块不清干净会导致「新词典永不生效」——必须从锚点到文件尾整体重建。
9. 不要用 PyInstaller 赌 Python 版本兼容性，内置 official embeddable runtime 更稳。
10. 用户机器上的 git 代理可能失效（例如指向已关闭的端口），`git clone` 报
    `Failed to connect to github.com:443 over proxy ...` 时，先清掉全局代理配置或改成实际在监听的端口。
11. **不要就地替换 `menu.js` / `tray.js` / `main.js` 的源码字符串**：官方结构一变，轻则翻译失效，
    重则主进程语法错误 → 客户端打不开。只追加带标记、整体 `try/catch` 的运行时包装。
12. **冒烟测试要清环境变量**：`ELECTRON_RUN_AS_NODE`、`NODE_USE_ENV_PROXY`、`ELECTRON_NO_ATTACH_CONSOLE`，
    否则客户端会被当 Node 启动。
13. **冒烟测试要按字节偏移读日志**：先记录 `main.log` 大小，只认新增内容里的 `Starting app (v`，
    否则历史日志会让旧记录误判成功；看到启动日志后还要再观察几秒确认进程稳定存活。
14. **回滚必须用替换前保留的副本**，并且同时恢复 `app.asar` 与 `app.asar.unpacked`；
    不要依赖用户目录备份（可能没有或版本不匹配）。
15. **结构校验必须在替换前做**：文件数、`package.json` 的 `main` 入口、每个注入文件的 BEGIN 标记；
    校验失败时客户端文件必须原封不动（退出码 2）。
16. **还原必须版本匹配**：旧 asar 装到新客户端会打不开；没有匹配备份时拒绝并以退出码 4 结束，`--force` 才放行。
17. `loadingOverlay.js` 的插入文本不能含 `$`、`` ` ``、`\`，否则模板字符串会插值 / 转义出错。
18. 开机自动修复**不要**写「启动」文件夹里的 `.bat`（会被安全软件拦截，实测 Permission denied），也**不要**建计划任务；
    写 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 的 `REG_SZ` 值最稳，无需管理员权限。
    数据必须写成 `"<pythonw>" "<install.py>" --auto-silent`（两个路径都加引号），优先 `runtime\pythonw.exe` 避免黑框。
19. `--auto` 快速路径要同时比对**词典哈希**和**客户端版本**，只比其中一个会在更新后误判「已是最新」。
20. 判断 asar 是否已注入：asar 不压缩，直接按字节搜索 TAG / 标记即可，不需要解包，速度快。

### 12. 验收标准（逐条自测）

**v1.5.0 安全验收（必做）**：

- [ ] 2.32.1 官方原版 → 双击 `安装汉化插件.bat` → 客户端自动打开、界面中文、命令行无报错、退出码 0。
- [ ] 模拟客户端更新（用官方 `app.asar` 覆盖已汉化文件）→ 双击 `汉化并启动.bat` → 自动重新注入并打开中文界面。
- [ ] **破坏性测试**：注入一个必定让主进程崩溃的补丁 → 冒烟测试捕获 → 自动回滚为官方原版 → 客户端能正常打开，退出码 3。
- [ ] `--restore` 且备份版本匹配 → 还原成功；备份版本不匹配 → 拒绝并提示，退出码 4。
- [ ] 插件 zip 解压 → 双击 `安装汉化插件.bat` → 成功，退出码 0。
- [ ] 词典无隐私信息（邮箱 / 用户名 / 本机路径）。
- [ ] `--auto` 在已汉化且词典 / 版本未变时 1 秒内直接打开客户端。
- [ ] `--install-task` 后注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 下存在 `AntigravityZhAutoRepair`（`--status` 显示已注册）；`--remove-task` 能删除。

**汉化质量验收**：

- [ ] `--status` 输出「汉化: 已注入」，两处备份都存在且版本与客户端一致，状态文件有记录。
- [ ] 主界面、设置（各标签页）、项目设置、命令面板、插件市场、自动化页、加载画面、原生菜单、托盘菜单均无英文残留。
- [ ] `Ctrl+Shift+P`、`/goal`、模型名（如 `Claude Sonnet 4.6 (Thinking)`）保持原样。
- [ ] 模型回复正文、代码块、diff 保持英文。
- [ ] `2 projects` → `2 个项目`，侧边栏 `Projects` → `项目`（两条件共存）。
- [ ] 删除 `resources\app.asar.bak` 后，还原仍成功（走用户目录备份）。
- [ ] 当前已是官方原版时执行还原，提示「无需还原」且退出码 0。

### 13. 输出要求

- 按阶段交付，每阶段给出可独立运行的验证方法（命令 + 期望输出）。
- 代码保持纯标准库、单文件可读、注释用中文，路径与常量集中在文件头部。
- 词典与规则分离：固定文案进 JSON，含变量的进 `dynamicRules`。
- 所有补丁遵守「只追加 + `try/catch` + BEGIN/END 标记」三原则，并在文档中写清回滚路径。
- 最后附一段「已知限制」：模型正文保持英文、新版本新增文案可能漏翻、动态规则改动需重装、
  macOS / Linux 暂无冒烟测试、修改 `app.asar` 可能违反服务条款。


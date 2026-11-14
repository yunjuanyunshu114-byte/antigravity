# 翻译机制详解（HOW IT WORKS）

本文说明 `antigravity-zh` 到底往客户端里放了什么、翻译是怎么一步步发生的、v1.5.0 如何做到「装不坏」、以及怎样安全地加词条和排查问题。

- 只想用插件：看 [README](../README.md) 就够了
- 想改代码 / 加词条 / 排查问题：看这里

---

## 1. 总览：三个部分

```text
┌───────────────────────────────────────────────────────────────┐
│ install.py   安装器：探测路径 → 关闭客户端 → 解包 asar        │
│              → 追加补丁 → 结构校验 → 原子替换 → 冒烟测试      │
│              → 成功收尾 / 失败回滚；另负责备份、还原、开机自动修复 │
├───────────────────────────────────────────────────────────────┤
│ dicts/engine.js   翻译引擎模板：DOM 监听 + 12 级流水线 + 动态规则│
├───────────────────────────────────────────────────────────────┤
│ dicts/zh_cn.json  整句词典："英文原文": "中文译文"             │
└───────────────────────────────────────────────────────────────┘
```

v1.5.0 的第一目标是**绝不把客户端装坏**。所有设计都围绕这一点：

1. 只**追加**补丁，不改官方原有代码；
2. 每个补丁块整体 `try/catch`，补丁自身出错不影响客户端启动；
3. 安装后真启动一次做冒烟测试，失败自动回滚；
4. 还原前校验客户端版本，避免旧 asar 装到新客户端上。

---

## 2. 注入架构：只追加 + 失败隔离

### 2.1 标记块

每个补丁块都带一对标记，便于识别、清理和重建：

```js
// ===== AG_ZH_BEGIN:engine =====
try {
  (function () {
    // ... 补丁代码 ...
  })();
} catch (e) {
  try { console.error("[Antigravity-ZH] 补丁初始化失败", e); } catch (_) {}
}
// ===== AG_ZH_END:engine =====
```

规则：

- **只在文件末尾追加**，不对 `menu.js` / `tray.js` / `main.js` 做就地字符串替换；
- 每个块整体包在 `try/catch` 里，异常只 `console.error`，绝不向上抛出；
- 块名写在标记里；同一个文件可以有多个块（例如 `main.js` 同时有 `menu` 和 `dialog`）；
- 安装器集中处理追加与清理，见 `install.py` 的 `apply_blocks()`。

### 2.2 注入点

| 目标文件 | 运行环境 | 补丁块 | 翻译对象 | 实现方式 |
| --- | --- | --- | --- | --- |
| `dist/preload.js` | 渲染进程（主窗口） | `engine` | 主界面全部 DOM 文本 | 追加翻译引擎 IIFE（`engine.js` 模板 + 内嵌全量词典） |
| `dist/ideInstall/wizardPreload.js` | 渲染进程（安装向导） | `engine` | 首次启动向导界面 | 同上 |
| `dist/menu.js` | 主进程 | `menu` | 原生菜单栏、托盘菜单 | 运行时包装 `Menu.setApplicationMenu` 与 `Menu.buildFromTemplate`，翻译 `label` / `role` |
| `dist/tray.js` | 主进程 | 无 | 托盘菜单 | **不追加补丁**：托盘菜单由 `Menu.buildFromTemplate` 构建，已被 `menu.js` / `main.js` 的包装覆盖 |
| `dist/main.js` | 主进程 | `menu`、`dialog` | 原生弹窗（退出确认、文件选择、错误框等） | 菜单包装兜底 + 包装 `dialog.showMessageBox` 等接口 |
| `dist/loadingOverlay.js` | 主进程 | 无（特例） | 启动加载画面 | 在 HTML 模板字符串中插入一行中文文案（锚点替换，见 2.3） |

> 文件不存在时只打印「跳过」并继续，不视为安装失败；`dist/preload.js` 是唯一的硬性要求，缺失会直接中止安装（未改动任何文件）。

### 2.3 各补丁块细节

#### 引擎块（`preload.js` / `wizardPreload.js`）

`build_engine_block()` 做三件事：

1. 读取 `dicts/engine.js` 模板；
2. 把 `__DICT_ITEMS__` 占位符替换成 `// ===== <TAG> =====` 注释 + `const extraDict = { ... }` 全量词条；
3. 用 `try { ... } catch (e) { ... }` 包住整个引擎。

其中 `TAG = "Antigravity Chinese Translation Injection v5-appendonly"`，`quick_is_patched()` 会用它（以及其他几个历史标记）快速判断 asar 是否被注入过。引擎在渲染进程的隔离世界里暴露 `window.__AG_ZH__` 调试入口，见第 9 节。

#### 菜单块（`menu.js`、`main.js`）

`MENU_PATCH_JS` 是一个运行时包装器：

- 用 `require("electron")` 拿到 `Menu`；
- 用 `Menu.__AG_ZH_MENU__` 标记防止重复包装；
- 维护两张表：`MENU_LABELS`（按 `label` 精确匹配，约 60 条）和 `MENU_ROLES`（菜单项没有 `label` 时按 `role` 补中文，约 25 条）；
- 动态文案用正则兜底：`/^(\d+) active agents?$/` → `N 个智能体运行中`，`/^Open (.+)$/` → `打开 X`；
- 包装 `Menu.setApplicationMenu`：先递归翻译 `menu.items` 再调用原函数；
- 包装 `Menu.buildFromTemplate`：先递归翻译模板数组再调用原函数。

托盘菜单（`tray.js`）就是用 `Menu.buildFromTemplate` 构建的，所以托盘标签也被同一层包装翻译，**不需要单独改 `tray.js`**。`main.js` 里再追加一份同样的块，是为了覆盖主进程其他位置构建的菜单。

#### 弹窗块（`main.js`）

`DIALOG_PATCH_JS` 包装 Electron 的 `dialog` 接口：

- `showMessageBox` / `showMessageBoxSync`（退出确认等）；
- `showOpenDialog` / `showOpenDialogSync`、`showSaveDialog` / `showSaveDialogSync`（按钮文案）；
- `showErrorBox`（两个字符串参数，单独处理）。

翻译的字段：`title`、`message`、`detail`、`checkboxLabel`、`buttonLabel`、`buttons` 数组。Electron 的这些接口既可能 `(options)` 也可能 `(browserWindow, options)` 调用，补丁用 `argOptions()` 兼容两种签名。

#### 加载画面（`loadingOverlay.js`，特例）

这里是整个版本里**唯一**不是「末尾追加标记块」的地方：它是 HTML 模板字符串里的一行可见文案。

- 优先替换已有的 `<div class="text">Loading Antigravity</div>`；
- 新版加载画面只有 Logo 时，在 `</svg>` 之后插入一行中文 + `<!-- AG_ZH_LOADING -->` 标记；
- 插入文案**禁止包含** `$`、`` ` ``、`\` 三个字符（模板字符串插值 / 转义风险），命中则跳过；
- 锚点都找不到就跳过，不报错、不影响安装；
- 已含 `AG_ZH_LOADING` 标记时直接跳过，保证幂等。

### 2.4 重装与旧版清理

`apply_blocks(path, blocks, engine=False)` 的执行顺序：

1. 删除 v1.4.1 及更早版本对 `menu.js` 的就地调用：
   `if (typeof translateMenu === "function") { menu.items.forEach(translateMenu); }`；
2. 收集清理标记，取**最早出现的位置**，从该位置截断到文件尾（`_truncate_tail()`）：
   - 新格式块前缀 `// ===== AG_ZH_BEGIN:`；
   - 历史版本注释行：`... Injection v3-full =====`、`... v2-extra =====`、`... v4-appendonly =====`；
   - 历史菜单块起点：`const menuTranslationMap = {`；
   - 引擎文件额外加 `(function() {` 换行 `const dictionary = {` 这个旧引擎起点；
3. `rstrip()` 后把新块追加到文件末尾。

效果：**引擎块和菜单块永远只有最新一份**，不会出现「旧引擎在前先翻译、新词典永不生效」的历史问题。

少数早期版本做过就地文案替换（`main.js` 的退出确认文案、`tray.js` 的托盘标签、`loadingOverlay.js` 的加载文案）。这些是纯字符串替换、不产生重复代码，保留也无副作用；`loadingOverlay.js` 检测到 `AG_ZH_LOADING` 后会跳过，不重复插入。

### 2.5 原子替换与回滚副本

`swap_in()` 保证替换过程可回退：

1. 把当前 `app.asar` 复制为 `app.asar.agzh_keep.asar`；
2. 把现有 `app.asar.unpacked` 改名为 `app.asar.unpacked.agzh_old`；
3. 新 asar 先写到同目录暂存文件 `app.asar.agzh_new`，再 `os.replace()` 原子替换；
4. 把新 unpacked 移动到 `app.asar.unpacked`；
5. 替换过程抛异常 → 立即恢复旧的 asar 和 unpacked。

安装成功后 `finalize_swap()` 删除保留副本；冒烟测试失败时 `rollback_swap()` 把 `keep` 副本换回去。

`chrome-devtools-mcp` 仍保持 unpacked（`**/node_modules/chrome-devtools-mcp/**`），不塞进 asar。

---

## 3. 安装主流程

`python install.py`（不带参数）实际执行：

```text
1. detect_paths()         自动探测 app.asar；--asar 可手动指定
2. load_dictionary()      读取词典，计算 dict_sha256
3. kill_app()             客户端在运行就 taskkill /IM Antigravity.exe /F /T，最多等 20 秒
4. asar.extract()         解包到临时目录（含 .unpacked）
5. 结构检查              dist/preload.js 必须存在，否则中止（未改动任何文件）
6. 读取版本 & 判定        package.json 版本；preload 里是否已有注入标记
7. ensure_backup()        官方原版写 resources\app.asar.bak + 用户目录持久备份
8. 注入                   preload / wizard / menu / main / loadingOverlay（见第 2 节）
9. asar.pack()            重新打包到临时目录
10. verify_new_asar()     结构校验：头部可读、文件数一致、package.json 入口存在、
                          每个被注入文件都含对应 BEGIN 标记；失败退出码 2（未改动）
11. swap_in()             原子替换（见 2.5）
12. 复制外部词典          %USERPROFILE%\.antigravity-zh\zh-CN.json
13. smoke_test()          Windows 默认执行；--no-smoke 跳过（见第 4 节）
14. 成功 → finalize + save_state()；需要时启动客户端
```

几个容易忽略的点：

- **不再要求用户手动退出客户端**：安装器会自己关闭，关不掉才报「客户端无法关闭」并以退出码 1 结束。
- 注入 `menu.js` / `main.js` 时的异常只打印「跳过」，不影响安装——它们是锦上添花，`preload` 引擎才是主体。
- 结构校验在替换**之前**完成，所以校验失败时客户端文件完全没被改动。
- 词典同时内嵌进 asar 并复制到用户目录（热重载用）。

退出码：

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功（还原时表示「无需还原」） |
| `1` | 前置条件 / 参数错误（找不到 asar、客户端无法关闭、解包失败等） |
| `2` | 注入或结构校验失败，安装中止（未改动客户端文件） |
| `3` | 冒烟测试失败，已自动回滚 |
| `4` | 还原被拒（没有可用备份，或备份版本与当前客户端不一致） |

### 3.1 批处理脚本与 CLI 对应

插件包里的 `.bat` 只是把常用参数封装起来，行为与直接运行 `install.py` 完全一致：

| 包内脚本 | 实际命令 | 说明 |
| --- | --- | --- |
| `安装汉化插件.bat` | `install.py --launch` | 完整安装（含冒烟测试与启动） |
| `还原官方原版.bat` | `install.py --restore` | 还原官方原版（校验版本） |
| `汉化并启动.bat` | `install.py --auto` | 需要时重新注入并启动，已最新则秒开 |
| `注册开机自动修复.bat` | `install.py --install-task` | 写 HKCU 注册表 Run 项（值名 `AntigravityZhAutoRepair`） |
| `取消开机自动修复.bat` | `install.py --remove-task` | 删除该注册表值并清理旧方案残留 |
| `创建桌面快捷方式.bat` | `install.py --create-shortcut` | 在桌面创建「Antigravity 汉化版」快捷方式，指向 `汉化并启动.bat` |

macOS / Linux 对应脚本：`install-macos.sh`（安装）、`launch-macos.sh`（`--auto`，更新后恢复）、`restore-macos.sh`（`--restore`）。

---

## 4. 冒烟测试与自动回滚

这是 v1.5.0 修复「装完打不开」的核心机制。写在 `install.py` 的 `smoke_test()` 里。

### 4.1 判定流程

```text
1. 记录客户端主进程日志的当前大小：
   Windows: %APPDATA%\Antigravity\logs\main.log
   macOS:   ~/Library/Application Support/Antigravity/logs/main.log
   Linux:   ~/.config/Antigravity/logs/main.log
2. start_app() 启动客户端，最多等 60 秒，每秒轮询：
   - 进程消失 → 失败「客户端进程启动后退出」
   - 新增日志里出现 Starting app (v → 记录已启动，再过约 6 秒确认进程仍存活
   - 已启动且稳定存活 → 成功「客户端已正常启动」
   - 超时仍未看到启动日志 → 失败「等待超时」
```

启动客户端前会清掉几个会干扰 Electron 的环境变量：`ELECTRON_RUN_AS_NODE`、`NODE_USE_ENV_PROXY`、`ELECTRON_NO_ATTACH_CONSOLE`。Windows 下用 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` 脱离安装器进程，标准输入输出接 `DEVNULL`，避免安装窗口被占住。

### 4.2 失败 → 回滚

```text
冒烟失败
  → kill_app(15)：关掉刚启动的客户端
  → rollback_swap()：把 app.asar.agzh_keep.asar 和 .unpacked.agzh_old 换回去
  → start_app()：重新启动官方原版，保证用户还能用
  → （若回滚失败：提示手动双击「还原官方原版.bat」）
  → die(..., 3)：退出码 3，打印失败原因和安装日志路径
```

冒烟**成功**时客户端保持运行（符合「装完就能用」的预期），安装器不会再多启动一次。

### 4.3 开关

- 仅 Windows 默认执行；macOS / Linux 自动跳过（安装器会打印「非 Windows 平台跳过冒烟测试」）。
- `--no-smoke` 跳过测试，此时注入完也不会自动启动客户端（除非再加 `--launch`）。
- `--auto-silent` 内部会强制设置 `no_smoke = True` 且不启动，适合登录自动修复静默检查。

> 跳过冒烟 = 放弃自动回滚保护。只有在你明确知道客户端启动异常与汉化无关时才用。

---

## 5. state.json 与 `--auto` 快速判定

### 5.1 状态文件

每次安装成功写入 `%USERPROFILE%\.antigravity-zh\state.json`：

```json
{
  "app_version": "2.32.1",
  "dict_sha256": "词典按 key 排序后的 SHA256",
  "injected_sha256": "替换后 app.asar 的 SHA256",
  "injected_at": "2026-11-14 10:30:00",
  "toolkit_version": "1.5.0"
}
```

### 5.2 `--auto` 判定顺序

```text
客户端正在运行？
  ├─ 是（普通 --auto）→ 启动/聚焦客户端，返回 0
  └─ 是（--auto-silent）→ 跳过，返回 0
asar 已注入（quick_is_patched）
 且 state.dict_sha256 == 当前词典哈希
 且 state.app_version == 当前 asar 内 version
  ├─ 是 → 「已是最新汉化，直接启动」，通常 1 秒内完成
  └─ 否（或未注入）→ 走完整注入流程，成功后启动（silent 时只注入）
```

所以「客户端自动更新后」和「词典更新后」都会被识别为需要重新注入，而日常启动走快速路径。

### 5.3 开机自动修复（HKCU 注册表 Run 项）

`--install-task` 不写「启动」文件夹、也不建计划任务，而是写当前用户注册表：

```text
键:   HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
值名: AntigravityZhAutoRepair
类型: REG_SZ
数据: "<插件目录>\runtime\pythonw.exe" "<插件目录>\install.py" --auto-silent
```

- 优先用插件包自带的 `runtime\pythonw.exe`（无黑框）；没有内置运行时则退回 `runtime\python.exe`，再退回当前解释器；
- 登录后 Windows 会执行该命令，`--auto-silent` 静默检查：未汉化（客户端更新过）就重新注入，不启动客户端；
- 不需要管理员权限；`--status` 通过读取该注册表值判断「已注册 / 未注册」；
- 安装成功后若检测到已注册，会自动把数据刷新为当前插件目录；
- `--remove-task` 删除该值，并顺带清理旧方案残留（启动文件夹里的 `AntigravityZhAutoRepair.bat`、旧的同名计划任务）；
- 值里记录的是**插件目录的绝对路径**，移动或删除插件文件夹后自动修复会失效，需要重新注册。

---

## 6. 还原与版本校验

`--restore` 的判定顺序（`cmd_restore()`）：

```text
1. 当前 asar 未被注入？
   → 打印「当前就是官方原版，无需还原」，退出码 0，不碰任何文件
2. 收集候选备份：resources\app.asar.bak、用户目录 app.asar.orig
   - 已被注入污染的备份直接忽略
   - 每个候选读取 asar 内 package.json 的 version
3. 找与当前客户端版本一致的备份
   ├─ 找到 → 关闭客户端 → 原子替换 → 删除 state.json → 退出码 0
   └─ 没找到
       ├─ --force → 用第一个候选强制还原（不推荐）
       └─ 否则 → 拒绝并提示，退出码 4
```

为什么必须校验版本：旧版 `app.asar` 里的 preload / main 可能和新客户端的主进程接口不兼容，装回去会打不开。

`quick_is_patched()` 的判断依据是 asar 字节流里是否含以下任意一个标记（asar 不压缩，直接搜很快）：

- `Antigravity Chinese Translation Injection v5-appendonly`（当前 TAG）；
- `AG_ZH_BEGIN:engine`；
- `Antigravity Chinese Translation Injection`（v1.4.x 及更早）；
- `Antigravity-ZH`（补丁日志前缀）。

还原不修改 `app.asar.unpacked`（内容与官方原版一致，注入时也不会写入补丁），也不删除用户目录的外部词典和备份。

---

## 7. 翻译引擎：12 级流水线

引擎是 `dicts/engine.js` 模板，注入后运行在 `preload` 的隔离世界。核心是一个纯函数 `translate(text)`。

### 7.1 初始化：四个结构

安装时词典被内嵌进 `preload.js`（`__DICT_ITEMS__` 占位符替换），启动后还会读取外部词典覆盖：

```text
coreWords（内置少量） + dictionary（内嵌全量） + ~/.antigravity-zh/zh-CN.json（外部覆盖）
                ↓
exactLookup      : 原文 → 译文（区分大小写，O(1)）
lowerLookup      : 小写 → 译文（忽略大小写，先到先得）
tokenLookup      : 单个单词 → 译文（仅短句逐词兜底）
translationCache : 600 字符以内结果缓存（上限 8000 条）
```

> `lowerLookup` 采用先到先得：词典按 key 小写排序，因此同名不同大小写的词条需要在词典里显式声明（见 7.4）。

### 7.2 逐级匹配顺序（命中即返回）

| 顺序 | 阶段 | 说明 | 例子 |
| --- | --- | --- | --- |
| 1 | 纯标点节点 | 英文标点转全角，快捷键上下文例外 | `?` → `？` |
| 2 | 不含英文字母 | 中文 / 数字 / 符号直接跳过（保证幂等） | `已完成` 原样返回 |
| 3 | 纯快捷键组合 | 只由修饰键 + 单键组成时保留原样 | `Ctrl+Shift+P` 原样返回 |
| 4 | 结果缓存 | 600 字符以内走 LRU（上限 8000 条） | 设置页大量重复文案 |
| 5 | 动态块 | `Worked for 1h2m`、`Edited x +3 -1`、`N files changed`、`Explored N files` 等 | → `已工作 1 小时 2 分` |
| 6 | **精确匹配（区分大小写）** | `exactLookup`，O(1) | `Projects` → `项目` |
| 7 | **忽略大小写匹配** | `lowerLookup` 兜底 | `projects` → `个项目` |
| 8 | 去尾部标点再匹配 | 保留原标点并转全角 | `Loading...` → `正在加载…` |
| 9 | 时长短语预处理 | `6 days, 23 hours` → `6 天 23 小时` | — |
| 10 | **动态正则规则** | 约 200 条整串锚定规则，处理计数、日期、配额、快捷键等 | `Turn 1 of 3` → `第 1 轮（共 3 轮）` |
| 11 | 安全护栏 | 超过 3 个单词的句子、或已含中文的文本，**保持英文不硬翻** | 模型正文永不逐词机翻 |
| 12 | 短文本逐词兜底 | 仅当**每个** ≥2 字母的单词都在词典中才整句逐词替换 | `Sign in required` → `需要登录` |

顺序的意义：

- **先词典后规则**：已校对过的固定文案不会被正则改写；
- **先精确后忽略大小写**：允许 `Projects` 与 `projects` 共存；
- **规则放最后**：动态规则只处理词典覆盖不到的、含变量的文案。

### 7.3 动态块（模型日志状态）

这类文本由客户端运行时拼接，格式固定但数值变化，用快速路径处理：

```js
if (/^Worked for [\d smhd.]+$/.test(trimmed)) {
  return "已工作 " + fmtDuration(...);   // Worked for 1h2m → 已工作 1 小时 2 分
}
if (/^Edited .* \+\d+ -\d+$/.test(trimmed)) { ... }   // 编辑了 file (+3 -1)
if (/^\d+ files? changed$/.test(trimmed)) { ... }      // 3 个文件已更改
if (/^Explored/.test(trimmed)) { ... }                  // 浏览了 12 个文件
```

`fmtDuration` 负责紧凑时长的单位替换与补空格：

```text
1d2h3m4.5s  →  1 天 2 小时 3 分 4.5 秒
```

### 7.4 大小写敏感的精确匹配

React 会把界面拆成多个文本节点，例如侧边栏标题 `Projects`，而设置页的计数是 `" projects"`（前面带空格）单独成节点。词典里两条同时存在：

```json
{
  "Projects": "项目",
  "projects": "个项目"
}
```

- `exactLookup.get("Projects")` 命中「项目」；
- `exactLookup.get(" projects")` 未命中 → `lowerLookup.get(" projects")` 命中「个项目」。

如果只保留忽略大小写的单表，两条会互相覆盖（旧版本就出现过后加译名失效）。

### 7.5 尾部标点单独处理

英文句号、问号常被 React 拆成独立文本节点。引擎分两步：

1. 纯标点节点：`?` → `？`（快捷键上下文除外，避免 `Ctrl+,` 变成 `Ctrl+，`）；
2. 整句末尾标点：先剥掉再查词，命中后按原标点补全角：

```text
"Loading..."  →  "正在加载…"
"Delete?"     →  "删除？"
```

### 7.6 拆分句合并（父子句兜底）

React 有时把一句话拆成多个文本节点，逐节点翻译会得到残句。引擎在翻译单个文本节点前会先看父节点：

```js
if (parent.childElementCount === 0 && parent.childNodes.length >= 2) {
  const combined = parent.textContent.replace(/\s+/g, " ").trim();  // No automations yet
  const hit = exactLookup.get(combined) ?? lowerLookup.get(combined.toLowerCase());
  if (hit) {
    // 译文写到第一个文本节点，其余置空（保留节点结构，不影响 React 协调）
  }
}
```

结果：`No automations yet` → `暂无自动化任务`。

### 7.7 安全护栏：宁可不翻，也不给中英夹杂

| 规则 | 目的 |
| --- | --- |
| 整句 > 3 个单词且未命中词典 → 原样返回 | 避免「已失败 to 运行」 |
| 文本已含中文 → 原样返回 | 保证幂等，防止二次翻译 |
| 短句逐词兜底要求**每个** ≥2 字母单词都在词典里 | `Failed to run` 不会变成「已失败 to 运行」 |
| 纯快捷键组合 → 原样返回 | `Ctrl+Shift+P` 保持可读 |
| 代码 / 思考链 / 预览区域 → 整块跳过 | 自由文本不该逐词机翻 |

### 7.8 动态规则与二次查词

`dynamicRules` 是「整串锚定」的正则数组（约 200 条），匹配成功的返回值支持 `$1` 与回调：

```js
[/^Turn (\d+) of (\d+)$/i, "第 $1 轮（共 $2 轮）"],
[/^Version (.+)$/i, "版本 $1"],
[/^See\s+(\d+)\s+more$/i, "查看另外 $1 项"],
[/^Toggle\s+(.+)$/i, function (m, name) { return "切换 " + translateCaptured(name); }],
```

`translateCaptured()` 会对捕获到的名称再做一次词典查询，避免：

```text
❌ 「New Conversation」的快捷键：Ctrl+Shift+O
✅ 「新建对话」的快捷键：Ctrl+Shift+O
```

### 7.9 外部词典热重载

安装时 `install.py` 会把词典复制到 `%USERPROFILE%\.antigravity-zh\zh-CN.json`。引擎启动时读取它并**覆盖**内嵌词典，同时 `fs.watch` 监听文件：

```js
fs.watch(extPath, { persistent: false }, () => setTimeout(loadExternalDict, 200));
```

修改并保存后：

1. 200ms 防抖后重新解析；
2. `rebuildDict()` 重建四张结构并清空翻译缓存；
3. 把 `document.body` 重新入队 → 界面逐片重翻。

所以补词条不需要重装、不需要重启客户端。**但热重载只影响词典**，改 `engine.js` 里的动态规则仍需重新运行安装器。

---

## 8. DOM 层：监听、队列、跳过

### 8.1 监听配置

```js
new MutationObserver(handleMutations).observe(document.documentElement, {
  childList: true,
  subtree: true,
  characterData: true,
  attributes: true,
  attributeFilter: ["placeholder", "title", "aria-label", "value"]
});
```

- `childList` / `characterData`：新出现的文本；
- `attributes`：按钮的无障碍标签、输入框占位符（React 常用 aria-label 存文案）。

### 8.2 两个队列 + 空闲调度

| 队列 | 来源 | 优先级 |
| --- | --- | --- |
| `priorityQueue` | 新增节点、属性变化、弹窗内容 | 先处理 |
| `pendingQueue` | 首次全量扫描 | 后处理 |

`requestIdleCallback` 每片只处理 2–10ms，处理不完继续排队；窗口被后台化时 `requestIdleCallback` 会被节流，因此有 `setTimeout(250ms)` 兜底。这就是设置页上千文本节点也不卡的原因。

### 8.3 跳过规则

```js
const SKIP_TAGS = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, NOSCRIPT: 1, KBD: 1, SAMP: 1, VAR: 1 };
const SKIP_SELECTOR = [
  "[data-testid=\"thinking-collapsible\"]",   // 思考链正文
  "[data-testid=\"planner-response-text\"]",  // 模型回复正文
  "[data-testid=\"artifact-view\"]",          // 工件预览
  // ...
];
const TRIGGER_SELECTOR = [
  "[data-testid=\"thinking-collapsible-trigger\"]",
  "[data-testid=\"worked-for-collapsible\"]",
  "[data-testid=\"tool-group-collapsible\"]",
].join(",");
```

另外会跳过类名含 `code-line`、`select-contain`、`monaco`、`hljs`、`shiki`、`diff` 等代码 / 预览区域。

例外：思考链容器里的「已思考 12 秒」「已工作 1 分」触发药丸是系统 UI，通过 `TRIGGER_SELECTOR` 放行翻译。

### 8.4 Shadow DOM

遇到元素带 `shadowRoot` 时递归入队，保证 Web Component 内部也能翻译。

### 8.5 幂等性

翻译结果不含英文字母 → `characterData` 回调里 `/[A-Za-z]/` 判断不成立 → 不会再次入队。这条规则避免「翻译 → 观察到变化 → 再翻译」的死循环。

---

## 9. 调试

### 9.1 日志位置

| 日志 | 路径 |
| --- | --- |
| 安装日志 | `%USERPROFILE%\.antigravity-zh\logs\install-<时间戳>.log`（每次安装一个） |
| 客户端主进程日志 | `%APPDATA%\Antigravity\logs\main.log`（冒烟测试读的就是它） |

安装失败时 `install.py` 会在最后打印安装日志路径。

### 9.2 查看状态

```bat
cd /d "C:\Users\<你>\Downloads\Antigravity汉化插件-v1.5.0"
runtime\python.exe install.py --status
```

会输出：安装器版本、客户端路径、asar 路径、客户端版本、大小 / SHA256、是否已注入、是否运行中、state.json 摘要、两处备份的版本、词典条数与哈希、开机自动修复（已注册 / 未注册）。

### 9.3 启动 CDP 调试

```bat
taskkill /IM Antigravity.exe /F /T
set ELECTRON_RUN_AS_NODE=
"%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe" --remote-debugging-port=9222
```

> 如果你的环境里设置了 `ELECTRON_RUN_AS_NODE=1`，直接启动会变成 Node 进程并报错，必须先清掉这个变量。

### 9.4 找到隔离上下文

翻译引擎运行在 `preload` 的隔离世界（Electron Isolated Context），普通页面 `console` 里访问不到 `window.__AG_ZH__`。通过 CDP `Runtime.evaluate`，选择 Electron Isolated Context 执行：

```js
window.__AG_ZH__.translate("2 projects")    // → "2 个项目"
window.__AG_ZH__.translate("Projects")      // → "项目"
window.__AG_ZH__.version                    // → "v4"
window.__AG_ZH__.dictSize                   // → 当前词典条数
window.__AG_ZH__.pending()                  // → 队列里还剩多少节点没翻译
```

### 9.5 定位漏翻文本

在页面上下文里遍历文本节点，把仍含英文字母的节点收集出来与词典比对：

```js
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
// 收集 t，过滤掉 t.toLowerCase() 已存在于词典的项
```

设置页这类大面板建议按标签页分批抓取，避免一次返回上千条。

---

## 10. 加词条 / 加规则 / 加跳过

### 加一条固定文案

1. 打开 `dicts/zh_cn.json`；
2. 插入 `"原文": "译文"`（保持按 key 小写排序，减少 diff 噪音）；
3. 重装一次（`安装汉化插件.bat`，源码目录为 `install-windows.bat`）让词典进 asar；或直接改 `%USERPROFILE%\.antigravity-zh\zh-CN.json` 热重载预览。

### 加一条动态文案

在 `dicts/engine.js` 的 `dynamicRules` 数组加一行，**必须整串锚定**（`^...$`）：

```js
[/^(\d+) tasks? (?:are )?running$/i, "正在运行 $1 个任务"],
```

捕获到名称时用 `translateCaptured(name)` 再查词。

### 加一条「这类区域不要翻译」

在 `SKIP_SELECTOR` 里加 `[data-testid="..."]`，或在 `shouldSkipNode()` 里加类名判断。

### 改完怎么验证

```bat
:: 1. 校验词典 JSON 语法
python -c "import json;json.load(open('dicts/zh_cn.json',encoding='utf-8'))"

:: 2. 重新注入（会自动重建引擎块并刷新外部词典）
安装汉化插件.bat

:: 3. 确认已注入
python install.py --status
```

---

## 11. 已知限制

| 限制 | 原因 | 现状 |
| --- | --- | --- |
| 模型回复正文保持英文 | 自由文本无法整句对齐 | 设计如此 |
| 第三方插件营销长文保留英文 | 逐词硬翻质量差 | 设计如此 |
| 新版本新增文案可能漏翻 | 词典滞后于客户端 | 提 Issue / 补词条 |
| 极少数 React 重渲染可能短暂回英文 | 组件重挂载优先于观察回调 | 下一个空闲片会重翻 |
| 动态规则改动需重装 | 规则在引擎里而非外部词典 | 有意为之（避免误伤） |
| macOS / Linux 无冒烟测试与自动回滚 | v1.5.0 的冒烟流程只实现了 Windows | 其他平台仍走「替换 → 手动启动」；失败需手动还原 |
| 菜单 / 弹窗翻译只覆盖已知词条 | 原生层用映射表，不是完整词典 | 新增文案需补 `MENU_LABELS` / `DIALOG_LABELS` |

---

## 12. 安全说明

- 注入代码是**只读**的：只读取 DOM 文本并回写文本，不修改业务逻辑、不发网络请求；
- 不包含、不分发 Antigravity 的任何二进制内容（发布包里只有本项目的源码与词典）；
- 首次安装自动备份官方原版（两处），`--restore` 可完全还原；
- 安装后自动冒烟测试，失败自动回滚，最坏情况是回到安装前的英文原版；
- 还原前校验版本，避免旧 asar 装到新客户端上；
- 修改 `app.asar` 可能违反官方服务条款，风险自负。


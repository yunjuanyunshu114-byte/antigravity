# 🀄 Antigravity 汉化插件

给 **Google Antigravity 桌面客户端**（Agent Manager）装上中文界面：下载插件包 → 解压 → 双击「安装汉化插件.bat」。脚本自动完成备份、注入、启动自检，装完直接就是中文。

官方客户端自动更新后，双击「汉化并启动.bat」即可自动重新汉化；也可以注册开机自动修复，登录时自动恢复。

> ⚠️ **非官方语言包**。本工具只修改本地 `app.asar`，安装前自动备份官方原版，可随时还原。与 Google 及 Antigravity 官方团队无关，使用风险自负。

| 项目 | 说明 |
| --- | --- |
| 当前版本 | **v1.5.0** |
| 已验证客户端 | Antigravity **2.32.1**（Windows 实测；macOS / Linux 提供同逻辑脚本） |
| 词典规模 | 约 6359 条整句词条 + 约 200 条动态正则规则 |
| 插件包 | 约 **11 MB**，内置 Windows 免安装 Python 运行时 |
| 许可证 | [MIT](LICENSE) |

---

## 目录

- [三步快速开始](#三步快速开始)
- [客户端更新后怎么办](#客户端更新后怎么办)
- [命令与参数](#命令与参数)
- [工作原理](#工作原理)
- [故障排查](#故障排查)
- [常见问题](#常见问题)
- [术语表](#术语表)
- [更新日志](#更新日志)
- [给开发者](#给开发者)

---

## 三步快速开始

### 第一步：下载插件包

打开 [Releases](https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin/releases/latest)，下载
**`Antigravity-zh-plugin-v1.5.0.zip`**（约 11 MB）。

> 下载后可以用同一页面提供的 `.sha256` 文件校验完整性，见[杀软误报或下载被拦截](#杀软误报或下载被拦截)。

### 第二步：解压

把 zip 解压到任意位置（例如 `D:\Tools\`），得到文件夹 **`Antigravity汉化插件-v1.5.0`**。

插件包已内置 Python 运行时，**不需要 git、不需要命令行、不需要自己装 Python**。

### 第三步：双击「安装汉化插件.bat」

1. 双击 **`安装汉化插件.bat`**
2. 脚本自动：关闭正在运行的 Antigravity → 解包 `app.asar` → 注入汉化 → 重新打包 → 启动客户端自检
3. 看到中文界面即安装成功；若自检失败，脚本会自动回滚官方原版并告诉你原因（详见[工作原理](#工作原理)）

还原英文原版：双击 **`还原官方原版.bat`**。

macOS / Linux 解压后执行 `./install-macos.sh`（安装）、`./launch-macos.sh`（更新后恢复）、`./restore-macos.sh`（还原），需系统自带 `python3`。

> 💡 **把这个插件文件夹留在硬盘上**。客户端每次自动更新都会覆盖汉化，留着插件包就能随时一键恢复。

---

## 客户端更新后怎么办

Antigravity 自动更新时，官方 `app.asar` 会覆盖汉化补丁——这是正常现象，不是安装失败。

### 方案一：双击「汉化并启动.bat」（最快）

1. 打开插件包文件夹
2. 双击 **`汉化并启动.bat`**
3. 脚本会自动判断：已汉化且客户端版本、词典都没变 → 直接打开客户端（通常 1 秒内）；客户端刚更新过 → 自动重新注入，再打开客户端
4. 等待界面变成中文即可

> macOS / Linux 用户执行 `./launch-macos.sh`，效果相同（等价于 `install.py --auto`）。

### 方案二：注册开机自动修复（一劳永逸）

双击 **`注册开机自动修复.bat`**，会在当前用户的注册表启动项里登记一条命令：
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`，值名 `AntigravityZhAutoRepair`。
以后每次登录系统都会静默检查：发现汉化没了（客户端更新过）就自动重新安装，不用再手动操作。
不需要管理员权限，也不会往「启动」文件夹里写 .bat（那种方式会被安全软件拦截）。
重新安装汉化时，如果之前注册过，会自动把启动项刷新为当前插件目录。

不想用了就双击 **`取消开机自动修复.bat`**。

### 方案三：完整重装

双击 **`安装汉化插件.bat`** 重新执行完整安装流程（重新备份、注入、自检、启动）。

### 关于备份

官方原版始终保留两份，客户端更新清掉一份也不会丢：

| 备份位置 | 作用 |
| --- | --- |
| `Antigravity\resources\app.asar.bak` | 安装目录内的就地备份 |
| `%USERPROFILE%\.antigravity-zh\backup\app.asar.orig` | 用户目录持久备份，**客户端更新清空 `resources\` 也不会丢** |

此外插件包还提供 **`创建桌面快捷方式.bat`**：在桌面创建名为「Antigravity 汉化版」的快捷方式，指向 `汉化并启动.bat`，以后从桌面双击即可自动重新汉化并打开客户端。

---

## 命令与参数

批处理脚本已经封装了常用组合，普通用户不需要命令。需要精细控制时，在插件包目录（或源码目录）执行
`python install.py <参数>`；插件包内可用自带的 `runtime\python.exe`：

```bat
cd /d "C:\Users\<你>\Downloads\Antigravity汉化插件-v1.5.0"
runtime\python.exe install.py --status
```

| 参数 | 作用 | 什么时候用 |
| --- | --- | --- |
| `--auto` | 智能模式：状态文件表明已汉化且客户端版本、词典哈希都没变 → 直接启动（通常 <1 秒）；否则重新注入后启动 | 「汉化并启动.bat」内部使用；客户端更新后恢复汉化 |
| `--auto-silent` | 智能模式，但**只注入、不启动**客户端 | 开机自动修复（登录启动项）、脚本后台修复 |
| `--launch` | 注入完成后启动客户端 | 希望装完立刻打开 |
| `--no-smoke` | 跳过安装后的冒烟自检 | 自动启动客户端被环境禁止时排障（**不推荐**，会失去自动回滚保护） |
| `--status` | 打印状态：是否已注入、两处备份、客户端版本、状态文件摘要 | 排查「到底装没装」 |
| `--restore` | 还原官方原版（还原前校验客户端版本） | 彻底去掉汉化 |
| `--force` | 与 `--restore` 合用：允许用客户端版本不一致的旧备份还原 | 确认要用旧版本备份恢复时 |
| `--install-task` | 在 HKCU 注册表 Run 项登记登录自动修复（值名 `AntigravityZhAutoRepair`） | 客户端经常自动更新 |
| `--remove-task` | 删除该注册表值（并清理旧方案残留） | 不再需要自动修复 |
| `--create-shortcut` | 在桌面创建「Antigravity 汉化版」快捷方式（指向 `汉化并启动.bat`） | 想从桌面直接启动并自动修复 |
| `--asar PATH` | 手动指定 `app.asar` 路径 | 客户端装在非默认位置 |
| `--version` | 打印安装器版本 | 确认插件包版本 |

补充说明：

- **不加参数**执行 `install.py` = 完整安装；Windows 下默认在替换 `app.asar` 后启动客户端做冒烟自检，成功后客户端保持运行。
- 需要手动指定非默认安装位置时，可加 `--asar "D:\Portable\Antigravity\resources\app.asar"`。
- **退出码**：`0` 成功或无需操作；`1` 前置条件 / 参数错误（如找不到 `app.asar`、客户端无法关闭）；`2` 注入或结构校验失败，安装中止（未改动客户端文件）；`3` 冒烟测试失败，已自动回滚；`4` 还原被拒（没有可用备份，或备份版本与当前客户端不一致）。
- `--install-task` / `--remove-task` 仅 Windows 可用：前者写 HKCU 注册表 Run 项，后者删除该值。它的值优先指向插件包自带的 `runtime\pythonw.exe`（无黑框）；插件目录被移动或删除后会失效，需要重新注册。
- `--help` 可查看全部参数说明。

---

## 工作原理

整体思路：**不改客户端业务代码**，只往 Electron 的几个入口文件末尾追加一层只读的翻译运行时，让渲染进程翻译界面文本、让主进程翻译原生菜单和弹窗。

### 1. 只追加注入，不改原代码

安装器解包 `app.asar` 后，只往目标文件**末尾追加**带标记的补丁块，不做任何就地字符串替换（`loadingOverlay.js` 的加载文案是唯一例外，见 [HOW_IT_WORKS](docs/HOW_IT_WORKS.md)）：

```js
// ===== AG_ZH_BEGIN:engine =====
try {
  ...补丁代码...
} catch (e) { /* 只写日志，不影响客户端 */ }
// ===== AG_ZH_END:engine =====
```

重装时按标记 / 锚点定位，从锚点处整体重建：v1.4.1 及更早版本留下的追加式引擎块、菜单补丁块会被清除后重写，不会出现新旧引擎叠加、新词典永不生效的问题。

### 2. 失败隔离

每个补丁块整体包在 `try/catch` 里：补丁自身出错只记录日志，**绝不让主进程或预加载脚本崩溃**。这是 v1.5.0 修复「装完客户端打不开」的核心改动。

### 3. 安装后冒烟测试 + 自动回滚

替换 `app.asar` 后，安装器会清空 `ELECTRON_RUN_AS_NODE` 环境变量并启动客户端做自检：

- **通过**：安装器先记录客户端主进程日志 `%APPDATA%\Antigravity\logs\main.log` 当前的字节位置，再启动客户端；60 秒内轮询到**新增日志里出现 `Starting app (v`** 且 `Antigravity.exe` 稳定存活（约 6 秒）→ 安装成功，客户端保持运行
- **失败**：进程提前消失或超时 → 杀掉进程 → 用替换前保留的官方原版（`app.asar` + `app.asar.unpacked`）回滚 → 重新启动官方版 → 以退出码 `3` 结束并给出中文原因

也就是说：**最坏情况是回到安装前的英文原版，而不是留下一个打不开的客户端。**

`--no-smoke` 可以跳过这一步，但会失去自动回滚保护，仅建议排障时使用。

### 4. 双备份

安装时把官方原版复制到 `resources\app.asar.bak`，同时另存一份到
`%USERPROFILE%\.antigravity-zh\backup\app.asar.orig`（含客户端版本、大小、SHA256、时间）。
客户端更新会整体替换 `resources\` 目录，但用户目录那份不受影响。

### 5. 还原版本校验

还原前会比对「当前 `app.asar` 内 `package.json` 的版本」与「备份 `app.asar` 内版本」：

- 版本一致 → 正常还原
- 版本不一致（说明客户端已升级，旧备份可能是上一版）→ **默认拒绝还原**（退出码 `4`）并提示先重装或修复；确认要用旧备份恢复时加 `--force`
- 当前本来就是官方原版 → 提示「无需还原」，退出码 `0`

### 6. 快速判定：状态文件

每次注入后会写状态文件 `%USERPROFILE%\.antigravity-zh\state.json`：

```json
{
  "app_version": "2.32.1",
  "dict_sha256": "…",
  "injected_sha256": "…",
  "injected_at": "2026-11-14 10:30:00",
  "toolkit_version": "1.5.0"
}
```

`--auto` 先读这个文件：当前 asar 已注入，且状态文件记录的 `dict_sha256` 与本版词典一致、`app_version` 与当前客户端版本一致，就直接启动（通常 1 秒内完成）；否则重新注入后再启动。这就是「客户端更新后双击一次即可」的实现方式。

### 7. 注入点一览

| 文件 | 运行环境 | 翻译对象 |
| --- | --- | --- |
| `dist/preload.js` | 渲染进程（主界面） | 全部界面文本、`placeholder`、`title`、`aria-label` |
| `dist/ideInstall/wizardPreload.js` | 渲染进程（安装向导） | 首次启动向导界面 |
| `dist/menu.js` | 主进程 | 原生菜单栏；同时包装 `Menu.buildFromTemplate`，托盘菜单 label 也在这里统一翻译 |
| `dist/tray.js` | 主进程 | **不追加补丁块**，托盘菜单 label 由 `menu.js` 的菜单包装统一翻译 |
| `dist/main.js` | 主进程 | 原生弹窗（退出确认等）、菜单兜底 |
| `dist/loadingOverlay.js` | 主进程 | 启动加载画面文案 |

注入的实现细节、翻译流水线的 12 个阶段、冒烟测试与回滚流程、`state.json` 判定逻辑，见 [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md)。

---

## 故障排查

### 双击安装后客户端打不开

v1.5.0 起安装器自带冒烟自检：如果注入后客户端起不来，会自动回滚官方原版并重新启动，最后以**退出码 3**结束，命令行窗口中能看到中文原因。

按顺序处理：

1. 看安装窗口最后几行提示，按提示操作（通常会告诉你已回滚到官方原版）。
2. 双击 **`还原官方原版.bat`** 再确认一次（当前已是官方原版时会提示「无需还原」）。
3. 仍打不开：在 Antigravity 里执行「修复 / 重新安装」，让官方重新下发文件。
4. 需要更多信息时，查看安装日志 `%USERPROFILE%\.antigravity-zh\logs\install-*.log`、客户端日志 `%APPDATA%\Antigravity\logs\main.log`，或执行 `runtime\python.exe install.py --status` 查看注入与备份状态。

> 不要手动删除 `app.asar.bak` 或 `%USERPROFILE%\.antigravity-zh\backup\`，那是回滚用的官方原版。

### 装完界面还是英文

1. **确认客户端已完全退出后重新打开**（包括托盘图标里的常驻进程），旧进程不会加载新界面。
2. 确认安装窗口显示的是成功，而不是「跳过」或「回滚」。
3. 执行 `runtime\python.exe install.py --status`，看到 `汉化: 已注入` 说明补丁在。
4. 如果客户端刚自动更新过，说明官方文件覆盖了补丁：双击 **`汉化并启动.bat`** 重新注入。
5. 只有部分英文：模型回复正文、代码块、diff 按设计保持英文；如果是界面按钮/菜单的英文，属于词典未覆盖，欢迎反馈原文。

### 客户端自动更新后汉化消失（正常现象）

客户端自动更新时会把 `resources\` 目录整体替换，汉化补丁随之被官方文件覆盖，界面回到英文——**这不是装坏了**。恢复方式：双击 **`汉化并启动.bat`** 重新注入并打开；或者提前注册开机自动修复，登录时自动恢复。

### 还原时提示「备份版本与当前客户端不一致」

还原只接受与当前客户端版本一致的官方备份，避免把上一版 `app.asar` 还原到新客户端上导致打不开。遇到这个提示：优先双击 **`安装汉化插件.bat`** 重新生成与当前版本匹配的备份，或在 Antigravity 里执行「修复 / 重新安装」；确认要用旧备份恢复再加 `--force`。

### 杀软误报或下载被拦截

插件包含批处理脚本和免安装 Python 运行时，运行时会写入 `app.asar`，可能被 Windows Defender 或第三方杀毒软件误报、拦截甚至隔离：

- **下载被浏览器/SmartScreen 拦截**：选择「保留」，或用 Release 页面提供的 `.sha256` 校验文件：

  ```bat
  certutil -hashfile "C:\Users\<你>\Downloads\Antigravity-zh-plugin-v1.5.0.zip" SHA256
  ```

  与 `.sha256` 文件里的值一致即可放心。
- **运行时被拦截**：把解压出来的插件文件夹加入杀软白名单，从隔离区恢复被删的文件后重新解压尝试。
- **不要长期关闭杀软**来安装；如果安装目录需要管理员权限（自定义安装到 `Program Files` 时），右键以管理员身份运行脚本。

### 如何彻底还原

1. 双击 **`还原官方原版.bat`**（或 `python install.py --restore`）。
2. 双击 **`取消开机自动修复.bat`**，移除开机自动修复注册表项（如果注册过）。
3. 可选：删除 `%USERPROFILE%\.antigravity-zh\`（状态文件、外部词典、备份都在这）和桌面快捷方式。
4. 最彻底：在 Antigravity 中执行「修复 / 重新安装」，用官方文件覆盖整个 `resources\`。

还原只替换 `app.asar`，不会动你的账号、项目和客户端设置。

---

## 常见问题

**Q：这个插件收费吗？**
A：不收费，[MIT 协议](LICENSE) 开源。

**Q：会不会影响客户端功能？会被风控吗？**
A：补丁只读取并回写界面文本，不拦截网络请求、不改业务状态；但修改 `app.asar` 本身可能违反官方服务条款，请自行评估。

**Q：支持哪些系统？**
A：Windows 已实测（Antigravity 2.32.1）；macOS / Linux 提供同一套注入逻辑的 `install-macos.sh` / `restore-macos.sh`，本版未做同等实测。

**Q：为什么不能在设置里直接选中文？**
A：Antigravity 官方目前没有中文界面选项，本插件通过注入翻译运行时实现。

**Q：客户端每次更新都要重新装一遍吗？**
A：是。更新会覆盖 `app.asar`。双击「汉化并启动.bat」一次即可；想一劳永逸就注册开机自动修复。

**Q：能不能只汉化、不自动打开客户端？**
A：可以。源码目录下 `python install.py --auto-silent`（或 `--no-smoke`）只注入不启动。

**Q：插件会收集或上传我的数据吗？**
A：不会。插件只在本机读写 `app.asar` 和本地词典，不联网、不上传界面内容。

**Q：怎么自己补词条？**
A：编辑 `%USERPROFILE%\.antigravity-zh\zh-CN.json`（保存后界面会自动重翻，无需重装）；要进发布包则改源码的 `dicts/zh_cn.json`。详见 [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md)。

**Q：不想用了怎么卸载？**
A：见[如何彻底还原](#如何彻底还原)，然后删除插件文件夹即可。

**Q：为什么有两份官方原版备份？**
A：客户端更新会清空 `resources\` 目录，安装目录里的 `.bak` 可能被删；用户目录那份保证任何时候都能还原。

**Q：开机自动修复为什么用注册表，而不是「启动」文件夹？**
A：把 .bat 写进「启动」文件夹会被部分安全软件拦截（实测报 Permission denied）；写当前用户注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 不需要管理员权限，更稳定可靠。

**Q：macOS 提示「应用已损坏，无法打开」？**
A：`sudo xattr -rd com.apple.quarantine /Applications/Antigravity.app`；安装器也会自动做 ad-hoc 重签名。

---

## 术语表

插件与文档中统一使用以下译名：

| 英文 | 译名 | 说明 |
| --- | --- | --- |
| Artifact | 工件 | 客户端产出的文件 / 预览内容 |
| Worktree | 工作树 | Git 工作树 |
| Sandbox | 沙箱 | 执行环境 |
| Review | 审查 | 代码 / 变更审查 |
| Fork | 分叉 | 对话分叉 |
| Agent | 智能体 | 执行任务的 AI 实例 |
| Subagent | 子智能体 | 由主智能体派生的子任务实例 |
| Quota | 配额 | 请求次数限制 |
| Credits | 额度 | 计费额度 |
| Customizations | 自定义（扩展） | 技能 / 插件等扩展配置 |
| Automations | 自动化 | 定时或触发的任务 |
| Workspace | 工作区 | 项目集合 |

文档中的技术词：

| 词 | 含义 |
| --- | --- |
| asar | Electron 应用归档格式，客户端代码都打包在 `app.asar` 里 |
| 注入 | 往 asar 里的入口文件追加汉化补丁代码 |
| 补丁块 | 带有 `AG_ZH_BEGIN` / `AG_ZH_END` 标记的一段追加代码 |
| 冒烟测试 | 安装后自动启动客户端、确认没被装坏的自检 |
| 回滚 | 自检失败时自动恢复备份的官方原版 |
| state.json | 记录注入结果的快速判定文件，`--auto` 靠它秒开 |

---

## 更新日志

### v1.5.0（2026-11-14）

- **修复「装完客户端打不开」**：注入架构改为「**只追加 + `try/catch` 失败隔离**」。补丁只追加在文件末尾并整体包在异常捕获里，出错只写日志，不会让预加载或主进程崩溃
- **安装后自动冒烟测试 + 回滚**：替换 `app.asar` 后自动启动客户端，60 秒内必须出现新的启动日志且进程稳定存活；失败则自动用替换前保留的官方原版回滚、重新打开官方版，退出码 `3` 并给出中文提示。最坏情况是回到英文原版，不会留下打不开的客户端
- **新增「汉化并启动.bat」**：客户端更新后双击一次，自动判断是否需要重新注入并打开客户端（已是最新则直接打开，通常 1 秒内）
- **新增「注册开机自动修复.bat / 取消开机自动修复.bat」**：写入 HKCU 注册表 Run 项（值名 `AntigravityZhAutoRepair`，无需管理员权限），登录时自动检查并重新汉化；不用「启动」文件夹里的 .bat（会被安全软件拦截）
- **新增 `--auto` 快速重装**：智能模式，已汉化且词典、客户端版本都没变就直接启动，否则注入后启动；配套 `--auto-silent`（只注入不启动）、`--launch`（注入后启动）、`--no-smoke`（跳过自检）
- **安装成功后客户端保持运行**，符合「装完就能用」的预期
- **还原保护**：还原前比对当前 `app.asar` 与备份 `app.asar` 内 `package.json` 的客户端版本，版本不一致默认拒绝并提示先重装/修复，`--force` 才允许强制还原；当前已是官方原版时提示「无需还原」并正常退出
- **兼容清理**：重装时按标记 / 锚点清除 v1.4.1 及更早版本的引擎与菜单注入块后重建，不会残留重复引擎导致新词典不生效
- **新增安装包脚本**：`汉化并启动.bat`、`创建桌面快捷方式.bat`、`注册开机自动修复.bat`、`取消开机自动修复.bat`
- **翻译补全**：6297 → **6359** 条（合并实测扫描出的 62 条 UI 缺口，含设置页说明长句、快捷键动作名、语音选择弹窗、插件市场/技能描述）；动态规则 190 → 200 条（相对时间缩写、Select project、Open 文件、Worked for · N updates、语音序号、模型名 + 限额等）；修掉实测发现的 20+ 处中英混排
- 已验证客户端 **2.32.1**

### v1.4.1 及更早（归档）

- **v1.4.1**：改为插件包（内置 Python 运行时，解压双击即装），新增用户目录持久备份；修复 `.bak` 被客户端更新清掉后无法还原、批处理输出乱码
- **v1.4.0**：适配 Antigravity 2.31，词典 5982 → 6297；精确匹配优先 + 忽略大小写兜底、拆分句合并、加载画面文案
- **v1.3.x**：词典 1855 → 5982；新增动态正则规则层与 `fmtDuration`；修复重复引擎块导致新词典永不生效
- **v1.2.0 / v1.1.x / v1.0.0**：术语统一、asar 原子替换与 macOS 重签名修复、纯 Python asar 解析与一键安装 / 还原

---

## 给开发者

### 从源码运行

```bat
git clone https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin.git
cd antigravity-zh-plugin

python install.py --auto                       :: 智能安装（需要时注入并启动）
python install.py --status                     :: 查看状态
python install.py --restore                    :: 还原官方原版
python install.py --restore --force            :: 版本不一致也强制还原
python install.py --install-task               :: 注册开机自动修复
python install.py --remove-task                :: 取消开机自动修复
python install.py --create-shortcut            :: 创建桌面快捷方式
python install.py --version                    :: 安装器版本
python install.py --asar "D:\Portable\Antigravity\resources\app.asar"   :: 手动指定路径
```

### 打包发布

```bat
python build_release.py          :: 生成 dist\Antigravity-zh-plugin-v1.5.0.zip（内置 runtime\）及 .sha256
python build_release.py --slim   :: 不内置运行时（约 250 KB，需系统已装 Python）
```

插件包结构（解压即用）：

```text
Antigravity汉化插件-v1.5.0/
├── 安装汉化插件.bat          ← 双击这个
├── 还原官方原版.bat
├── 汉化并启动.bat            ← 客户端更新后双击这个
├── 创建桌面快捷方式.bat
├── 注册开机自动修复.bat
├── 取消开机自动修复.bat
├── install-macos.sh / launch-macos.sh / restore-macos.sh
├── 使用说明.txt
├── install.py / asar.py
├── dicts/
├── docs/
└── runtime/                  ← 免安装 Python，用户机器无需任何环境
```

仓库结构：

```text
antigravity-zh-plugin/
├── install.py                # 安装器：注入 / 还原 / 状态 / 冒烟测试 / 开机自动修复
├── asar.py                   # 纯 Python asar 解包与打包
├── build_release.py          # 生成插件包（zip + sha256）
├── VERSION                   # 版本号
├── install-windows.bat       # 源码版一键安装（打包时改名为「安装汉化插件.bat」）
├── restore-windows.bat       # 源码版一键还原（打包时改名为「还原官方原版.bat」）
├── launch-windows.bat        # 源码版汉化并启动（打包时改名为「汉化并启动.bat」）
├── autorepair-on-windows.bat  # 源码版注册开机自动修复（打包时改名为「注册开机自动修复.bat」）
├── autorepair-off-windows.bat # 源码版取消开机自动修复（打包时改名为「取消开机自动修复.bat」）
├── shortcut-windows.bat      # 源码版创建桌面快捷方式（打包时改名为「创建桌面快捷方式.bat」）
├── install-macos.sh          # macOS / Linux 一键安装
├── launch-macos.sh           # macOS / Linux 汉化并启动（更新后恢复）
├── restore-macos.sh          # macOS / Linux 一键还原
├── runtime/                  # Windows 免安装 Python 运行时（不进 Git，打包时内置）
├── dicts/
│   ├── zh_cn.json            # 整句词典
│   └── engine.js             # DOM 翻译引擎模板（含动态规则）
├── docs/
│   ├── HOW_IT_WORKS.md       # 翻译机制详解（进阶阅读）
│   └── PROMPT.md             # 项目复现提示词（交给 AI 从零重做）
├── SKILL.md                  # 供 AI 智能体调用的技能说明
├── README.md
└── LICENSE                   # MIT
```

---

## 免责声明

本项目与 Google 及 Antigravity 官方团队无关，不包含 Antigravity 任何二进制内容。
修改 `app.asar` 可能违反官方服务条款，请自行评估使用风险。

## License

[MIT](LICENSE)


---
name: antigravity-zh-plugin
description: 为 Google Antigravity 桌面客户端（Agent Manager）安装、更新或还原中文汉化插件。当用户要求「给 Antigravity 装中文/汉化」、官方更新导致汉化失效后一键恢复、注册开机自动修复、或彻底还原英文原版时使用。v1.5.0 起补丁只追加并在安装后冒烟测试，失败自动回滚官方原版，避免把客户端装坏。
---

# Antigravity 汉化插件

为 Google Antigravity（Agent Manager）注入中文翻译引擎的汉化插件。

- 当前版本：**v1.5.0**
- 已验证客户端：Antigravity **2.32.1**（Windows 实测；macOS / Linux 提供同逻辑脚本）
- 词典规模：约 6359 条整句词条 + 约 200 条动态正则规则
- 包内自带的 Windows 免安装 Python 运行时，用户机器无需任何环境

## 适用对象

- Antigravity 桌面客户端（Agent Manager），Windows / macOS / Linux
- Electron 结构：`resources/app.asar` + `dist/preload.js`
- 典型请求：安装汉化 / 客户端更新后恢复 / 还原英文 / 注册开机自动修复 / 排查「装完打不开」

## 工作方式（v1.5.0）

1. 解包 `app.asar`（`asar.py` 纯 Python 实现，无需 Node.js）。
2. **只追加注入**：向入口文件末尾追加带标记的补丁块
   （`// ===== AG_ZH_BEGIN:<name> =====` … `// ===== AG_ZH_END:<name> =====`），
   **不就地替换**任何官方代码，每个补丁块整体 `try/catch`，补丁出错不影响客户端启动。
3. 注入点：`dist/preload.js` / `dist/ideInstall/wizardPreload.js`（DOM 翻译引擎）、
   `dist/menu.js`（包装 `Menu.setApplicationMenu` + `Menu.buildFromTemplate`，
   菜单与托盘标签统一翻译）、`dist/main.js`（菜单兜底 + 包装 `dialog.*` 原生弹窗）、
   `dist/loadingOverlay.js`（加载画面插入一行中文，唯一例外）。
   `dist/tray.js` **不追加补丁**，托盘菜单由菜单包装覆盖。
4. 重新打包（`chrome-devtools-mcp` 保持 unpacked）→ **替换前结构校验**（头部、文件数、入口、注入标记）
   → 同目录暂存 + `os.replace` 原子替换，并保留替换前副本用于回滚。
5. **冒烟测试 + 自动回滚**（Windows 默认）：记录 `%APPDATA%\Antigravity\logs\main.log` 偏移后启动客户端，
   60 秒内新增日志出现 `Starting app (v` 且进程稳定存活 → 成功；失败则杀进程、用替换前
   `app.asar` + `app.asar.unpacked` 回滚、启动官方原版，退出码 `3`。
6. **双备份**：`resources/app.asar.bak` + `%USERPROFILE%\.antigravity-zh\backup\app.asar.orig`。
7. **还原版本校验**：只接受与当前客户端版本一致的备份，避免旧 asar 装到新客户端导致打不开。
8. **快速自愈**：`state.json` 记录客户端版本与词典哈希，`--auto` 判定「已最新」时直接启动（<1 秒），
   否则重新注入；登录自动修复用 `--auto-silent` 静默检查 / 修复。
9. 词典复制到 `%USERPROFILE%\.antigravity-zh\zh-CN.json`，支持 `fs.watch` 热重载（只影响词典，规则需重装）。

## 使用步骤

### 插件包（推荐，用户无需任何环境）

1. 下载并解压 `Antigravity-zh-plugin-v1.5.0.zip`，得到 `Antigravity汉化插件-v1.5.0` 文件夹。
2. 完全退出 Antigravity（含托盘；脚本也会自动关闭）。
3. 双击 **`安装汉化插件.bat`**：自动关闭客户端 → 备份 → 注入 → 结构校验 → 冒烟测试 → 启动客户端。
   看到中文界面即成功；若冒烟失败会自动回滚官方原版并提示原因。

### 客户端自动更新后恢复汉化

官方更新会用原版覆盖 `app.asar`（并可能清空 `resources/` 里的 `.bak`），汉化消失属正常现象。

- 最快：双击 **`汉化并启动.bat`**（= `install.py --auto`），自动判断并重新注入、启动。
- 一劳永逸：双击 **`注册开机自动修复.bat`**（写入 HKCU 注册表 Run 项，值名 `AntigravityZhAutoRepair`；登录时静默检查，发现未汉化就自动重装，不需要管理员权限）；
  取消用 **`取消开机自动修复.bat`**。
- 桌面入口：双击 **`创建桌面快捷方式.bat`**，在桌面创建名为「Antigravity 汉化版」、指向 `汉化并启动.bat` 的快捷方式。

### 还原英文原版

双击 **`还原官方原版.bat`**（= `install.py --restore`）。当前已是官方原版时提示「无需还原」；
备份版本与当前客户端不一致时默认拒绝（退出码 4），确认要用旧备份再加 `--force`。

macOS / Linux 用 `./install-macos.sh`（安装）/ `./launch-macos.sh`（更新后恢复）/ `./restore-macos.sh`（还原），需系统自带 `python3`；无冒烟测试与自动回滚。

### 从源码运行

```bat
git clone https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin.git
cd antigravity-zh-plugin

python install.py --auto          :: 智能安装：需要时注入并启动
python install.py --status        :: 查看状态
python install.py --restore       :: 还原官方原版
python install.py --asar "D:\Portable\Antigravity\resources\app.asar"   :: 手动指定路径
```

## 参数表

| 参数 | 作用 |
| --- | --- |
| `--auto` | 智能模式：已汉化且客户端版本、词典哈希没变 → 直接启动；否则重新注入后启动 |
| `--auto-silent` | 智能模式，但只注入不启动（供登录自动修复） |
| `--launch` | 注入完成后启动客户端 |
| `--no-smoke` | 跳过安装后的冒烟测试（不推荐，会失去自动回滚保护；此时不会自动启动） |
| `--status` | 查看汉化状态、客户端版本、两处备份、`state.json`、词典、开机自动修复（注册表） |
| `--restore` | 还原官方原版（校验版本；当前已是原版则退出码 0） |
| `--force` | 与 `--restore` 合用，允许版本不一致的旧备份强制还原 |
| `--install-task` | 在 HKCU 注册表 Run 项登记登录自动修复（值名 `AntigravityZhAutoRepair`） |
| `--remove-task` | 删除该注册表值并清理旧方案残留 |
| `--create-shortcut` | 在桌面创建「Antigravity 汉化版」快捷方式（指向 `汉化并启动.bat`） |
| `--asar PATH` | 手动指定 `app.asar` 路径 |
| `--version` | 显示安装器版本 |

退出码：

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功；还原时表示无需还原 |
| `1` | 前置条件 / 参数错误（找不到 asar、客户端无法关闭、解包失败等） |
| `2` | 注入或结构校验失败，安装中止（未改动客户端文件） |
| `3` | 冒烟测试失败，已自动回滚 |
| `4` | 还原被拒（无可用备份，或备份版本与当前客户端不一致） |

## 智能体处理常见请求

| 用户请求 | 建议动作 |
| --- | --- |
| 装中文 / 汉化 | 解压插件包，双击 `安装汉化插件.bat`（源码环境 `python install.py --auto`） |
| 更新后汉化没了 | 双击 `汉化并启动.bat`；想自动恢复就注册开机自动修复 |
| 还原英文 | 双击 `还原官方原版.bat`；提示版本不一致时不要盲目 `--force` |
| 装完打不开 | 看安装窗口退出码与日志；先 `--restore` 回滚，再在客户端里「修复 / 重新安装」 |
| 想确认装没装 | `python install.py --status`，看「汉化: 已注入」 |
| 不想每次手动修 | `python install.py --install-task` |

## 打包发布

```bat
python build_release.py           :: 生成 dist\Antigravity-zh-plugin-v1.5.0.zip（内置 runtime\）及 .sha256
python build_release.py --slim    :: 不内置 Python 运行时
```

## 注意事项

- 非官方语言包；修改本地 `app.asar`，安装前自动备份官方原版。
- 修改 `app.asar` 可能违反官方服务条款，提示用户自行评估。
- 客户端更新会整体替换 `resources/`，需要重新汉化（双击「汉化并启动」或依赖开机自动修复）。
- 还原只接受与当前客户端版本一致的备份；旧备份需要 `--force` 且不推荐。
- 开机自动修复写的是 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`（值名 `AntigravityZhAutoRepair`），
  不写「启动」文件夹 `.bat`（会被安全软件拦截）；安装汉化时会自动刷新该值指向当前目录。
- 移动或删除插件目录后，已注册的开机自动修复会失效（注册表值仍指向旧路径），需要重新注册。
- macOS 若提示「应用已损坏」：`sudo xattr -rd com.apple.quarantine /Applications/Antigravity.app`；
  安装器也会自动做 ad-hoc 重签名。
- 本 skill 目录下的 `install.py`、`asar.py`、`dicts/`、`runtime/` 是运行所需文件，请保持相对结构。


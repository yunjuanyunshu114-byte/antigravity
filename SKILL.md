---
name: antigravity-zh-plugin
description: 为 Google Antigravity 桌面客户端（Agent Manager）安装/还原中文汉化插件。当用户要求“给 Antigravity 装中文/汉化”、官方更新导致汉化失效后重新安装、或需要还原英文原版时使用。插件包内置 Python 运行时，双击即装，自动探测安装路径、自动双重备份并支持一键还原。
---

# Antigravity 汉化插件

为 Google Antigravity（Agent Manager）注入中文翻译引擎的汉化插件。

- 当前版本：**v1.4.1**
- 词典规模：**6297 条**整句词条 + **189 条**动态正则规则
- 已验证客户端：Antigravity **2.31.2**（Windows；macOS 逻辑一致）

## 适用对象

- Antigravity 桌面客户端（Agent Manager），macOS / Windows / Linux
- Electron 结构：`resources/app.asar` + `dist/preload.js`

## 工作方式

1. 解包 `app.asar`（`asar.py` 纯 Python 实现，无需 Node.js）
2. 向 `dist/preload.js` 与 `dist/ideInstall/wizardPreload.js` 注入 DOM 翻译引擎
   （MutationObserver + 6297 条词典 + 189 条动态正则规则，覆盖主界面/设置/弹窗/报错）
3. 向 `dist/menu.js` 注入原生菜单翻译、`dist/tray.js` 注入托盘菜单翻译、
   `dist/main.js` 注入原生弹窗翻译、`dist/loadingOverlay.js` 注入加载画面文案
4. 重新打包（chrome-devtools-mcp 保持 unpacked）
5. macOS 自动 ad-hoc 重签名
6. 词典复制到 `~/.antigravity-zh/zh-CN.json`，支持 `fs.watch` 热重载
7. 官方原版双备份：`resources/app.asar.bak` + `~/.antigravity-zh/backup/app.asar.orig`

幂等设计：官方原版 → 注入完整引擎；已汉化版本 → 从引擎锚点到文件尾整体重建并更新词条；
`app.asar.bak` 始终保留官方原版。

翻译流水线：纯标点 → 无英文字母跳过 → 纯快捷键跳过 → 缓存 → 动态日志块 →
精确匹配（区分大小写）→ 忽略大小写 → 去尾部标点 → 时长短语 → 动态规则 →
安全护栏（长句/含中文保持英文）→ 短文本逐词兜底。
详见 `docs/HOW_IT_WORKS.md`。

## 使用步骤

### 插件包（推荐，无需任何环境）

1. 下载并解压 `Antigravity汉化插件-v1.4.1.zip`
2. 完全退出 Antigravity（含托盘）
3. 双击 `安装汉化插件.bat`（自动关进程 → 注入 → 重新启动）

还原：双击 `还原官方原版.bat`。macOS / Linux 用 `./install-macos.sh` / `./restore-macos.sh`。

### 从源码运行

```bash
git clone https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin.git
cd antigravity-zh-plugin
python install.py                                   # 自动探测路径并安装
python install.py --asar "/自定义路径/Contents/Resources/app.asar"   # 指定路径
python install.py --status                          # 查看状态与两处备份
python install.py --restore                         # 还原官方原版
```

安装前会检测 Antigravity 是否在运行；安装后启动应用即可看到中文界面。

### 客户端更新后恢复汉化

官方更新会覆盖 `app.asar`（并可能清空 `resources/` 里的 `.bak`），这是正常现象。
重新双击 `安装汉化插件.bat` 即可恢复；还原时若 `.bak` 已丢失，会自动回退到
`~/.antigravity-zh/backup/app.asar.orig`。

## 打包发布

```bash
python build_release.py           # 生成 dist/Antigravity汉化插件-v1.4.1.zip（内置 runtime/）
python build_release.py --slim    # 不内置 Python 运行时
```

## 注意事项

- 非官方语言包；修改本地 `app.asar`，安装前自动备份为 `app.asar.bak`
- macOS 若提示“应用已损坏”，执行：
  `sudo xattr -rd com.apple.quarantine /Applications/Antigravity.app`
- 本 skill 目录下的 `install.py`、`asar.py` 与 `dicts/` 是运行所需文件，请保持相对结构

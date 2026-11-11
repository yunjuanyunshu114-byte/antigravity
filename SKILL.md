---
name: antigravity-zh
description: 为 Google Antigravity 桌面客户端（Agent Manager）安装/还原中文汉化补丁。当用户要求“给 Antigravity 装中文/汉化”、官方更新导致汉化失效后重新安装、或需要还原英文原版时使用。纯 Python 零外部依赖，自动探测平台与安装路径，自动备份并支持一键还原。
---

# 谷歌反重力汉化插件（antigravity-zh）

为 Google Antigravity（Agent Manager）注入中文翻译引擎的零依赖安装器。

- 当前版本：**v1.4.0**
- 词典规模：**6297 条**整句词条 + **189 条**动态正则规则
- 已验证客户端：Antigravity **2.31.0**（Windows；macOS 逻辑一致）

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

幂等设计：官方原版 → 注入完整引擎；已汉化版本 → 从引擎锚点到文件尾整体重建并更新词条；
`app.asar.bak` 始终保留官方原版。

翻译流水线：纯标点 → 无英文字母跳过 → 纯快捷键跳过 → 缓存 → 动态日志块 →
精确匹配（区分大小写）→ 忽略大小写 → 去尾部标点 → 时长短语 → 动态规则 →
安全护栏（长句/含中文保持英文）→ 短文本逐词兜底。
详见 `docs/HOW_IT_WORKS.md`。

## 使用步骤

### 一键安装（Windows）

1. 完全退出 Antigravity（含托盘）
2. 双击 `install-windows.bat`（自动关进程 → 注入 → 重新启动）

macOS / Linux：

```bash
./install-macos.sh
```

### 命令行安装

```bash
git clone https://github.com/zhonghugo/antigravity-zh.git
cd antigravity-zh
python3 install.py                                   # 自动探测路径并安装
python3 install.py --asar "/自定义路径/Contents/Resources/app.asar"   # 指定路径
```

安装前会检测 Antigravity 是否在运行；安装后启动应用即可看到中文界面。

### 还原原版

```bash
python3 install.py --restore
# 或双击 restore-windows.bat
```

### 查看状态

```bash
python3 install.py --status
```

### 客户端更新后恢复汉化

官方更新会覆盖 `app.asar`，这是正常现象。重新双击 `install-windows.bat`
（或 `python3 install.py`）即可，无需重新下载。

## 打包发布

```bash
python build_release.py     # 生成 dist/antigravity-zh-v1.4.0.zip
```

## 注意事项

- 非官方语言包；修改本地 `app.asar`，安装前自动备份为 `app.asar.bak`
- Antigravity 官方升级会覆盖补丁，升级后重新运行安装脚本即可
- macOS 若提示“应用已损坏”，执行：
  `sudo xattr -rd com.apple.quarantine /Applications/Antigravity.app`
- 本 skill 目录下的 `install.py`、`asar.py` 与 `dicts/` 是运行所需文件，请保持相对结构

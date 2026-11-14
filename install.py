# -*- coding: utf-8 -*-
"""
Antigravity 中文汉化安装器 v1.5.0（纯 Python 零依赖）
====================================================
为 Google Antigravity 桌面客户端注入中文翻译引擎。

v1.5.0 设计要点（安全第一）：
- 只向入口文件末尾【追加】带 BEGIN/END 标记的补丁块，不改动官方原有代码；
  每个补丁块整体 try/catch 包裹，任何补丁自身出错都不会影响客户端启动。
- 安装后自动冒烟测试：真启动一次客户端并确认能起来；失败自动回滚官方原版。
- 还原前校验备份与当前客户端版本是否一致，避免把旧版 asar 还原到新客户端。
- --auto：客户端更新后双击一次即可自动重新汉化并启动（已汉化则秒开）。

用法：
    python install.py                 # 安装汉化（含冒烟测试与自动启动）
    python install.py --auto          # 智能模式：需要时才重新汉化，然后启动
    python install.py --auto-silent   # 需要时重新汉化，不启动（供开机任务用）
    python install.py --launch        # 安装后启动客户端
    python install.py --no-smoke      # 跳过冒烟测试（不推荐）
    python install.py --restore       # 还原官方原版（校验版本）
    python install.py --status        # 查看状态
    python install.py --install-task  # 注册登录时自动修复任务
    python install.py --remove-task   # 移除登录时自动修复任务
    python install.py --asar PATH     # 手动指定 app.asar 路径

说明：本工具修改本地 app.asar，非 Google 官方语言包。客户端自动更新后汉化会
消失，双击「汉化并启动.bat」或重新运行本脚本即可恢复。
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asar  # noqa: E402

TOOLKIT_VERSION = "1.5.0"
TAG = "Antigravity Chinese Translation Injection v5-appendonly"
DICT_PLACEHOLDER = "__DICT_ITEMS__"
ENGINE_START_MARKER = "(function() {\n  const dictionary = {"
UNPACK_PATTERNS = ["**/node_modules/chrome-devtools-mcp/**"]

BLOCK_BEGIN = "// ===== AG_ZH_BEGIN:%s ====="
BLOCK_END = "// ===== AG_ZH_END:%s ====="
BLOCK_BEGIN_PREFIX = "// ===== AG_ZH_BEGIN:"
LEGACY_MARKERS = [
    "// ===== Antigravity Chinese Translation Injection v3-full =====",
    "// ===== Antigravity Chinese Translation Injection v2-extra =====",
    "// ===== Antigravity Chinese Translation Injection v4-appendonly =====",
    "const menuTranslationMap = {",
]
LEGACY_MENU_CALL = "if (typeof translateMenu === 'function') { menu.items.forEach(translateMenu); } "

USER_DIR = os.path.join(os.path.expanduser("~"), ".antigravity-zh")
BACKUP_DIR = os.path.join(USER_DIR, "backup")
BACKUP_ASAR = os.path.join(BACKUP_DIR, "app.asar.orig")
BACKUP_META = os.path.join(BACKUP_DIR, "meta.json")
STATE_FILE = os.path.join(USER_DIR, "state.json")
EXT_DICT = os.path.join(USER_DIR, "zh-CN.json")
LOG_DIR = os.path.join(USER_DIR, "logs")
TASK_NAME = "AntigravityZhAutoRepair"
APP_EXE_NAMES = ["Antigravity.exe"]
# 登录时自动修复：写 HKCU Run 注册表项（无需管理员权限；
# 启动文件夹里的 .bat 会被安全软件拦截，注册表 Run 更稳）
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE_NAME = "AntigravityZhAutoRepair"
# 旧方案残留（v1.5.0 早期测试用），清理用
LEGACY_STARTUP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                                  "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
LEGACY_STARTUP_FILE = os.path.join(LEGACY_STARTUP_DIR, "AntigravityZhAutoRepair.bat")

_LOG_PATH = None


def toolkit_version():
    try:
        with open(os.path.join(HERE, "VERSION"), "r", encoding="utf-8") as f:
            return f.read().strip() or TOOLKIT_VERSION
    except Exception:
        return TOOLKIT_VERSION


def setup_log():
    global _LOG_PATH
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        _LOG_PATH = os.path.join(LOG_DIR, "install-%s.log" % time.strftime("%Y%m%d-%H%M%S"))
        with open(_LOG_PATH, "w", encoding="utf-8") as f:
            f.write("Antigravity 汉化安装器 v%s\n" % toolkit_version())
            f.write("time: %s\nplatform: %s\npython: %s\n\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), sys.platform, sys.version.replace("\n", " ")))
    except Exception:
        _LOG_PATH = None


def say(msg=""):
    print(msg)
    if _LOG_PATH:
        try:
            with open(_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(str(msg) + "\n")
        except Exception:
            pass


def die(msg, code=1):
    say("")
    say("[ERR] " + msg)
    if _LOG_PATH:
        say("[i] 详细日志: " + _LOG_PATH)
    sys.exit(code)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- 平台与路径
def detect_paths(asar_path=None):
    if asar_path:
        if not os.path.exists(asar_path):
            die("指定的 app.asar 不存在: %s" % asar_path)
        return os.path.abspath(asar_path), os.path.dirname(os.path.abspath(asar_path))

    candidates = []
    if sys.platform == "darwin":
        candidates = [
            "/Applications/Antigravity.app/Contents/Resources/app.asar",
            os.path.expanduser("~/Applications/Antigravity.app/Contents/Resources/app.asar"),
        ]
    elif sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            os.path.join(base, "Programs", "Antigravity", "resources", "app.asar"),
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Antigravity", "resources", "app.asar"),
        ]
    elif sys.platform.startswith("linux"):
        candidates = [
            "/opt/Antigravity/resources/app.asar",
            os.path.expanduser("~/.local/share/Antigravity/resources/app.asar"),
        ]
    for c in candidates:
        if c and os.path.exists(c):
            return c, os.path.dirname(c)
    die("未找到 Antigravity app.asar。\n"
        "      macOS: /Applications/Antigravity.app\n"
        "      Windows: %%LOCALAPPDATA%%\\Programs\\Antigravity\n"
        "      或使用 --asar 手动指定路径。")


def app_exe_path(resources_dir=None):
    if sys.platform == "darwin":
        if resources_dir:
            return os.path.dirname(os.path.dirname(resources_dir))
        return "/Applications/Antigravity.app"
    if sys.platform.startswith("linux"):
        return "/opt/Antigravity/Antigravity"
    if resources_dir:
        app_root = os.path.dirname(resources_dir)
        exe = os.path.join(app_root, "Antigravity.exe")
        if os.path.exists(exe):
            return exe
    for base in (os.environ.get("LOCALAPPDATA", ""),
                 os.environ.get("ProgramFiles", ""),
                 os.environ.get("ProgramFiles(x86)", "")):
        if not base:
            continue
        exe = os.path.join(base, "Programs", "Antigravity", "Antigravity.exe")
        if not os.path.exists(exe):
            exe = os.path.join(base, "Antigravity", "Antigravity.exe")
        if os.path.exists(exe):
            return exe
    return None


def is_app_running():
    try:
        if sys.platform == "darwin":
            r = subprocess.run(["pgrep", "-f", "Antigravity.app/Contents/MacOS"], capture_output=True)
            return r.returncode == 0
        if sys.platform == "win32":
            r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Antigravity.exe"],
                               capture_output=True, text=True, encoding="utf-8", errors="ignore")
            return "Antigravity.exe" in (r.stdout or "")
        r = subprocess.run(["pgrep", "-x", "Antigravity"], capture_output=True)
        return r.returncode == 0
    except Exception:
        return False


def kill_app(wait_seconds=20):
    if not is_app_running():
        return True
    say("[*] 正在关闭 Antigravity ...")
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/IM", "Antigravity.exe", "/F", "/T"],
                           capture_output=True, text=True, encoding="utf-8", errors="ignore")
        elif sys.platform == "darwin":
            subprocess.run(["pkill", "-f", "Antigravity.app/Contents/MacOS"], capture_output=True)
        else:
            subprocess.run(["pkill", "-x", "Antigravity"], capture_output=True)
    except Exception:
        pass
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if not is_app_running():
            time.sleep(1.0)  # 留时间给系统释放文件句柄
            return True
        time.sleep(0.5)
    return not is_app_running()


def start_app(exe):
    if not exe:
        return False
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", exe], close_fds=True)
            return True
        env = os.environ.copy()
        for k in ("ELECTRON_RUN_AS_NODE", "NODE_USE_ENV_PROXY", "ELECTRON_NO_ATTACH_CONSOLE"):
            env.pop(k, None)
        flags = 0
        if sys.platform == "win32":
            flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen([exe], env=env, close_fds=True, creationflags=flags,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        say("[!] 启动客户端失败: %s" % e)
        return False


def app_log_path():
    if sys.platform == "win32":
        return os.path.join(os.environ.get("APPDATA", ""), "Antigravity", "logs", "main.log")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Antigravity/logs/main.log")
    return os.path.expanduser("~/.config/Antigravity/logs/main.log")


def _read_from_offset(path, offset):
    try:
        if not os.path.exists(path):
            return ""
        size = os.path.getsize(path)
        if size <= offset:
            return ""
        with open(path, "rb") as f:
            f.seek(offset)
            return f.read().decode("utf-8", "ignore")
    except Exception:
        return ""


def smoke_test(exe, timeout=60):
    """真启动一次客户端，确认能正常起来。返回 (ok, reason)。成功时客户端保持运行。"""
    if sys.platform != "win32":
        return True, "非 Windows 平台跳过冒烟测试"
    if not exe:
        return False, "找不到 Antigravity.exe"
    log = app_log_path()
    try:
        offset = os.path.getsize(log) if os.path.exists(log) else 0
    except Exception:
        offset = 0
    say("[*] 冒烟测试：启动客户端验证（最多 %d 秒）..." % timeout)
    if not start_app(exe):
        return False, "启动失败"
    deadline = time.time() + timeout
    seen_start = False
    stable_since = None
    while time.time() < deadline:
        if not is_app_running():
            return False, "客户端进程启动后退出"
        if not seen_start:
            chunk = _read_from_offset(log, offset)
            if "Starting app (v" in chunk:
                seen_start = True
                stable_since = time.time()
        if seen_start and stable_since and (time.time() - stable_since) >= 6:
            if is_app_running():
                return True, "客户端已正常启动"
            return False, "客户端启动后又退出"
        time.sleep(1.0)
    if seen_start:
        return False, "客户端启动后不稳定"
    return False, "等待超时（未看到启动日志）"


# ---------------------------------------------------------------- 词典与引擎
def load_dictionary():
    d = {}
    dict_path = os.path.join(HERE, "dicts", "zh_cn.json")
    if not os.path.exists(dict_path):
        die("找不到字典文件: %s" % dict_path)
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        d.update(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "key" in item and "value" in item:
                d[item["key"]] = item["value"]
    if not d:
        die("字典为空")
    return d


def dictionary_sha(dictionary):
    payload = json.dumps(dictionary, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_engine_template():
    p = os.path.join(HERE, "dicts", "engine.js")
    if not os.path.exists(p):
        die("找不到引擎模板: %s" % p)
    return read_text(p)


def build_engine_block(dictionary):
    items = []
    for k, v in dictionary.items():
        items.append("    %s: %s" % (json.dumps(k, ensure_ascii=False),
                                     json.dumps(v, ensure_ascii=False)))
    dict_block = "// ===== %s =====\n  const extraDict = {\n%s\n  };\n" % (
        TAG, ",\n".join(items))
    engine = load_engine_template().replace(DICT_PLACEHOLDER, dict_block)
    return ("try {\n" + engine.rstrip() + "\n} catch (e) {\n"
            "  try { console.error('[Antigravity-ZH] 引擎初始化失败', e); } catch (_) {}\n"
            "}")


MENU_LABELS = {
    "File": "文件", "Edit": "编辑", "View": "视图", "Workspace": "工作区",
    "Window": "窗口", "Help": "帮助", "New Window": "新建窗口", "New Conversation": "新建对话",
    "Docs": "使用文档", "Documentation": "使用文档", "Toggle Developer Tools": "开发者工具",
    "Check for Updates": "检查更新", "Checking for Updates...": "正在检查更新...",
    "Downloading Update...": "正在下载更新...", "Restart to Update": "重启以应用更新",
    "Undo": "撤销", "Redo": "重做", "Cut": "剪切", "Copy": "复制", "Paste": "粘贴",
    "Select All": "全选", "Minimize": "最小化", "Close": "关闭", "Quit": "退出",
    "Quit Antigravity": "退出 Antigravity", "About Antigravity": "关于 Antigravity",
    "Services": "服务", "Hide Antigravity": "隐藏 Antigravity", "Hide Others": "隐藏其他",
    "Show All": "显示全部", "Force Reload": "强制重新加载", "Reload": "重新加载",
    "Actual Size": "实际大小", "Zoom In": "放大", "Zoom Out": "缩小",
    "Toggle Full Screen": "切换全屏", "Settings": "设置", "Settings...": "设置...",
    "Preferences": "偏好设置", "Preferences...": "偏好设置...", "Exit": "退出",
    "No agents running": "没有智能体在运行", "Open Antigravity": "打开 Antigravity",
    "Learn More": "了解更多", "Show Logs": "显示日志", "Reload Window": "重新加载窗口",
    "New Agent": "新建智能体", "Open Settings": "打开设置", "Export": "导出",
    "Import": "导入", "Remove": "移除", "Delete": "删除", "Rename": "重命名",
    "Select Project": "选择项目", "Open Folder": "打开文件夹", "Open Terminal": "打开终端",
    "Connect to WSL": "连接到 WSL", "Start New Chat": "开始新对话",
}
MENU_ROLES = {
    "undo": "撤销", "redo": "重做", "cut": "剪切", "copy": "复制", "paste": "粘贴",
    "selectAll": "全选", "reload": "重新加载", "forceReload": "强制重新加载",
    "toggleDevTools": "开发者工具", "resetZoom": "实际大小", "zoomIn": "放大",
    "zoomOut": "缩小", "togglefullscreen": "切换全屏", "minimize": "最小化",
    "close": "关闭", "quit": "退出", "about": "关于", "services": "服务",
    "hide": "隐藏", "hideOthers": "隐藏其他", "unhide": "显示全部",
    "front": "前置全部窗口", "newWindow": "新建窗口", "window": "窗口",
    "help": "帮助", "file": "文件", "edit": "编辑", "view": "视图",
}
DIALOG_LABELS = {
    "Confirm Quit": "确认退出", "Are you sure you want to quit?": "您确定要退出吗？",
    "There may be agents or background tasks running.": "可能还有智能体或后台任务正在运行。",
    "Quit": "退出", "Cancel": "取消", "OK": "确定", "Save": "保存",
    "Don't Save": "不保存", "Yes": "是", "No": "否", "Continue": "继续",
    "Error": "错误", "Warning": "警告", "Antigravity": "Antigravity",
}


def _js_map(d):
    parts = []
    for k in d:
        parts.append("    %s: %s" % (json.dumps(k, ensure_ascii=False), json.dumps(d[k], ensure_ascii=False)))
    return "{\n" + ",\n".join(parts) + "\n  }"


MENU_PATCH_JS = """(function () {
  try {
    var electron = require('electron');
    var Menu = electron && electron.Menu;
    if (!Menu || Menu.__AG_ZH_MENU__) return;
    var LABELS = __MENU_LABELS__;
    var ROLES = __MENU_ROLES__;
    function tr(s) {
      if (typeof s !== 'string') return s;
      if (Object.prototype.hasOwnProperty.call(LABELS, s)) return LABELS[s];
      var m = /^(\\d+) active agents?$/.exec(s);
      if (m) return m[1] + ' 个智能体运行中';
      m = /^Open (.+)$/.exec(s);
      if (m) return '打开 ' + m[1];
      return s;
    }
    function walk(item) {
      if (!item || typeof item !== 'object') return;
      try {
        if (typeof item.label === 'string' && item.label) {
          item.label = tr(item.label);
        } else if (!item.label && typeof item.role === 'string' && ROLES[item.role]) {
          item.label = ROLES[item.role];
        }
        var sub = item.submenu;
        if (sub && typeof sub === 'object') {
          if (Array.isArray(sub)) sub.forEach(walk);
          else if (Array.isArray(sub.items)) sub.items.forEach(walk);
        }
      } catch (e) {}
    }
    var origSet = Menu.setApplicationMenu;
    if (typeof origSet === 'function') {
      Menu.setApplicationMenu = function (menu) {
        try { if (menu && Array.isArray(menu.items)) menu.items.forEach(walk); } catch (e) {}
        return origSet.apply(this, arguments);
      };
    }
    var origBuild = Menu.buildFromTemplate;
    if (typeof origBuild === 'function') {
      Menu.buildFromTemplate = function (template) {
        try { if (Array.isArray(template)) template.forEach(walk); } catch (e) {}
        return origBuild.apply(this, arguments);
      };
    }
    Menu.__AG_ZH_MENU__ = true;
  } catch (e) {
    try { console.error('[Antigravity-ZH] 菜单补丁失败', e); } catch (_) {}
  }
})();"""

DIALOG_PATCH_JS = """(function () {
  try {
    var electron = require('electron');
    var dialog = electron && electron.dialog;
    if (!dialog || dialog.__AG_ZH_DIALOG__) return;
    var LABELS = __DIALOG_LABELS__;
    function tr(s) {
      if (typeof s !== 'string') return s;
      return Object.prototype.hasOwnProperty.call(LABELS, s) ? LABELS[s] : s;
    }
    function patchOptions(o) {
      try {
        if (!o || typeof o !== 'object') return;
        if (typeof o.title === 'string') o.title = tr(o.title);
        if (typeof o.message === 'string') o.message = tr(o.message);
        if (typeof o.detail === 'string') o.detail = tr(o.detail);
        if (typeof o.checkboxLabel === 'string') o.checkboxLabel = tr(o.checkboxLabel);
        if (typeof o.buttonLabel === 'string') o.buttonLabel = tr(o.buttonLabel);
        if (Array.isArray(o.buttons)) o.buttons = o.buttons.map(tr);
      } catch (e) {}
    }
    function argOptions(a, b) {
      if (b && typeof b === 'object') return b;
      if (a && typeof a === 'object') return a;
      return null;
    }
    var names = ['showMessageBox', 'showMessageBoxSync', 'showOpenDialog', 'showOpenDialogSync',
                 'showSaveDialog', 'showSaveDialogSync', 'showErrorBox'];
    for (var i = 0; i < names.length; i++) {
      try {
        var name = names[i];
        var fn = dialog[name];
        if (typeof fn !== 'function') continue;
        dialog[name] = (function (orig) {
          return function (a, b) {
            try { patchOptions(argOptions(a, b)); } catch (e) {}
            if (name === 'showErrorBox') {
              try { return orig.call(this, tr(a), tr(b)); } catch (e) {}
            }
            return orig.apply(this, arguments);
          };
        })(fn);
      } catch (e) {}
    }
    dialog.__AG_ZH_DIALOG__ = true;
  } catch (e) {
    try { console.error('[Antigravity-ZH] 对话框补丁失败', e); } catch (_) {}
  }
})();"""


def build_menu_block():
    js = MENU_PATCH_JS.replace("__MENU_LABELS__", _js_map(MENU_LABELS))
    return js.replace("__MENU_ROLES__", _js_map(MENU_ROLES))


def build_dialog_block():
    return DIALOG_PATCH_JS.replace("__DIALOG_LABELS__", _js_map(DIALOG_LABELS))


# ---------------------------------------------------------------- 注入与清理
def _truncate_tail(content, markers):
    idx = -1
    for m in markers:
        if not m:
            continue
        i = content.find(m)
        if i >= 0 and (idx < 0 or i < idx):
            idx = i
    if idx >= 0:
        content = content[:idx]
    return content.rstrip() + "\n"


def apply_blocks(path, blocks, engine=False):
    """清除旧注入块后，把 blocks 以标记块形式追加到文件末尾。"""
    content = read_text(path)
    content = content.replace(LEGACY_MENU_CALL, "")
    markers = [BLOCK_BEGIN_PREFIX] + LEGACY_MARKERS
    if engine:
        markers = markers + [ENGINE_START_MARKER]
    content = _truncate_tail(content, markers)
    for name, body in blocks:
        content += "\n" + (BLOCK_BEGIN % name) + "\n" + body.rstrip() + "\n" + (BLOCK_END % name) + "\n"
    write_text(path, content)
    return content


def patch_loading_overlay(tmp):
    path = os.path.join(tmp, "dist", "loadingOverlay.js")
    if not os.path.exists(path):
        say("[!] loadingOverlay.js 不存在，跳过加载画面翻译")
        return False
    content = read_text(path)
    if "AG_ZH_LOADING" in content:
        say("[*] loadingOverlay.js 已含中文加载提示，跳过")
        return True
    snippet = '正在加载 Antigravity'
    for bad in ("$", "`", "\\"):
        if bad in snippet:
            say("[!] 加载提示文本包含危险字符，跳过")
            return False
    old = '<div class="text">Loading Antigravity</div>'
    if old in content:
        content = content.replace(old, '<div class="text">' + snippet + '</div> <!-- AG_ZH_LOADING -->', 1)
        write_text(path, content)
        say("[OK] 加载画面翻译完成")
        return True
    if "</svg>" in content:
        css_anchor = "  @keyframes logo-pulse {"
        text_css = "  .text { margin-top: 16px; font-size: 14px; letter-spacing: 0.02em; opacity: 0.7; }\n"
        if ".text {" not in content and css_anchor in content:
            content = content.replace(css_anchor, text_css + css_anchor, 1)
        content = content.replace("</svg>", "</svg>\n  <div class=\"text\">" + snippet +
                                  "</div> <!-- AG_ZH_LOADING -->", 1)
        write_text(path, content)
        say("[OK] 加载画面翻译完成")
        return True
    say("[!] loadingOverlay.js 锚点未匹配，跳过加载画面翻译")
    return False


# ---------------------------------------------------------------- 备份与还原
def save_persistent_backup(asar_path, app_version=""):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(asar_path, BACKUP_ASAR)
    meta = {
        "app_version": app_version,
        "toolkit_version": toolkit_version(),
        "size": os.path.getsize(asar_path),
        "sha256": sha256(asar_path),
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(BACKUP_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def read_meta():
    try:
        with open(BACKUP_META, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def safe_asar_version(path):
    try:
        return asar.read_json(path, "package.json").get("version", "") or ""
    except Exception:
        return ""


INJECTION_NEEDLES = [
    TAG.encode("utf-8"),
    b"AG_ZH_BEGIN:engine",
    b"Antigravity Chinese Translation Injection",
    b"Antigravity-ZH",
]


def quick_is_patched(path):
    """判断 asar 是否被本插件（任意历史版本）注入过。"""
    needles = INJECTION_NEEDLES
    try:
        with open(path, "rb") as f:
            tail = b""
            while True:
                chunk = f.read(1 << 20)
                if not chunk:
                    return False
                buf = tail + chunk
                for n in needles:
                    if n in buf:
                        return True
                tail = buf[-64:]
    except OSError:
        return False


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(app_version, dict_sha, asar_sha):
    data = {
        "app_version": app_version,
        "dict_sha256": dict_sha,
        "injected_sha256": asar_sha,
        "injected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "toolkit_version": toolkit_version(),
    }
    os.makedirs(USER_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- 原子替换
def swap_in(asar_path, new_asar):
    stage = asar_path + ".agzh_new"
    unpacked = asar_path + ".unpacked"
    new_unpacked = new_asar + ".unpacked"
    keep_asar = asar_path + ".agzh_keep.asar"
    keep_unpacked = asar_path + ".unpacked.agzh_old"

    if os.path.exists(keep_asar):
        os.remove(keep_asar)
    if os.path.isdir(keep_unpacked):
        shutil.rmtree(keep_unpacked, ignore_errors=True)
    shutil.copy2(asar_path, keep_asar)
    shutil.copy2(new_asar, stage)

    if os.path.isdir(unpacked):
        os.rename(unpacked, keep_unpacked)
    if os.path.isdir(new_unpacked):
        shutil.move(new_unpacked, unpacked)
    try:
        os.replace(stage, asar_path)
    except Exception:
        if os.path.isdir(unpacked):
            shutil.rmtree(unpacked, ignore_errors=True)
        if os.path.isdir(keep_unpacked):
            os.rename(keep_unpacked, unpacked)
        if os.path.exists(keep_asar):
            os.remove(keep_asar)
        raise
    finally:
        if os.path.exists(stage):
            os.remove(stage)
    return {"keep_asar": keep_asar,
            "keep_unpacked": keep_unpacked if os.path.isdir(keep_unpacked) else None}


def finalize_swap(state):
    try:
        if state.get("keep_asar") and os.path.exists(state["keep_asar"]):
            os.remove(state["keep_asar"])
    except Exception:
        pass
    try:
        if state.get("keep_unpacked") and os.path.isdir(state["keep_unpacked"]):
            shutil.rmtree(state["keep_unpacked"], ignore_errors=True)
    except Exception:
        pass


def rollback_swap(asar_path, state):
    keep_asar = state.get("keep_asar")
    keep_unpacked = state.get("keep_unpacked")
    if not keep_asar or not os.path.exists(keep_asar):
        return False
    stage = asar_path + ".agzh_restore"
    shutil.copy2(keep_asar, stage)
    if keep_unpacked and os.path.isdir(keep_unpacked):
        unpacked = asar_path + ".unpacked"
        if os.path.isdir(unpacked):
            shutil.rmtree(unpacked, ignore_errors=True)
        os.rename(keep_unpacked, unpacked)
    os.replace(stage, asar_path)
    if os.path.exists(keep_asar):
        os.remove(keep_asar)
    return True


# ---------------------------------------------------------------- 安装主流程
def original_unpacked_set(asar_path):
    """读取原 asar 中被标记为 unpacked 的文件集合（只读头，很快）。"""
    try:
        return set(rel for rel, size, unp in asar.list_files(asar_path) if unp)
    except Exception:
        return set()


def extract_and_prepare(asar_path):
    tmp = tempfile.mkdtemp(prefix="agy_zh_")
    try:
        asar.extract(asar_path, tmp)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        die("解包 app.asar 失败: %s" % e)
    return tmp


def ensure_backup(asar_path, app_version, already):
    bak = asar_path + ".bak"
    if not already:
        if not os.path.exists(bak):
            shutil.copy2(asar_path, bak)
            say("[OK] 已备份官方原版 -> %s" % bak)
        elif os.path.getmtime(asar_path) > os.path.getmtime(bak):
            shutil.copy2(asar_path, bak)
            say("[OK] 检测到官方版本已更新，已刷新备份 -> %s" % bak)
        else:
            say("[*] 已有官方原版备份，直接使用")
        try:
            meta = save_persistent_backup(asar_path, app_version)
            say("[OK] 官方原版已另存：%s（版本 %s）" % (BACKUP_ASAR, app_version or "未知"))
            return meta
        except Exception as e:
            say("[!] 持久备份失败（不影响安装）: %s" % e)
    return read_meta()


def verify_new_asar(path, tmp_dir, patched_rels, expected_unpacked=None):
    """结构校验：能读头、文件数一致、unpacked 集合保持、关键注入文件含标记、入口文件存在。"""
    header_ok = False
    try:
        files = asar.list_files(path)
        header_ok = True
    except Exception as e:
        return False, "重建的 app.asar 无法读取: %s" % e
    expected = 0
    for root, dirs, fs in os.walk(tmp_dir):
        expected += len(fs)
    if len(files) != expected:
        return False, "文件数量不一致（期望 %d，实际 %d）" % (expected, len(files))
    names = set(rel for rel, size, unp in files)
    if expected_unpacked:
        got_unpacked = set(rel for rel, size, unp in files if unp)
        if got_unpacked != expected_unpacked:
            return False, "unpacked 文件集合不一致（期望 %d，实际 %d）" % (
                len(expected_unpacked), len(got_unpacked))
    try:
        pkg = asar.read_json(path, "package.json")
    except Exception as e:
        return False, "读取 package.json 失败: %s" % e
    main_rel = str(pkg.get("main") or "").replace("\\", "/").lstrip("./")
    if main_rel and main_rel not in names:
        return False, "入口文件不存在: %s" % main_rel
    for rel, marker in patched_rels:
        try:
            text = asar.read_file(path, rel).decode("utf-8", "ignore")
        except Exception as e:
            return False, "读取 %s 失败: %s" % (rel, e)
        if marker not in text:
            return False, "%s 缺少注入标记 %s" % (rel, marker)
    return True, "ok"


def has_installed_app(resources_dir):
    """判断 asar 所在目录是否是真实安装目录（旁边有客户端可执行文件）。"""
    root = os.path.dirname(resources_dir)
    if sys.platform == "win32":
        return os.path.exists(os.path.join(root, "Antigravity.exe"))
    if sys.platform == "darwin":
        return os.path.isdir(root) and root.endswith(".app")
    return os.path.exists(os.path.join(root, "Antigravity"))


def cmd_install(args, launch_after=None):
    asar_path, resources_dir = detect_paths(args.asar)
    installed_app = has_installed_app(resources_dir)
    offline = bool(args.asar) and not installed_app
    exe = app_exe_path(resources_dir) if installed_app else None
    say("[*] 使用 app.asar: %s" % asar_path)
    say("[*] 客户端: %s" % (exe or "未找到（稍后仅注入）"))

    dict_ = load_dictionary()
    dsha = dictionary_sha(dict_)
    say("[*] 词典词条: %d（%s）" % (len(dict_), dsha[:12]))

    if offline:
        say("[i] 离线模式（操作的是自定义 app.asar 副本，不启动/不影响已安装客户端）")
    elif is_app_running():
        if not kill_app():
            die("Antigravity 正在运行且无法关闭，请手动完全退出后重试。")

    unpacked_set = original_unpacked_set(asar_path)
    if unpacked_set:
        say("[*] 原包 unpacked 文件: %d 个（将原样保持）" % len(unpacked_set))
    tmp = extract_and_prepare(asar_path)
    try:
        preload = os.path.join(tmp, "dist", "preload.js")
        if not os.path.exists(preload):
            die("解包结果里没有 dist/preload.js，客户端结构可能已变化，已中止（未改动任何文件）。")
        app_version = ""
        try:
            with open(os.path.join(tmp, "package.json"), "r", encoding="utf-8") as f:
                app_version = json.load(f).get("version", "")
        except Exception:
            app_version = ""
        say("[*] 客户端版本: %s" % (app_version or "未知"))

        preload_text = read_text(preload)
        already = (("AG_ZH_BEGIN:engine" in preload_text)
                   or (ENGINE_START_MARKER in preload_text)
                   or ("Antigravity Chinese Translation Injection" in preload_text)
                   or ("Antigravity-ZH" in preload_text))
        ensure_backup(asar_path, app_version, already)
        if already:
            usable = [x for x in (asar_path + ".bak", BACKUP_ASAR)
                      if os.path.exists(x) and not quick_is_patched(x)]
            if not usable:
                say("[!] 警告：两处官方备份都不可用（可能都被污染/被删）。")
                say("    这会导致将来无法一键还原英文原版。建议：在 Antigravity 里执行「重新安装/修复」，")
                say("    再运行本安装器，即可重新生成当前版本的官方备份。")

        # ---- 注入（全部为「末尾追加 + try/catch」）----
        patched = []
        engine_block = build_engine_block(dict_)
        apply_blocks(preload, [("engine", engine_block)], engine=True)
        patched.append(("dist/preload.js", BLOCK_BEGIN % "engine"))
        say("[OK] dist/preload.js 注入翻译引擎")

        wizard = os.path.join(tmp, "dist", "ideInstall", "wizardPreload.js")
        if os.path.exists(wizard):
            apply_blocks(wizard, [("engine", engine_block)], engine=True)
            patched.append(("dist/ideInstall/wizardPreload.js", BLOCK_BEGIN % "engine"))
            say("[OK] dist/ideInstall/wizardPreload.js 注入翻译引擎")

        try:
            menu_js = os.path.join(tmp, "dist", "menu.js")
            if os.path.exists(menu_js):
                apply_blocks(menu_js, [("menu", build_menu_block())])
                patched.append(("dist/menu.js", BLOCK_BEGIN % "menu"))
                say("[OK] dist/menu.js 注入菜单翻译（运行时包装）")
            else:
                say("[!] dist/menu.js 不存在，跳过菜单翻译")
            main_js = os.path.join(tmp, "dist", "main.js")
            if os.path.exists(main_js):
                apply_blocks(main_js, [("menu", build_menu_block()), ("dialog", build_dialog_block())])
                patched.append(("dist/main.js", BLOCK_BEGIN % "menu"))
                patched.append(("dist/main.js", BLOCK_BEGIN % "dialog"))
                say("[OK] dist/main.js 注入对话框/菜单翻译（运行时包装）")
            else:
                say("[!] dist/main.js 不存在，跳过对话框翻译")
        except Exception as e:
            say("[!] 主进程补丁跳过（不影响启动）: %s" % e)

        patch_loading_overlay(tmp)

        # ---- 重新打包 + 结构校验 ----
        build_dir = tempfile.mkdtemp(prefix="agy_zh_out_")
        new_asar = os.path.join(build_dir, "app.asar")
        say("[*] 重新打包（unpack: chrome-devtools-mcp）...")
        try:
            asar.pack(tmp, new_asar, UNPACK_PATTERNS, exact_unpack=unpacked_set)
        except Exception as e:
            die("重新打包失败: %s（未改动任何文件）" % e)
        if not os.path.exists(new_asar) or os.path.getsize(new_asar) == 0:
            die("打包结果为空（未改动任何文件）")
        ok, reason = verify_new_asar(new_asar, tmp, patched, unpacked_set)
        if not ok:
            die("重建的 app.asar 结构校验失败：%s（未改动任何文件）" % reason, 2)
        say("[OK] 结构校验通过（文件数 %d）" % len(asar.list_files(new_asar)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 原子替换 ----
    swap_state = None
    try:
        swap_state = swap_in(asar_path, new_asar)
        say("[OK] 已替换 app.asar（新大小: %d bytes）" % os.path.getsize(asar_path))
        say("[OK] SHA256: %s" % sha256(asar_path))

        os.makedirs(USER_DIR, exist_ok=True)
        shutil.copy2(os.path.join(HERE, "dicts", "zh_cn.json"), EXT_DICT)
        say("[OK] 外部词典已更新：%s" % EXT_DICT)

        # ---- 冒烟测试 ----
        do_smoke = (not args.no_smoke) and sys.platform == "win32" and not offline
        if do_smoke:
            ok, reason = smoke_test(exe)
            if not ok:
                say("")
                say("[X] 冒烟测试失败：%s" % reason)
                say("[*] 正在自动回滚官方原版 ...")
                kill_app(15)
                if rollback_swap(asar_path, swap_state):
                    say("[OK] 已自动还原官方原版（未被汉化影响）")
                    if exe:
                        start_app(exe)
                        say("[i] 已重新启动官方原版客户端。")
                else:
                    say("[!] 自动回滚失败！请运行「还原官方原版.bat」。")
                say("[i] 这说明当前客户端版本与汉化补丁不兼容。请把日志发给我：")
                say("    " + (_LOG_PATH or "(无日志)"))
                die("汉化未生效，已回滚，客户端保持可用。", 3)
        else:
            if args.no_smoke:
                say("[!] 已跳过冒烟测试（--no-smoke）")
            else:
                say("[i] 非 Windows 平台跳过冒烟测试")

        finalize_swap(swap_state)
        swap_state = None
        save_state(app_version, dsha, sha256(asar_path))
        if task_installed():
            try:
                write_autorepair_entry()
                say("[OK] 已刷新开机自动修复项（指向当前安装目录）")
            except Exception as e:
                say("[!] 刷新开机自动修复项失败: %s" % e)
        say("")
        say("[DONE] 汉化完成，客户端版本 %s。" % (app_version or "未知"))
    except SystemExit:
        raise
    except Exception as e:
        if swap_state:
            say("[!] 安装过程出错，正在回滚: %s" % e)
            rollback_swap(asar_path, swap_state)
        raise
    finally:
        try:
            shutil.rmtree(build_dir, ignore_errors=True)
        except Exception:
            pass

    if offline:
        launch_after = False
    if launch_after is None:
        launch_after = args.launch or args.auto
    if launch_after or do_smoke:
        if is_app_running():
            say("[i] 客户端已在运行。")
        else:
            if start_app(exe):
                say("[OK] 已启动 Antigravity。")
            else:
                say("[!] 未能自动启动，请手动打开 Antigravity。")
    say("[i] 日志: %s" % (_LOG_PATH or "(无)"))
    return 0


# ---------------------------------------------------------------- 还原
def cmd_restore(args):
    asar_path, resources_dir = detect_paths(args.asar)
    exe = app_exe_path(resources_dir)
    cur_patched = quick_is_patched(asar_path)
    cur_version = safe_asar_version(asar_path)
    say("[*] 使用 app.asar: %s" % asar_path)
    say("[*] 当前客户端版本: %s，汉化状态: %s" % (cur_version or "未知", "已注入" if cur_patched else "官方原版"))

    if not cur_patched:
        say("[OK] 当前 app.asar 就是官方原版（未汉化），无需还原。")
        return 0

    candidates = []
    for label, path in (("安装目录备份", asar_path + ".bak"), ("用户目录备份", BACKUP_ASAR)):
        if not os.path.exists(path):
            continue
        if quick_is_patched(path):
            say("[!] %s 已被汉化污染，忽略：%s" % (label, path))
            continue
        candidates.append((label, path, safe_asar_version(path)))
    if not candidates:
        say("[!] 找不到可用的官方原版备份。")
        say("    解决办法（任选其一）：")
        say("      1. 重新双击「安装汉化插件.bat」——会为当前版本重新生成官方备份；")
        say("      2. 在 Antigravity 里执行「重新安装 / 修复」恢复官方文件。")
        die("没有可用备份，未做任何改动。", 4)

    matching = [c for c in candidates if c[2] and c[2] == cur_version]
    chosen = None
    if matching:
        chosen = matching[0]
    else:
        detail = "，".join("%s=%s" % (c[0], c[2] or "未知") for c in candidates)
        if args.force:
            chosen = candidates[0]
            say("[!] 备份版本与当前客户端不一致（当前 %s，%s），因 --force 强制使用「%s」。"
                % (cur_version or "未知", detail, chosen[0]))
        else:
            say("[X] 备份版本与当前客户端不一致：当前 %s，%s" % (cur_version or "未知", detail))
            say("    旧版本的 app.asar 还原到新客户端会导致客户端打不开。")
            say("    建议：先运行「安装汉化插件.bat」为当前版本生成官方备份，再执行还原。")
            die("版本不匹配，已拒绝还原（可用 --force 强制，但不推荐）。", 4)

    if not kill_app():
        die("Antigravity 正在运行且无法关闭，请手动退出后重试。")
    say("[*] 正在用「%s」还原 ..." % chosen[0])
    stage = asar_path + ".agzh_restore"
    shutil.copy2(chosen[1], stage)
    os.replace(stage, asar_path)
    try:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    except Exception:
        pass
    say("[OK] 已还原官方原版（SHA256: %s）" % sha256(asar_path))
    say("[OK] 汉化已移除，请手动启动 Antigravity。")
    return 0


# ---------------------------------------------------------------- 状态
def cmd_status(args):
    asar_path, resources_dir = detect_paths(args.asar)
    exe = app_exe_path(resources_dir)
    say("安装器版本: %s" % toolkit_version())
    say("客户端: %s" % (exe or "未找到"))
    say("asar 路径: %s" % asar_path)
    if not os.path.exists(asar_path):
        say("状态: app.asar 不存在")
        return 0
    patched = quick_is_patched(asar_path)
    try:
        cur_version = safe_asar_version(asar_path)
    except Exception:
        cur_version = ""
    say("客户端版本: %s" % (cur_version or "未知"))
    say("大小: %d bytes" % os.path.getsize(asar_path))
    say("SHA256: %s" % sha256(asar_path))
    say("汉化: %s" % ("已注入" if patched else "未注入（官方原版）"))
    say("运行中: %s" % ("是" if is_app_running() else "否"))

    state = load_state()
    if state:
        say("状态文件: 版本 %s，词典 %s，注入于 %s" % (
            state.get("app_version", "?"), str(state.get("dict_sha256", ""))[:12],
            state.get("injected_at", "?")))

    bak = asar_path + ".bak"
    if os.path.exists(bak):
        say("备份(安装目录): 存在，版本 %s" % (safe_asar_version(bak) or "未知"))
    else:
        say("备份(安装目录): 无（客户端更新通常会清掉）")
    if os.path.exists(BACKUP_ASAR):
        meta = read_meta()
        say("备份(用户目录): 存在，版本 %s，保存于 %s" % (
            meta.get("app_version") or safe_asar_version(BACKUP_ASAR) or "未知",
            meta.get("saved_at", "")))
    else:
        say("备份(用户目录): 无")
    try:
        n = len(load_dictionary())
        say("词典: %d 条（%s）" % (n, dictionary_sha(load_dictionary())[:12]))
    except SystemExit:
        say("词典: 读取失败")
    say("开机自动修复: %s" % ("已注册" if task_installed() else "未注册"))
    return 0


def _read_autorepair_value():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, REG_VALUE_NAME)
            return val
    except Exception:
        return ""


def task_installed():
    if sys.platform != "win32":
        return False
    return bool(_read_autorepair_value())


def _python_for_startup():
    """优先用插件包自带的 pythonw.exe（无黑框），否则退回当前解释器。"""
    cands = [os.path.join(HERE, "runtime", "pythonw.exe"),
             os.path.join(HERE, "runtime", "python.exe")]
    for c in cands:
        if os.path.exists(c):
            return c
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        w = os.path.join(os.path.dirname(exe), "pythonw.exe")
        if os.path.exists(w):
            return w
    return exe


def write_autorepair_entry():
    import winreg
    python = _python_for_startup()
    script = os.path.join(HERE, "install.py")
    command = '"%s" "%s" --auto-silent' % (python, script)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, REG_VALUE_NAME, 0, winreg.REG_SZ, command)
    # 清理旧方案（启动文件夹 .bat / 计划任务）残留
    try:
        if os.path.exists(LEGACY_STARTUP_FILE):
            os.remove(LEGACY_STARTUP_FILE)
    except Exception:
        pass
    try:
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
                       capture_output=True)
    except Exception:
        pass
    return command


def cmd_install_task(args):
    if sys.platform != "win32":
        die("仅 Windows 支持开机自动修复。")
    try:
        command = write_autorepair_entry()
    except Exception as e:
        die("注册失败: %s" % e)
    say("[OK] 已注册登录时自动修复（HKCU 注册表 Run 项）：%s" % REG_VALUE_NAME)
    say("    命令: %s" % command)
    say("    之后每次登录系统会自动检查；客户端更新导致汉化消失时会自动重装。")
    say("    注意：请不要移动或删除本插件目录，否则自动修复会失效。")
    return 0


def cmd_remove_task(args):
    if sys.platform != "win32":
        die("仅 Windows 支持开机自动修复。")
    removed = False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, REG_VALUE_NAME)
            removed = True
    except FileNotFoundError:
        pass
    except OSError:
        pass
    try:
        if os.path.exists(LEGACY_STARTUP_FILE):
            os.remove(LEGACY_STARTUP_FILE)
            removed = True
    except Exception:
        pass
    try:
        r = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], capture_output=True)
        if r.returncode == 0:
            removed = True
    except Exception:
        pass
    if removed:
        say("[OK] 已取消登录时自动修复。")
    else:
        say("[!] 之前没有注册自动修复，无需取消。")
    return 0


# ---------------------------------------------------------------- 智能模式
def cmd_auto(args, silent=False):
    asar_path, resources_dir = detect_paths(args.asar)
    exe = app_exe_path(resources_dir)
    if is_app_running():
        if silent:
            say("[i] 客户端正在运行，自动修复跳过。")
            return 0
        say("[i] 客户端已在运行。")
        if exe:
            start_app(exe)
        return 0
    if not os.path.exists(asar_path):
        die("找不到 app.asar，请先安装 Antigravity。")

    dict_ = load_dictionary()
    dsha = dictionary_sha(dict_)
    state = load_state()
    if quick_is_patched(asar_path):
        ver = safe_asar_version(asar_path)
        if state.get("dict_sha256") == dsha and state.get("app_version") == ver:
            say("[OK] 当前已是最新汉化（客户端 %s），直接启动。" % (ver or "未知"))
            if not silent:
                start_app(exe)
            return 0
        say("[*] 汉化版本或词典有更新，重新注入 ...")
    else:
        say("[*] 检测到客户端未汉化（可能是刚自动更新过），开始注入 ...")

    if silent:
        args.no_smoke = True
        args.launch = False
        return cmd_install(args, launch_after=False)
    args.launch = True
    return cmd_install(args, launch_after=True)


def cmd_create_shortcut(args):
    if sys.platform != "win32":
        die("仅 Windows 支持创建桌面快捷方式。")
    launcher = None
    for name in ("汉化并启动.bat", "launch-windows.bat"):
        cand = os.path.join(HERE, name)
        if os.path.exists(cand):
            launcher = cand
            break
    if not launcher:
        die("找不到「汉化并启动.bat」，请确认插件包文件完整。")
    ps = (
        "$ErrorActionPreference = 'Stop'\n"
        "$desktop = [Environment]::GetFolderPath('Desktop')\n"
        "$path = Join-Path $desktop 'Antigravity 汉化版.lnk'\n"
        "$ws = New-Object -ComObject WScript.Shell\n"
        "$lnk = $ws.CreateShortcut($path)\n"
        "$lnk.TargetPath = '%TARGET%'\n"
        "$lnk.WorkingDirectory = '%WORKDIR%'\n"
        "$lnk.Description = 'Antigravity 汉化版（自动重新汉化后启动）'\n"
        "$lnk.IconLocation = '%ICON%'\n"
        "$lnk.Save()\n"
        "Write-Output $path\n"
    )
    target = launcher
    workdir = HERE
    icon = app_exe_path() or ""
    content = ps.replace("%TARGET%", target.replace("'", "''")) \
                .replace("%WORKDIR%", workdir.replace("'", "''")) \
                .replace("%ICON%", (icon.replace("'", "''") + ",0") if icon else "")
    ps1 = os.path.join(tempfile.gettempdir(), "agy_zh_shortcut.ps1")
    with open(ps1, "w", encoding="utf-8-sig") as f:
        f.write(content)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", ps1],
                           capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if r.returncode != 0:
            die("创建快捷方式失败：%s %s" % ((r.stdout or "").strip(), (r.stderr or "").strip()))
        say("[OK] 已创建桌面快捷方式：Antigravity 汉化版")
        say("    指向：%s" % launcher)
        say("    以后从桌面这个快捷方式启动，客户端更新后会自动重新汉化。")
    finally:
        try:
            os.remove(ps1)
        except Exception:
            pass
    return 0


def main():
    setup_log()
    ap = argparse.ArgumentParser(description="Antigravity 中文汉化安装器 v%s（零依赖）" % toolkit_version())
    ap.add_argument("--restore", action="store_true", help="还原官方原版（会校验版本）")
    ap.add_argument("--status", action="store_true", help="查看汉化状态")
    ap.add_argument("--auto", action="store_true", help="智能模式：需要时重新汉化，然后启动")
    ap.add_argument("--auto-silent", action="store_true", help="智能模式：需要时重新汉化，不启动（开机任务用）")
    ap.add_argument("--launch", action="store_true", help="完成安装后启动客户端")
    ap.add_argument("--no-smoke", action="store_true", help="跳过安装后的启动冒烟测试（不推荐）")
    ap.add_argument("--force", action="store_true", help="还原时允许使用版本不匹配的备份（不推荐）")
    ap.add_argument("--install-task", action="store_true", help="注册登录时自动修复（HKCU 注册表 Run 项）")
    ap.add_argument("--remove-task", action="store_true", help="取消登录时自动修复")
    ap.add_argument("--create-shortcut", action="store_true", help="创建「Antigravity 汉化版」桌面快捷方式")
    ap.add_argument("--asar", default=None, help="手动指定 app.asar 路径")
    ap.add_argument("--version", action="store_true", help="显示版本")
    args = ap.parse_args()

    if args.version:
        say("Antigravity 汉化安装器 v%s" % toolkit_version())
        return
    if args.status:
        sys.exit(cmd_status(args))
    if args.restore:
        sys.exit(cmd_restore(args))
    if args.install_task:
        sys.exit(cmd_install_task(args))
    if args.remove_task:
        sys.exit(cmd_remove_task(args))
    if args.create_shortcut:
        sys.exit(cmd_create_shortcut(args))
    if args.auto_silent:
        sys.exit(cmd_auto(args, silent=True))
    if args.auto:
        sys.exit(cmd_auto(args, silent=False))
    sys.exit(cmd_install(args))


if __name__ == "__main__":
    main()

(function() {
  const dictionary = {
    "Allow": "允许",
    "Deny": "拒绝",
    "Reason": "申请原因",
    "Run Command": "运行命令",
    "Run command": "运行命令",
    "Terminal Command": "终端命令",
    "CommandLine": "命令行",
    "Command Line": "命令行",
    "Execute": "执行",
    "Approved": "已批准",
    "Pending approval": "等待批准",
    "Task ID": "任务 ID",
    "Working Directory": "工作目录",
    "Cancel": "取消",
    "Close": "关闭",
    "Confirm": "确认",
    "Submit": "提交",
    "Skip": "跳过",
    "Requesting permission": "正在请求权限",
    "Insufficient permissions": "权限不足",
    "Permission requested": "已请求权限",
    "Target": "目标",
    "Action": "操作",
    "Grant Permission": "授予权限",
    "Deny Permission": "拒绝权限",
    "Always Allow": "总是允许",
    "Always Deny": "总是拒绝",
    "Always allow for this session": "在此会话中始终允许",
    "Always deny for this session": "在此会话中始终拒绝",
    "Run in background": "后台运行",
    "Keep running in background": "保持后台运行",
    "Execution output": "执行输出",
    "Error executing command": "执行命令时出错",
    "Command completed successfully": "命令执行成功",
    "The command failed with exit code": "命令执行失败，退出代码为",
    "WaitMsBeforeAsync": "异步等待时间（毫秒）",
    "This command is running asynchronously in the background.": "该命令正在后台异步运行。",
    "View logs": "查看日志",
    "Clear logs": "清除日志",
    "Kill task": "终止任务",
    "Command history": "命令历史记录",
    "Operating System": "操作系统",
    "Shell": "终端 Shell",
    "The actual command will NOT execute until you approve it": "在您批准之前，该命令不会实际执行",
    "This tool is proposing to run a command on your behalf": "此工具申请代表您运行以下命令",
    "Ask Permission": "请求授权",
    "File": "文件",
    "Edit": "编辑",
    "View": "视图",
    "Selection": "选择",
    "Find": "查找",
    "Help": "帮助",
    "Docs": "文档",
    "Docs & API Reference": "文档与 API 参考",
    "Toggle Developer Tools": "开发者工具",
    "New Window": "新窗口",
    "Quit": "退出",
    "Confirm Quit": "确认退出",
    "Are you sure you want to quit?": "您确定要退出吗？",
    "There may be agents or background tasks running.": "可能还有智能体或后台任务正在运行。",
    "Welcome to the new Antigravity!": "欢迎使用全新 Antigravity！",
    "Antigravity has been redesigned to put agents first with new capabilities. If you'd still like a code editor, you can download it as a separate app named": "Antigravity 已经重构为以智能体为核心的全新平台。如果您仍需要代码编辑器，可以将其作为名为以下的独立应用下载：",
    "Antigravity IDE": "Antigravity IDE 编辑器",
    "Download the Antigravity IDE": "下载 Antigravity IDE",
    "Explore the new Antigravity": "探索全新 Antigravity",
    "Setting up…": "正在设置...",
    "Agent": "智能体",
    "Agents": "智能体",
    "Subagent": "子智能体",
    "Subagents": "子智能体",
    "Task": "任务",
    "Tasks": "任务",
    "Workspace": "工作区",
    "Workspaces": "工作区",
    "Command": "命令",
    "Run": "运行",
    "Settings": "设置",
    "Model": "模型",
    "Stop": "停止",
    "Approve": "批准",
    "Reject": "拒绝",
    "Terminal": "终端",
    "Output": "输出",
    "Codebase": "代码库",
    "Error": "错误",
    "Success": "成功",
    "Pending": "等待中",
    "Running": "运行中",
    "Completed": "已完成",
    "Failed": "已失败",
    "Branch": "分支",
    "Merge": "合并",
    "Conflict": "冲突",
    "Generate Image": "生成图像",
    "Web Search": "网页搜索",
    "Grep Search": "全局搜索",
    "Active Agents": "活跃智能体",
    "No agents running": "没有运行中的智能体",
    "active workspace": "活动工作区",
    "Active Workspace": "活动工作区",
    "Search": "搜索",
    "Search...": "搜索...",
    "Type a command...": "输入命令...",
    "Settings & Preferences": "设置与偏好",
    "General": "通用",
    "Themes": "主题",
    "Language": "语言",
    "Model Selection": "模型选择",
    "Advanced": "高级",
    "Developer": "开发者",
    "Save": "保存",
    "Status": "状态",
    "Progress": "进度",
    "Logs": "日志",
    "Console": "控制台",
    "Running task...": "任务运行中...",
    "Task completed successfully": "任务成功完成",
    "An error occurred": "发生错误",
    "Connecting to Language Server...": "正在连接语言服务器...",
    "Language Server": "语言服务器",
    "Connected": "已连接",
    "Disconnected": "已断开",
    "Select a folder": "选择文件夹",
    "Open Folder": "打开文件夹",
    "Create New Project": "创建新项目",
    "Antigravity": "Antigravity",
    "Antigravity 2.0": "Antigravity 2.0",
    "Google DeepMind": "Google DeepMind",
    "Advanced Agentic Coding": "高级智能体编码",
    "Welcome to Antigravity": "欢迎使用 Antigravity",
    "Get Started": "开始使用",
    "Create an agent to get started": "创建一个智能体以开始",
    "New Agent": "新建智能体",
    "Agent Name": "智能体名称",
    "System Prompt": "系统提示词",
    "Description": "描述",
    "Capabilities": "能力",
    "Write Files": "写入文件",
    "Run Commands": "运行命令",
    "Web Browsing": "网页浏览",
    "Define Subagents": "定义子智能体",
    "Call MCP Tools": "调用 MCP 工具",
    "Inherit Workspace": "继承工作区",
    "Branch Workspace": "分支隔离工作区",
    "Share Workspace": "共享工作区",
    "timer": "定时器",
    "Timers": "定时器",
    "Cron Jobs": "计划任务",
    "Schedule": "调度",
    "Directory analysis": "目录分析",
    "Web search": "网页搜索",
    "File edit": "文件编辑",
    "Command execution": "命令执行",
    "Semantic search": "语义搜索",
    "Permissions": "权限",
    "Configure global allowed and denied resource permissions. Learn more.": "配置全局允许与拒绝的资源访问权限。了解更多。",
    "Configure global allowed and denied resource permissions.": "配置全局允许与拒绝的资源访问权限。",
    "Learn more.": "了解更多。",
    "Learn more": "了解更多",
    "Project-Specific Settings": "项目专属设置",
    "Project-Specific": "项目专属",
    "Modify scoped permissions, folders, and Agent settings like Sandbox and Terminal command execution.": "修改项目专属访问权限、工作文件夹以及智能体设置（例如沙箱和终端命令执行）。",
    "Modify scoped permissions, folders, and Agent settings": "修改项目专属访问权限、工作文件夹以及智能体设置",
    "like Sandbox and Terminal command execution.": "例如沙箱与终端命令执行。",
    "Go to Projects": "转到项目",
    "File Permissions": "文件权限",
    "File Access Rules": "文件访问规则",
    "Configure allowed and denied paths for file reads and writes.": "配置文件读写的允许与拒绝路径。",
    "Network Permissions": "网络权限",
    "Network Access Rules": "网络访问规则",
    "Configure allowed and denied URLs for reading.": "配置允许或禁止读取的 URL。",
    "Terminal & Tooling Permissions": "终端和工具权限",
    "Terminal Commands": "终端命令",
    "Configure allowed terminal commands.": "配置允许执行的终端命令。",
    "Commands Outside Sandbox": "沙箱外命令",
    "Configure allowed commands outside the sandbox.": "配置允许在沙箱外执行的终端命令。",
    "MCP Tools": "MCP 工具",
    "Configure external tools via Model Context Protocol.": "通过模型上下文协议 (MCP) 配置外部工具。",
    "Global": "全局",
    "Sandbox": "沙箱",
    "Sandbox enabled": "沙箱已启用",
    "Sandbox disabled": "沙箱已禁用",
    "Allowed": "已允许",
    "Denied": "已拒绝",
    "Paths": "路径",
    "URLs": "URL",
    "Tools": "工具",
    "Appearance": "外观",
    "Configure the Agent's visual theme and display preferences.": "配置智能体的视觉主题与显示偏好。",
    "Chat Settings": "对话设置",
    "Verbose Agent Chat": "显示智能体详细输出",
    "Display and preserve intermediate thinking steps": "显示并保留智能体中间思考过程",
    "Choose light, dark, or inherit system settings.": "选择浅色、深色，或继承系统设置。",
    "Dark": "深色",
    "Light": "浅色",
    "Light Theme": "浅色主题",
    "Preset": "预设",
    "Default Light": "默认浅色",
    "Background": "背景色",
    "Foreground": "前景色",
    "Accent": "强调色",
    "Dark Theme": "深色主题",
    "Default Dark": "默认深色",
    "Customizations": "自定义",
    "Configure default behaviors, skills, and MCP servers.": "配置默认行为、技能以及 MCP 服务器。",
    "Token Usage": "Token 用量",
    "The breakdown below shows token usage from customizations like skills, rules, and MCP. If the budget is exceeded, large customizations will be truncated automatically.": "以下详情展示了来自技能、规则和 MCP 等自定义扩展的 Token 使用情况。如果额度超限，大型自定义内容将被自动截断。",
    "of the customization budget is available.": "的自定义额度可用。",
    "100.0% of the customization budget is available.": "100.0% 的自定义额度可用。",
    "No customizations found for this workspace.": "未找到此工作区的自定义扩展。",
    "Installed MCP Servers": "已安装的 MCP 服务器",
    "No MCP Servers": "无已安装的 MCP 服务器",
    "You currently don't have any MCP Servers installed.": "您当前未安装任何 MCP 服务器。",
    "Add an MCP server above": "在上方添加一个 MCP 服务器",
    "Build With Google Plugins": "使用 Google 插件构建",
    "Account": "账号",
    "Manage your plan, credentials, and general preferences.": "管理您的套餐、凭据与常规偏好。",
    "Enable Telemetry": "启用遥测",
    "When toggled on, Antigravity collects usage data to help Google enhance performance and features.": "开启后，Antigravity 会收集使用数据，以帮助 Google 持续改进性能和功能。",
    "Marketing Emails": "营销电子邮件",
    "Receive product updates, tips, and promotions from Google Antigravity via email.": "通过电子邮件接收来自 Google Antigravity 的产品更新、技巧与促销信息。",
    "Your Plan:": "您的套餐：",
    "Your Plan: Google AI Pro": "您的套餐：Google AI Pro",
    "You can upgrade to a Google AI Ultra plan to receive the highest rate limits.": "您可以升级到 Google AI Ultra 套餐，获得最高的使用限额。",
    "Email": "电子邮件",
    "Browser Settings": "浏览器设置",
    "Configure the browser subagent. It requires Google Chrome to be installed. The browser subagent can be invoked by typing /browser in the conversation input box.": "配置浏览器子智能体。这需要安装 Google Chrome。可以在对话输入框中输入 /browser 来调用浏览器子智能体。",
    "Configure the browser subagent. It requires Google Chrome to be installed. The browser subagent can be invoked by typing": "配置浏览器子智能体。这需要安装 Google Chrome。可以通过输入",
    "in the conversation input box.": "在对话输入框中调用该子智能体。",
    "Browser Javascript Execution Policy": "浏览器 JavaScript 执行策略",
    "Controls whether the agent can run custom JavaScript to automate complex browser actions.": "控制智能体是否可以运行自定义 JavaScript 以自动化复杂的浏览器操作。",
    "Request Review": "请求审查",
    "Disabled": "已禁用",
    "Block all browser JavaScript execution.": "阻止所有浏览器 JavaScript 执行。",
    "Prompt for approval before running browser scripts.": "运行浏览器脚本前请求批准。",
    "Allow full browser script execution without prompting.": "允许完整浏览器脚本执行，无需提示。",
    "Actuation Permissions": "动作执行权限",
    "Browser Actuation Rules": "浏览器操作控制规则",
    "Configure allowed and denied URLs for browser actuation.": "配置允许或禁止浏览器执行动作的 URL 列表。",
    "App Settings": "应用设置",
    "Prevent Sleep": "防止计算机休眠",
    "Prevent the computer from sleeping while the app is running.": "在应用运行时防止计算机进入休眠状态。",
    "Keep In Menu Bar": "常驻系统托盘",
    "The app will be accessible from the menu bar and will keep running in the background when all windows are closed.": "关闭所有窗口后，应用将常驻菜单栏并在后台保持运行。",
    "Notifications": "通知",
    "Notification Settings": "通知设置",
    "To modify notification settings, open your operating system's system preferences.": "如需修改通知设置，请打开您操作系统的系统偏好设置。",
    "Agent Settings": "智能体设置",
    "Security Preset": "安全预设",
    "Choose a predefined security preset for the agent. This controls terminal auto-execution policy, and file access policy.": "为智能体选择预定义的安全预设。这将控制终端自动执行策略和文件访问策略。",
    "Choose a predefined security preset for the agent.": "为智能体选择预定义的安全预设。",
    "This controls terminal auto-execution policy, and file access policy.": "这将控制终端自动执行策略和文件访问策略。",
    "Learn more about Default": "了解关于默认预设的更多信息",
    "Default": "默认",
    "Agent Behavior": "智能体行为",
    "Artifact Review Policy": "工件审查策略",
    "Specifies agent's behavior when asking for review on artifacts, which are documents it creates to enable a richer conversation experience.": "指定智能体在请求审查工件时的行为。工件是其为提供更丰富的对话体验而创建的文档。",
    "Always Ask": "始终询问",
    "Local Permissions": "项目专属权限",
    "Inherits from global settings. Local permissions have higher priority.": "继承自全局设置。项目专属权限具有更高的优先级。",
    "Inherits from global settings.": "继承自全局设置。",
    "Local permissions have higher priority.": "项目专属权限具有更高的优先级。",
    "Danger Zone": "危险区域",
    "Delete Project": "删除项目",
    "Permanently delete this project and all of its conversations.": "永久删除当前项目及其包含的所有历史对话。",
    "Custom": "自定义",
    "Outside of folders file access policy": "文件夹外文件访问策略",
    "Configures how the agent tries to access files outside of its working folders.": "配置智能体如何尝试访问其工作文件夹外部的文件。",
    "Terminal command Auto execution": "终端命令自动执行",
    "Controls whether terminal commands require your approval before running.": "控制终端命令在运行前是否需要您批准。",
    "Require Review": "需要审查",
    "Add Context": "添加上下文",
    "Media": "媒体",
    "Mentions": "提及",
    "Actions": "操作",
    "Browser": "浏览器",
    "Worktree": "工作树",
    "Projects": "项目",
    "Review Changes": "审查更改",
    "Ask anything, @ to mention, / for actions": "输入任何问题，输入 @ 提及，/ 触发操作",
    "Ask anything, @to mention, /for actions": "输入任何问题，输入 @ 提及，/ 触发操作",
    "Ask anything, @ to mention, / for commands": "输入任何问题，输入 @ 提及，/ 触发命令",
    "Ask anything, @to mention, /for commands": "输入任何问题，输入 @ 提及，/ 触发命令",
    "Overview": "概览",
    "Artifacts": "工件",
    "Conversations": "对话",
    "Agent settings and permissions for conversations outside of projects.": "项目外部对话的智能体设置和权限配置。",
    "Not in Project": "不在项目中",
    "Manage project folders, agent settings, and permissions.": "管理项目文件夹、智能体设置和专属权限。",
    "Requires manual review for all terminal commands and file accesses outside of the working folders.": "运行终端命令以及访问工作区外的文件时，均需手动人工审查。",
    "Full Machine": "完整本机访问",
    "All terminal commands require review. The agent can read or write to any file in the machine.": "所有终端命令均需审查，智能体可读写本机上的任意文件。",
    "Unrestricted": "无限制模式",
    "Disables all safety barriers for maximal iteration velocity.": "禁用所有安全屏障以获得极致的迭代效率。",
    "Manually customize individual settings.": "手动自定义各项具体设置。",
    "Always Proceed": "始终继续",
    "One Light": "One 浅色",
    "Solarized Light": "Solarized 浅色",
    "One Dark Pro": "One 深色 Pro",
    "Configure AI models and view your quota.": "配置 AI 模型并查看您的配额。",
    "Refresh": "刷新",
    "Model Credits": "模型额度",
    "Enable AI Credit Overages": "启用 AI 额度超量使用",
    "When toggled on, Antigravity will use your AI credits to fulfill model requests once you're out of model quota. Antigravity will always use your model quota first before using AI credits.": "开启后，当您的模型配额耗尽时，Antigravity 将使用您的 AI 额度来满足模型请求。Antigravity 始终会先使用您的模型配额，然后再使用 AI 额度。",
    "Model Quota": "模型配额",
    "View your available model quota and AI credits. Model quota refreshes periodically based on your plan. Enable AI Credit Overages to continue using models when your quota is exhausted.": "查看您可用的模型配额和 AI 额度。模型配额会根据您的套餐定期刷新。启用 AI 额度超量使用，以便在配额耗尽时继续使用模型。",
    "Shortcuts": "快捷键",
    "Keyboard shortcuts for quick navigation and control.": "用于快速导航与控制的键盘快捷键。",
    "Recommended": "推荐",
    "Open Conversation Picker": "打开对话选择器",
    "Open File Search": "打开文件搜索",
    "Focus Input": "聚焦输入框",
    "New Conversation": "新建对话",
    "Navigation": "导航",
    "Go Back": "后退",
    "Go Forward": "前进",
    "File Picker": "文件选择器",
    "Scheduled Tasks": "计划任务",
    "Select Previous Conversation": "选择上一个对话",
    "Select Next Conversation": "选择下一个对话",
    "Open Settings": "打开设置",
    "Conversation": "对话",
    "Conversation History": "历史对话",
    "Conversation history": "历史对话",
    "Toggle Model Selector": "切换模型选择器",
    "Toggle Voice Recording": "切换录音",
    "Find in Pane": "在窗格中查找",
    "Layout Controls": "布局控制",
    "Toggle Sidebar": "切换侧边栏",
    "Toggle Auxiliary Pane": "切换辅助窗格",
    "Zoom In": "放大",
    "Zoom Out": "缩小",
    "Reset Zoom": "重置缩放",
    "Provide Feedback": "提供反馈",
    "Feedback Type": "反馈类型",
    "Bug Report": "Bug 报告",
    "Feature Request": "功能请求",
    "Auth and Billing": "账号与计费",
    "General Feedback": "常规反馈",
    "Please describe the feature you'd like to see. The more detailed the requirements, the easier it will be for our team to incorporate your ideas. Some helpful information includes:": "请描述您希望获得的新功能。需求描述越详尽，我们的团队就越容易采纳您的想法。以下是一些建议提供的信息：",
    "What is missing in your workflow": "您的工作流中缺少了什么",
    "What you would like to see to address this gap in your workflow": "您希望通过什么功能来解决这一需求",
    "How this feature would help you and other users": "此功能如何帮助您和其他用户",
    "Describe the feature you would like to see...": "请描述您希望获得的新功能...",
    "Attach a screenshot (optional)": "添加屏幕截图（可选）",
    "Attach Antigravity server logs": "附带 Antigravity 服务器日志",
    "Send feedback as": "发送反馈身份",
    "We recommend attaching logs. Attaching logs will help the Antigravity team act on and prioritize your feedback.": "我们建议附带日志。这将有助于 Antigravity 团队更快速、更有针对性地处理您的问题。",
    "Checking for Updates...": "正在检查更新...",
    "Downloading Update...": "正在下载更新...",
    "Restart to Update": "重启以应用更新",
    "Check for Updates": "检查更新",
    "No updates available": "当前已是最新版本",
    "Update available": "发现新版本",
    "Downloading...": "正在下载...",
    "Update downloaded": "更新已下载完成",
    "Error checking for updates": "检查更新失败"
  };

  const coreWords = {
    "create": "创建", "delete": "删除", "new": "新建", "edit": "编辑", "save": "保存", "cancel": "取消", "confirm": "确认",
    "close": "关闭", "open": "打开", "stop": "停止", "start": "启动", "run": "运行", "add": "添加", "remove": "移除",
    "update": "更新", "select": "选择", "clear": "清除", "search": "搜索", "find": "查找", "view": "查看", "show": "显示", "hide": "隐藏",
    "agent": "智能体", "agents": "智能体", "subagent": "子智能体", "subagents": "子智能体", "task": "任务", "tasks": "任务",
    "workspace": "工作区", "workspaces": "工作区", "directory": "目录", "folder": "文件夹", "file": "文件", "files": "文件",
    "command": "命令", "commands": "命令", "terminal": "终端", "console": "控制台", "output": "输出", "input": "输入",
    "log": "日志", "logs": "日志", "setting": "设置", "settings": "设置", "preference": "偏好", "preferences": "偏好",
    "theme": "主题", "themes": "主题", "model": "模型", "models": "模型", "capability": "能力", "capabilities": "能力",
    "running": "运行中", "completed": "已完成", "failed": "已失败", "pending": "等待中", "success": "成功", "error": "错误",
    "system": "系统", "prompt": "提示词", "instructions": "指令", "description": "描述", "name": "名称", "version": "版本",
    "active": "活跃", "background": "后台", "parent": "父级", "child": "子级", "branch": "分支", "share": "共享", "inherit": "继承",
    "original": "原始", "backup": "备份", "duration": "持续时间", "seconds": "秒", "timer": "定时器", "timers": "定时器",
    "schedule": "调度", "cron": "定时任务", "tools": "工具", "tool": "工具", "execute": "执行", "execution": "执行", "plan": "计划",
    "chat": "聊天", "message": "消息", "messages": "消息", "history": "历史", "clear history": "清除历史",
    "changed": "已更改", "review": "审查", "reviewing": "审查中", "reviewed": "已审查",
    "edited": "编辑了", "canceled": "已取消",
    "explore": "探索", "change": "更改", "changes": "更改",
    "turn": "回合", "turns": "回合"
  };


  

  __DICT_ITEMS__
  // 将 extraDict 合并到 dictionary（从零注入时必需）
  if (typeof extraDict !== 'undefined') {
    for (const ek in extraDict) {
      if (!(ek in dictionary) && !(ek in coreWords)) dictionary[ek] = extraDict[ek];
    }
  }
  // ===== 索引与缓存（v4 性能优化）=====
  // lowerLookup: 小写 key -> 译文（O(1) 精确匹配）
  // tokenLookup: 单个单词 key -> 译文（短文本逐词兜底）
  let combinedDict, exactLookup, lowerLookup, tokenLookup;
  const translationCache = new Map();
  const CACHE_LIMIT = 8000;
  const CACHE_MAX_TEXT = 600;

  function rebuildDict() {
    combinedDict = Object.assign({}, coreWords, dictionary);
    exactLookup = new Map();
    lowerLookup = new Map();
    tokenLookup = new Map();
    for (const k in combinedDict) {
      const v = combinedDict[k];
      exactLookup.set(k, v);
      const lk = k.toLowerCase();
      if (!lowerLookup.has(lk)) lowerLookup.set(lk, v);
      if (!/\s/.test(k) && !tokenLookup.has(lk)) tokenLookup.set(lk, v);
    }
    translationCache.clear();
  }
  rebuildDict();

  function loadExternalDict() {
    try {
      const fs = require('fs');
      const os = require('os');
      const path = require('path');
      const extPath = path.join(os.homedir(), '.antigravity-zh', 'zh-CN.json');
      if (!fs.existsSync(extPath)) return;
      const raw = fs.readFileSync(extPath, 'utf-8');
      const ext = JSON.parse(raw);
      const items = ext.translations || ext;
      let added = 0;
      for (const k in items) {
        if (k.startsWith('__')) continue;
        dictionary[k] = items[k]; // 外部词典覆盖嵌入词典
        added++;
      }
      if (added > 0) {
        rebuildDict();
        console.log('[Antigravity-ZH] 外部词典已加载 ' + added + ' 条，总计 ' + Object.keys(dictionary).length + ' 条');
        // 清缓存后重新排队翻译当前页面（不阻塞主线程）
        setTimeout(function () {
          if (document.body && typeof enqueueNode === 'function') enqueueNode(document.body, true);
        }, 0);
      }
    } catch (e) {
      // sandbox 或权限不足时静默失败，用嵌入词典
    }
  }

  // 监听外部词典文件变化，热重载
  try {
    const fs = require('fs');
    const os = require('os');
    const path = require('path');
    const extPath = path.join(os.homedir(), '.antigravity-zh', 'zh-CN.json');
    if (fs.existsSync(extPath)) {
      fs.watch(extPath, { persistent: false }, function () {
        setTimeout(loadExternalDict, 200); // 防抖：等文件写入完成
      });
    }
  } catch (e) {}

  const escapeRegExp = (str) => {
    const specials = ['[', ']', '(', ')', '{', '}', '*', '+', '?', '.', '^', '$', '|', '\\'];
    return str.split('').map(c => specials.includes(c) ? '\\' + c : c).join('');
  };

  // 时长格式化：1d2h3m4.5s / 1d 2h 3m -> 1 天 2 小时 3 分 4.5 秒
  const fmtDuration = function (d) {
    return d
      .replace(/(\d+(?:\.\d+)?)\s*d/gi, '$1 天')
      .replace(/(\d+(?:\.\d+)?)\s*h/gi, '$1 小时')
      .replace(/(\d+(?:\.\d+)?)\s*m/gi, '$1 分')
      .replace(/(\d+(?:\.\d+)?)\s*s/gi, '$1 秒')
      .replace(/(天|小时|分|秒)\s*(?=\d)/g, '$1 ');
  };
  const MONTH_CN = { jan: '1月', feb: '2月', mar: '3月', apr: '4月', may: '5月', jun: '6月', jul: '7月', aug: '8月', sep: '9月', oct: '10月', nov: '11月', dec: '12月' };
  const meridiem = function (ap) { return ap.toUpperCase() === 'PM' ? '下午' : '上午'; };
  // 动态正则规则（参考社区汉化项目沉淀，整串锚定匹配；在词典精确匹配之后执行）
  const dynamicRules = [
    [/^(\d+)\s*(?:seconds?|secs?)\s+ago$/i, '$1 秒前'],
    [/^(\d+)\s*(?:minutes?|mins?)\s+ago$/i, '$1 分钟前'],
    [/^(\d+)\s*(?:hours?|hrs?)\s+ago$/i, '$1 小时前'],
    [/^(\d+)\s*days?\s+ago$/i, '$1 天前'],
    [/^(\d+)\s*weeks?\s+ago$/i, '$1 周前'],
    [/^(\d+)\s*months?\s+ago$/i, '$1 个月前'],
    [/^(\d+)\s*years?\s+ago$/i, '$1 年前'],
    [/^(\d+)[sS]\s+ago$/, '$1 秒前'],
    [/^(\d+)[mM]\s+ago$/, '$1 分钟前'],
    [/^(\d+)[hH]\s+ago$/, '$1 小时前'],
    [/^(\d+)[dD]\s+ago$/, '$1 天前'],
    [/^\((\d+)\s+subagents?\)$/i, '($1 个子智能体)'],
    [/^(\d+)\s+subagents?$/i, '$1 个子智能体'],
    [/^(\d+)\s+active\s+subagents?$/i, '$1 个运行中的子智能体'],
    [/^(\d+)\s+tasks?\s+running$/i, '$1 个运行中的任务'],
    [/^(\d+)\s+agents?\s+running$/i, '$1 个运行中的智能体'],
    [/^(\d+)\s+active\s+conversations?$/i, '$1 个活跃对话'],
    [/^(\d+)\s+archived\s+conversations?$/i, '$1 个已归档对话'],
    [/^See all\s*\((\d+)\)$/i, '查看全部 ($1)'],
    [/^See all\s+(\d+)$/i, '查看全部 $1 项'],
    [/^Step (\d+) of (\d+)$/i, '第 $1 步（共 $2 步）'],
    [/^Task (\d+) running$/i, '正在运行任务 $1'],
    [/^Created (\d+) files?$/i, '已创建 $1 个文件'],
    [/^Modified (\d+) files?$/i, '已修改 $1 个文件'],
    [/^Ran (\d+) commands?$/i, '已运行 $1 个命令'],
    [/^Thinking for (\d+)s$/i, '已思考 $1 秒'],
    [/^Stopped after (\d+) steps?$/i, '已在 $1 步后停止'],
    [/^You have used some of your weekly limit,?\s*it will fully refresh in (.*?)\.?$/i, '您已消耗了部分每周额度，将在 $1后完全重置刷新。'],
    [/^You have used some of your 5-?hour limit,?\s*it will fully refresh in (.*?)\.?$/i, '您已消耗了部分 5 小时额度，将在 $1后完全重置刷新。'],
    [/^You have hit your 5-?hour limit,?\s*it will refresh in (.*?)\.?$/i, '您已达到 5 小时上限，将在 $1后重置刷新。'],
    [/^You have hit your weekly limit,?\s*it will refresh in (.*?)\.?$/i, '您已达到每周上限，将在 $1后重置刷新。'],
    [/^Your quota for this model is running low\.?$/i, '您在此模型上的剩余配额即将耗尽。'],
    [/^Your quota for this model has run out\.?$/i, '您在此模型上的配额已耗尽。'],
    [/^Your plan's baseline quota will refresh on (.+?)\.?\s*You can upgrade to a Google AI Ultra plan to receive higher rate limits\.?$/i, '您的套餐基础配额将于 $1重置刷新。您可以升级至 Google AI Ultra 以获取更高的请求配额与速率上限。'],
    [/^Your plan's baseline quota will refresh on (.+?)\.?\s*To continue using this model now,?\s*enable AI Credit overages\.?$/i, '您的套餐基础配额将于 $1重置刷新。若要立即继续使用此模型，请启用 AI 额度超量使用。'],
    [/^Your plan's baseline quota will refresh on ([^.。]+)\.?$/i, '您的套餐基础配额将于 $1重置刷新。'],
    [/^(?:Model|Your) quota will refresh on ([^.。]+)\.?$/i, '您的模型配额将于 $1重置刷新。'],
    [/^You need at least (\d+) AI Credits to send messages\.?$/i, '您至少需要 $1 个 AI 额度才能发送消息。'],
    [/^To continue using this model now,?\s*purchase more AI Credits\.?$/i, '若要立即继续使用此模型，请购买更多 AI 额度。'],
    [/^To continue using this model now,?\s*enable AI Credit overages\.?$/i, '若要立即继续使用此模型，请启用 AI 额度超量使用。'],
    [/^To continue using (.+?) now,?\s*purchase more AI Credits\.?$/i, '若要立即继续使用 $1，请购买更多 AI 额度。'],
    [/^To continue using (.+?) now,?\s*enable AI Credit overages\.?$/i, '若要立即继续使用 $1，请启用 AI 额度超量使用。'],
    [/^Available AI Credits:\s*(.+)$/i, '可用 AI 额度：$1'],
    [/^([\d,]+)\s*\/\s*([\d,]+)\s*tokens?\s*\(([\d.]+%)\)$/i, '$1 / $2 个 Token ($3)'],
    [/^\(([\d,]+)\s*tokens?\)\s*([\d.]+%)$/i, '($1 个 Token) $2'],
    [/^\(([\d,]+)\s*tokens?\)$/i, '($1 个 Token)'],
    [/^[Rr]esets? in (\d+)\s*(?:d|days?)[,\s]+(\d+)\s*(?:h|hours?)[,\s]+(\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 天 $2 小时 $3 分钟后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:d|days?)[,\s]+(\d+)\s*(?:h|hours?)\.?$/, '$1 天 $2 小时后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:h|hours?)[,\s]+(\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 小时 $2 分钟后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:m|mins?|minutes?)[,\s]+(\d+)\s*(?:s|secs?|seconds?)\.?$/, '$1 分 $2 秒后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:d|days?)\.?$/, '$1 天后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:h|hours?)\.?$/, '$1 小时后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 分钟后重置'],
    [/^[Rr]esets? in (\d+)\s*(?:s|secs?|seconds?)\.?$/, '$1 秒后重置'],
    [/^[Rr]esets? in less than a minute\.?$/i, '不到 1 分钟后重置'],
    [/^[Rr]esets? in a few seconds\.?$/i, '几秒后重置'],
    [/^[Rr]esets? soon\.?$/i, '即将重置'],
    [/^[Rr]efreshes? in (\d+)\s*(?:d|days?)[,\s]+(\d+)\s*(?:h|hours?)[,\s]+(\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 天 $2 小时 $3 分钟后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:d|days?)[,\s]+(\d+)\s*(?:h|hours?)\.?$/, '$1 天 $2 小时后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:h|hours?)[,\s]+(\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 小时 $2 分钟后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:d|days?)\.?$/, '$1 天后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:h|hours?)\.?$/, '$1 小时后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:m|mins?|minutes?)\.?$/, '$1 分钟后重置刷新'],
    [/^[Rr]efreshes? in (\d+)\s*(?:s|secs?|seconds?)\.?$/, '$1 秒后重置刷新'],
    [/^[Rr]efreshes? soon\.?$/i, '即将重置刷新'],
    [/^Permanently delete (.+?)\s+including\s+(\d+)\s+active\s+conversations?\s*([?.。？])?$/i, function (m, body, n, p) { return '永久删除 ' + body + '，包括其中的 ' + n + ' 个活跃对话' + (p === '?' ? '？' : p === '.' ? '。' : p || ''); }],
    [/^Permanently delete (.+?)\s*([?.。？])?$/, function (m, body, p) { return '永久删除 ' + body + (p === '?' ? '？' : p === '.' ? '。' : p || ''); }],
    [/^Mark all (\d+) conversations as read$/i, '将全部 $1 个对话标记为已读'],
    [/^Mark (\d+) conversations? as read$/i, '将 $1 个对话标记为已读'],
    [/^You have (\d+) conversations in progress\. Updating will interrupt them, and they will automatically resume once the update completes\.$/i, '您当前有 $1 个正在进行的对话。更新将暂时中断这些对话，并在更新完成后自动恢复。'],
    [/^You have (\d+) conversations in progress\. Updating will cancel them and you'll need to manually restart them\.$/i, '您当前有 $1 个正在进行的对话。更新将取消这些对话，更新后您需要手动重新开始。'],
    [/^(Enter|Alt\+Enter|Shift\+Enter|Ctrl\+Enter|Cmd\+Enter)\s+Queues after the turn$/i, '$1 在当前回合结束后排队'],
    [/^(Enter|Alt\+Enter|Shift\+Enter|Ctrl\+Enter|Cmd\+Enter)\s+Sends immediately$/i, '$1 立即发送'],
    [/^(Enter|Alt\+Enter|Shift\+Enter|Ctrl\+Enter|Cmd\+Enter)\s+On empty prompt,\s*sends next in queue$/i, '$1 在输入框为空时发送队列中的下一条消息'],
    [/^Record Audio(\s+Ctrl\+[A-Za-z])?$/i, '录制语音$1'],
    [/^New Terminal(\s+Ctrl\+Shift\+.*)?$/i, '新建终端$1'],
    [/^Add Terminal(\s+Ctrl\+Shift\+.*)?$/i, '添加终端$1'],
    [/^Add Context(\s+.*)?$/i, '添加上下文$1'],
    // --- 插件市场卡片按钮 / 无障碍标签 ---
    [/^Install ([^!?,;:]{1,40})$/i, function (m, name) { return '安装 ' + translateCaptured(name); }],
    [/^Add ([^!?,;:]{1,30})$/i, function (m, name) { return '添加 ' + translateCaptured(name); }],
    [/^Details for (.+)$/i, '$1 详情'],
    [/^Select Project(\s+(?:Ctrl|Cmd|Alt|Shift)\+[\w;:,/+ -]+)?$/i, '选择项目$1'],
    [/^Select Model(\s+(?:Ctrl|Cmd|Alt|Shift)\+[\w;:,/+ -]+)?$/i, '选择模型$1'],
    [/^Cancel\s*\(((?:Ctrl|Cmd|Alt|Shift)\+[\w+-]+)\)$/i, '取消 ($1)'],
    // --- 快捷键设置页动态标签 ---
    [/^Recording shortcut for (.+)\. Press keys to bind, Enter to save, Escape to cancel\.$/i, function (m, action) { return '正在录制「' + translateCaptured(action) + '」的快捷键。按下按键进行绑定，Enter 保存，Escape 取消。'; }],
    [/^Remove shortcut\s+(.+?)\s+for\s+(.+)$/i, function (m, key, action) { return '移除「' + translateCaptured(action) + '」的快捷键 ' + key; }],
    [/^Add shortcut for\s+(.+)$/i, function (m, action) { return '为「' + translateCaptured(action) + '」添加快捷键'; }],
    [/^Shortcut\s+(.+?)\s+for\s+(.+)$/i, function (m, key, action) { return '「' + translateCaptured(action) + '」的快捷键：' + key; }],
    [/^Send [Mm]essage\s+(Enter|Return|Ctrl\+Enter|Cmd\+Enter|↵)$/, '发送消息 $1'],
    [/^Send [Mm]essage\s+\((Enter|Return|Ctrl\+Enter|Cmd\+Enter|↵)\)$/, '发送消息 ($1)'],
    // --- v2.31 新增界面 ---
    [/^Hey there,\s*what should we build today\?$/i, '嗨，今天想构建什么？'],
    [/^Hey\s+(.+?),\s*what should we build today\?$/i, '嗨，$1，今天想构建什么？'],
    [/^Welcome back,\s*(.+?)\.\s*Where should we pick up\?$/i, '欢迎回来，$1。我们从哪里继续？'],
    [/^Welcome back\.\s*Where should we pick up\?$/i, '欢迎回来。我们从哪里继续？'],
    [/^Good to see you,\s*(.+?)\.\s*What's next\?$/i, '很高兴见到你，$1。接下来做什么？'],
    [/^Good to see you\.\s*What's next\?$/i, '很高兴见到你。接下来做什么？'],
    [/^Version\s+([\d.]+)$/i, '版本 $1'],
    [/^Turn\s+(\d+)\s+of\s+(\d+)$/i, '第 $1 轮（共 $2 轮）'],
    [/^(\d+)\s+projects?$/i, '$1 个项目'],
    [/^See\s+(\d+)\s+more$/i, '查看另外 $1 项'],
    [/^Toggle\s+(.+)$/i, '切换 $1'],
    [/^([\d,.]+)% of the customization budget is available\.?$/i, '$1% 的自定义扩展预算可用。'],
    [/^of the customization budget is available\.?$/i, '的自定义扩展预算可用。'],
    [/^Show (\d+) breakdowns?$/i, '显示 $1 项明细'],
    [/^Hide (\d+) breakdowns?$/i, '隐藏 $1 项明细'],
    [/^(\d+) demoted$/i, '$1 项已降级'],
    [/^(\d+) excluded$/i, '$1 项已排除'],
    [/^(\d+)\s+tools?\s+excluded$/i, '已排除 $1 个工具'],
    [/^(\d+)\s+tools?\s+enabled$/i, '已启用 $1 个工具'],
    [/^(\d+)\s+tools?\s+disabled$/i, '已禁用 $1 个工具'],
    [/^(\d+)\s+tools$/i, '$1 个工具'],
    [/^Plugin:\s*(.*)$/i, '插件：$1'],
    [/^Build with (.+) Plugins$/i, 'Build with $1 插件'],
    [/^There are currently no Build with (.+) plugins available\.?$/i, '当前暂无可用的 Build with $1 插件。'],
    [/^Failed to enable plugin (.+)$/i, '启用插件 $1 失败'],
    [/^Failed to update agent:\s*(.+)$/i, '更新智能体失败：$1'],
    [/^Failed to remove agent:\s*(.+)$/i, '移除智能体失败：$1'],
    [/^Failed to remove plugin:\s*(.+)$/i, '移除插件失败：$1'],
    [/^Failed to toggle plugin:\s*(.+)$/i, '切换插件状态失败：$1'],
    [/^Error updating agent:\s*(.+)$/i, '更新智能体出错：$1'],
    [/^Failed to write MCP config:\s*(.+)$/i, '写入 MCP 配置失败：$1'],
    [/^Failed to load skills:\s*(.+)$/i, '加载技能失败：$1'],
    [/^Failed to scan skills config file:\s*(.+)$/i, '扫描技能配置文件失败：$1'],
    [/^Failed to revalidate slash commands:\s*(.*)$/i, '重新验证斜杠命令失败：$1'],
    [/^Failed to add plugin\.?\s*(?:Please try again\.?)?$/i, '添加插件失败。请重试。'],
    [/^Unnamed [Aa]gent (\d+)$/, '未命名智能体 $1'],
    [/^Unnamed [Ss]kill (\d+)$/, '未命名技能 $1'],
    [/^UI Extension (\d+)$/, '界面扩展 $1'],
    [/^Automation (\d+)$/, '自动化任务 $1'],
    [/^Rule (\d+)$/, '规则 $1'],
    [/^Branch ([\w./-]+)$/, '分支 $1'],
    [/^All changes since (.+)$/i, '自 $1 以来的全部更改'],
    [/^(\d+) commits? to push$/i, '$1 个待推送的提交'],
    [/^(\d+) commits? to pull$/i, '$1 个待拉取的提交'],
    [/^(?:All |全部)?scheduled tasks run as (.+?)\.?$/i, '所有计划任务均以 $1 模型运行。'],
    [/^scheduled tasks run as (.+?)\.?$/i, '计划任务均以 $1 模型运行。'],
    [/^(?:All |全部)?plugins run as (.+?)\.?$/i, '所有插件均以 $1 模型运行。'],
    [/^(?:All |全部)?automations run as (.+?)\.?$/i, '所有自动化任务均以 $1 模型运行。'],
    [/^Review permissions for (.+)$/i, '审查 $1 的权限'],
    [/^(.+) needs a few details from you before it can run\.$/i, '$1 运行前需要您补充几项详细信息。'],
    [/^Agents created by (.+) run in a dedicated (?:project|workspace) with its own permissions, which you can change anytime in the (?:project|workspace) settings page\.? On top of those defaults, (.+) requests the access below\.$/i, '由 $1 创建的智能体将在专属工作区中运行并拥有独立权限，您可以随时在设置页面中更改。除默认权限外，$2 还请求以下访问权限。'],
    [/^Agents created by (.+) run in a dedicated (?:project|workspace) with its own permissions, which you can change anytime in the (?:project|workspace) settings page\.?$/i, '由 $1 创建的智能体将在专属工作区中运行并拥有独立权限，您可以随时在设置页面中更改。'],
    [/^On top of those defaults, (.+) requests the access below\.$/i, '除默认权限外，$1 还请求以下访问权限。'],
    [/^Message from (.+)$/i, '来自 $1 的消息'],
    [/^Executing task:\s*(.+)$/i, '正在执行任务：$1'],
    [/^Send feedback as (.+)$/i, '以 $1 身份发送反馈'],
    [/^Models within this group:\s*(.*)$/i, '该分组包含的模型：$1'],
    [/^Select model,\s*current:\s*(.+)$/i, '选择模型，当前：$1'],
    [/^(\d+) models selected$/i, '已选择 $1 个模型'],
    [/^Auth code for (.+)$/i, '$1 的授权码'],
    [/^The (.+) MCP server requires configuration parameters before it can be started\.?$/i, '$1 MCP 服务器需要先配置参数才能启动。'],
    [/^See more in (.+)$/i, '在 $1 中查看更多'],
    [/^See less in (.+)$/i, '在 $1 中收起'],
    [/^(?:More actions|更多操作) for (.+)$/i, '$1 的更多操作'],
    [/^(.+),\s*setup required$/i, '$1（需要配置）'],
    [/^Tool Definition:\s*(.+)$/i, '工具定义：$1'],
    [/^Invocation:\s*(.+)$/i, '调用：$1'],
    [/^Agent permissions preset selector, current:\s*(.+)$/i, '智能体权限预设选择器，当前：$1'],
    [/^Undo to (?:this point|here)\.?$/i, '撤销到此处'],
    [/^Search tasks[.…]*$/i, '搜索任务...'],
    [/^Search conversations[.…]*$/i, '搜索对话...'],
    [/^Enter scheduled task name[.…]*$/i, '输入计划任务名称...'],
    [/^Enter a prompt for the agent to run[.…]*$/i, '输入供智能体执行的提示词...'],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s*[-\u2013\u2014]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})$/i, function (m, mo1, d1, mo2, d2) { return MONTH_CN[mo1.toLowerCase()] + d1 + '日 - ' + MONTH_CN[mo2.toLowerCase()] + d2 + '日'; }],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s*[-\u2013\u2014]\s*(\d{1,2})$/i, function (m, mo, d1, d2) { return MONTH_CN[mo.toLowerCase()] + d1 + '日 - ' + d2 + '日'; }],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(\d{4}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)?$/i, function (m, mo, d, y, t, ap) { return y + '年' + MONTH_CN[mo.toLowerCase()] + d + '日 ' + (ap ? meridiem(ap) + ' ' : '') + t; }],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)?$/i, function (m, mo, d, t, ap) { return MONTH_CN[mo.toLowerCase()] + d + '日 ' + (ap ? meridiem(ap) + ' ' : '') + t; }],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(\d{4})$/i, function (m, mo, d, y) { return y + '年' + MONTH_CN[mo.toLowerCase()] + d + '日'; }],
    [/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})$/i, function (m, mo, d) { return MONTH_CN[mo.toLowerCase()] + d + '日'; }],
    [/^(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)$/i, function (m, t, ap) { return meridiem(ap) + ' ' + t; }],
    // --- 吸收自 Zero-Touch 项目（antigravity-chinese-Zero-Touch） ---
    [/^(\d+)\s*([smhd])\s+ago$/i, function (m, n, u) { return n + ' ' + { s: '秒', m: '分钟', h: '小时', d: '天' }[u.toLowerCase()] + '前'; }],
    [/^Load older messages,\s*showing\s+(\d+)\s+of\s+(\d+)$/i, '加载更早的消息（已显示 $1 / $2）'],
    [/^showing\s+(\d+)\s+of\s+(\d+)$/i, '已显示 $1 / $2'],
    [/^Fold lines\s+(\d+)\s*-\s*(\d+)$/i, '折叠第 $1-$2 行'],
    [/^Run command:\s*(.+)$/i, '执行命令：$1'],
    [/^Remove\s+(.{1,40})$/i, '移除 $1'],
    // --- 吸收自 AntigravityCN 项目 ---
    [/^Thinking\s*\((.+)\)$/i, '正在思考（$1）'],
    [/^(\d+)\s+searches?$/i, '$1 次搜索'],
    [/^(\d+(?:\.\d+)?%?)\s+remaining$/i, '$1 剩余'],
    [/^(\d+)\s+hours?\s+(\d+)\s+minutes?$/i, '$1 小时 $2 分钟'],
    [/^(\d+)\s+minutes?$/i, '$1 分钟'],
    [/^(\d+)\s+hours?$/i, '$1 小时'],
    [/^(\d+)\s+days?$/i, '$1 天'],
    // --- 权限确认弹窗按钮（插入命令后的动态形式）---
    [/^Yes, and always allow '([\s\S]+)' in this conversation$/i, '是，且在此对话中始终允许 \'$1\''],
    [/^Yes, and always allow '([\s\S]+)' in this project$/i, '是，且在此项目中始终允许 \'$1\''],
    [/^Yes, and always allow '([\s\S]+)' when not in a project$/i, '是，且在非项目时始终允许 \'$1\''],
    [/^Yes, and always allow '([\s\S]+)'$/i, '是，且始终允许 \'$1\''],
    [/^Yes, allow '([\s\S]+)' this time$/i, '是，仅允许本次执行 \'$1\''],
    [/^Yes, allow '([\s\S]+)'$/i, '是，允许 \'$1\'']
  ];

  // 动态规则里捕获到的名称（如快捷键动作名）再走一次词典，避免中英混排
  function translateCaptured(s) {
    if (!s) return s;
    const t = s.trim();
    if (!t) return s;
    const hit = exactLookup.get(t);
    if (hit !== undefined) return hit;
    const lowerHit = lowerLookup.get(t.toLowerCase());
    if (lowerHit !== undefined) return lowerHit;
    return s;
  }

  function translateString(text) {
    if (!text) return text;
    const trimmed = text.trim();
    if (!trimmed) return text;

    // --- 纯标点节点：独立渲染的英文标点转中文标点（如 DOM 拆分的 "?" 节点）---
    if (/^[?.!,;:]+$/.test(trimmed)) {
      const puncMap = { '?': '？', '.': '。', '!': '！', ',': '，', ';': '；', ':': '：' };
      let puncOut = '';
      for (const ch of trimmed) puncOut += puncMap[ch] || ch;
      return text.replace(trimmed, puncOut);
    }

    // 没有英文字母的节点直接跳过（中文、数字、纯符号等）
    if (!/[A-Za-z]/.test(trimmed)) return text;

    // 纯键盘快捷键组合保持原样（如 "Ctrl+Shift+P"）；带说明文字的标签仍交给动态规则
    if (/^(?:Ctrl|Cmd|Command|Alt|Option|Shift|Meta|Super|⌘|⌥|⇧|⌃)(?:\s*[+\-]\s*(?:Ctrl|Cmd|Command|Alt|Option|Shift|Meta|Super|[A-Za-z0-9[\]\\;',./`=+\-↑↓←→⇥]))+$/i.test(trimmed)) return text;

    // 结果缓存：设置页大量重复文案，避免重复跑动态规则
    if (trimmed.length <= CACHE_MAX_TEXT) {
      const cached = translationCache.get(text);
      if (cached !== undefined) return cached;
    }

    const result = translateStringUncached(text, trimmed);
    if (trimmed.length <= CACHE_MAX_TEXT) {
      if (translationCache.size >= CACHE_LIMIT) translationCache.clear();
      translationCache.set(text, result);
    }
    return result;
  }

  function translateStringUncached(text, trimmed) {
    // --- Dynamic Agent Logs Regex Rules ---
    let dynamicMatch = trimmed;
    let isDynamic = false;

    if (/^Worked for [\d smhd.]+$/.test(trimmed)) {
      dynamicMatch = dynamicMatch.replace(/Worked for (.+)$/, function (_, d) {
        return '已工作 ' + fmtDuration(d);
      });
      isDynamic = true;
    }
    if (/^Thought for [\d smhd.]+$/.test(trimmed)) {
      dynamicMatch = dynamicMatch.replace(/Thought for (.+)$/, function (_, d) {
        return '已思考 ' + fmtDuration(d);
      });
      isDynamic = true;
    }
    if (/^Edited .* \+\d+ -\d+$/.test(trimmed)) {
      dynamicMatch = dynamicMatch.replace(/Edited (.*) \+(\d+) -(\d+)/, '编辑了 $1 (+$2 -$3)');
      isDynamic = true;
    }
    if (/^\d+ files? changed$/.test(trimmed)) {
      dynamicMatch = dynamicMatch.replace(/^(\d+) files? changed(.*)/, '$1 个文件已更改$2');
      isDynamic = true;
    }
    if (/^Explored/.test(trimmed)) {
      if (/^Explored \d+ files?$/.test(trimmed)) {
        dynamicMatch = dynamicMatch.replace(/^Explored (\d+) files?(.*)/, '浏览了 $1 个文件$2');
      } else if (/^Explored (.*)$/.test(trimmed)) {
        dynamicMatch = dynamicMatch.replace(/^Explored (.*)/, '浏览了 $1');
      }
      isDynamic = true;
    }
    if (/^Canceled taskkill/.test(trimmed)) {
      dynamicMatch = dynamicMatch.replace(/^Canceled (.*)/, '已取消 $1');
      isDynamic = true;
    }
    if (isDynamic) return text.replace(trimmed, dynamicMatch);

    // 1. 精确匹配（先区分大小写，再大小写不敏感，Map O(1)）
    const trimmedLower = trimmed.toLowerCase();
    const exact = exactLookup.get(trimmed);
    if (exact !== undefined) return text.replace(trimmed, exact);
    const exactLower = lowerLookup.get(trimmedLower);
    if (exactLower !== undefined) return text.replace(trimmed, exactLower);

    // 2. 去掉尾部标点后再精确匹配
    let core = trimmed;
    let trailPunc = '';
    let matchPunc = '';
    const puncRegex = /(\.\.\.|…|\.|\?|!|:|：|？|！|。)$/;
    const match = core.match(puncRegex);
    if (match) {
      matchPunc = match[0];
      core = core.slice(0, -matchPunc.length).trim();
      if (matchPunc === '.') trailPunc = '。';
      else if (matchPunc === '?') trailPunc = '？';
      else if (matchPunc === '!') trailPunc = '！';
      else if (matchPunc === ':') trailPunc = '：';
      else if (matchPunc === '：') trailPunc = '：';
      else if (matchPunc === '？') trailPunc = '？';
      else if (matchPunc === '！') trailPunc = '！';
      else if (matchPunc === '。') trailPunc = '。';
      else trailPunc = matchPunc;
    }

    const coreExact = exactLookup.get(core);
    if (coreExact !== undefined) return text.replace(trimmed, coreExact + trailPunc);
    const coreExactLower = lowerLookup.get(core.toLowerCase());
    if (coreExactLower !== undefined) return text.replace(trimmed, coreExactLower + trailPunc);

    // 2.5 配额/时长中的英文单位先转成中文（如 "6 days, 23 hours"）
    let dynamicInput = trimmed;
    if (/\d/.test(dynamicInput) && /\b(?:days?|hours?|minutes?|seconds?|weeks?|months?|years?)\b/i.test(dynamicInput)) {
      dynamicInput = translateDurationPhrases(dynamicInput);
    }

    // 2.6 动态正则规则兜底（整串锚定）
    for (var ri = 0; ri < dynamicRules.length; ri++) {
      if (dynamicRules[ri][0].test(dynamicInput)) {
        var ruleOut = dynamicInput.replace(dynamicRules[ri][0], dynamicRules[ri][1]);
        if (ruleOut !== dynamicInput) {
          return text.replace(trimmed, ruleOut);
        }
      }
    }

    // 3. 长句不再逐词替换：无法整句命中时保持英文，避免中英夹杂（缺失词条请补词典）
    const hasChinese = /[一-龥]/.test(core);
    const wordsCount = core.split(/\s+/).filter(Boolean).length;
    if (wordsCount > 3) return text;
    if (hasChinese) return text;

    // 4. 短文本逐词兜底：仅当每个 >=2 字母的单词都能在词典中找到时才翻译
    const tokens = core.match(/[A-Za-z][A-Za-z'-]*/g) || [];
    if (!tokens.length) return text;
    for (var ti = 0; ti < tokens.length; ti++) {
      const token = tokens[ti];
      if (token.length < 2) continue;
      if (!tokenLookup.has(token.toLowerCase())) return text;
    }
    let out = core.replace(/[A-Za-z][A-Za-z'-]*/g, function (token) {
      const tr = tokenLookup.get(token.toLowerCase());
      return tr !== undefined ? tr : token;
    });
    out = out.replace(/([一-龥])\s+([一-龥])/g, '$1$2');
    if (matchPunc) out += trailPunc;
    return text.replace(trimmed, out);
  }

  // 时长短语：6 days, 23 hours -> 6 天 23 小时
  function translateDurationPhrases(s) {
    return s
      .replace(/(\d+)\s*days?\s*,\s*(\d+)\s*hours?/gi, '$1 天 $2 小时')
      .replace(/(\d+)\s*hours?\s*,\s*(\d+)\s*minutes?/gi, '$1 小时 $2 分钟')
      .replace(/(\d+)\s*minutes?\s*,\s*(\d+)\s*seconds?/gi, '$1 分 $2 秒')
      .replace(/(\d+)\s*days?/gi, '$1 天')
      .replace(/(\d+)\s*hours?/gi, '$1 小时')
      .replace(/(\d+)\s*minutes?/gi, '$1 分钟')
      .replace(/(\d+)\s*seconds?/gi, '$1 秒');
  }

  // 用于模糊匹配类名中包含代码/预览/diff相关关键词的正则
  const codeClassPattern = /(?:^|[\s_-])(hljs|shiki|prism|monaco|codemirror|line-number|line-content|gutter|codeblock|code-block|code-view|code-preview|file-preview|file-content|syntax-highlighting)(?:$|[\s_-])/i;

  const SKIP_TAGS = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, NOSCRIPT: 1, KBD: 1, SAMP: 1, VAR: 1 };
  const SKIP_SELECTOR = [
    '[contenteditable="true"]',
    '[data-language]', '[data-code]', '[data-line]', '[data-line-number]',
    '[role="code"]',
    '.cursor-edit', '.monaco-editor', '.editor-instance', '.input-area', '.chat-input',
    '.code-line', '.select-contain',
    '[class*="font-mono"][class*="rounded-xl"]'
  ].join(',');
  const TRIGGER_SELECTOR = '[data-testid="thinking-collapsible-trigger"],[data-testid="worked-for-collapsible"],[data-testid="tool-group-collapsible"]';
  const skipCache = new WeakMap();

  function shouldSkipNode(node) {
    if (!node) return true;
    const element = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
    if (!element) return false;
    if (node.nodeType === Node.TEXT_NODE && (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) return true;
    const cached = skipCache.get(element);
    if (cached !== undefined) return cached;

    let result = false;
    if (SKIP_TAGS[element.tagName]) {
      result = true;
    } else {
      // 思考链/模型回复正文：模型生成的自由文本不逐词翻译；
      // 但触发药丸（已思考 X 秒 / 已工作 X）是系统 UI，放行。
      const container = element.closest && element.closest(
        '[data-testid="thinking-collapsible"],[data-testid="planner-response-text"],[data-testid="artifact-view"]'
      );
      if (container) {
        const trigger = element.closest(TRIGGER_SELECTOR);
        if (!(trigger && container.contains(trigger))) result = true;
      }
      if (!result && element.closest && element.closest(SKIP_SELECTOR)) result = true;
      if (!result && element.className && typeof element.className === 'string') {
        let cur = element;
        while (cur) {
          if (cur.className && typeof cur.className === 'string') {
            const lc = cur.className.toLowerCase();
            if (lc.includes('code-line') || lc.includes('select-contain') || codeClassPattern.test(cur.className)) {
              result = true;
              break;
            }
          }
          if (SKIP_TAGS[cur.tagName]) {
            result = true;
            break;
          }
          cur = cur.parentElement;
        }
      }
    }
    skipCache.set(element, result);
    return result;
  }

  function isKeyboardShortcutContext(node) {
    let el = node && node.parentElement;
    for (let depth = 0; depth < 4 && el; depth++, el = el.parentElement) {
      const txt = (el.textContent || '').trim();
      if (/(?:Ctrl|Cmd|Alt|Shift|Meta|Enter|Tab|Esc|⌘|⌥|⇧|⌃)\s*[+\-]/.test(txt)) return true;
    }
    return false;
  }

  const ATTR_NAMES = ['placeholder', 'title', 'aria-label', 'value'];

  let pendingQueue = [];
  let pendingHead = 0;
  let priorityQueue = [];
  let priorityHead = 0;
  let scheduled = false;
  const queuedNodes = new WeakSet();

  function scheduleQueue() {
    if (scheduled) return;
    scheduled = true;
    let done = false;
    const run = function (deadline) {
      if (done) return;
      done = true;
      processQueue(deadline);
    };
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(run, { timeout: 200 });
      // 兜底：窗口后台化时 requestIdleCallback 可能被节流，用定时器保证队列继续推进
      setTimeout(run, 250);
    } else {
      setTimeout(run, 16);
    }
  }

  function enqueueNode(node, priority) {
    if (!node) return;
    const type = node.nodeType;
    if (type !== Node.TEXT_NODE && type !== Node.ELEMENT_NODE && type !== Node.DOCUMENT_FRAGMENT_NODE) return;
    if (queuedNodes.has(node)) return;
    queuedNodes.add(node);
    if (priority) priorityQueue.push(node);
    else pendingQueue.push(node);
    scheduleQueue();
  }

  function isDetached(node) {
    return node.nodeType !== Node.DOCUMENT_FRAGMENT_NODE && node.isConnected === false;
  }

  // React 常把一句话拆成多个文本节点（如 "No automations yet"），
  // 若整个父节点的文本在词典里有整句译文，就统一改写，避免出现中英混杂
  function tryCompositeSentence(node, original) {
    const parent = node && node.parentElement;
    if (!parent || parent.childElementCount > 0) return false;
    const childNodes = parent.childNodes;
    if (childNodes.length < 2) return false;
    const own = (original || '').trim();
    if (!own) return false;
    const combined = (parent.textContent || '').replace(/\s+/g, ' ').trim();
    if (!combined || combined.length > 200 || !/[A-Za-z]/.test(combined)) return false;
    if (combined === own || !combined.includes(own)) return false;
    let hit = exactLookup.get(combined);
    if (hit === undefined) hit = lowerLookup.get(combined.toLowerCase());
    if (hit === undefined) return false;
    // 逐节点写入，保留原有文本节点结构，避免影响 React 的节点引用
    let first = true;
    for (let i = 0; i < childNodes.length; i++) {
      const child = childNodes[i];
      if (child.nodeType !== Node.TEXT_NODE) continue;
      child.nodeValue = first ? hit : '';
      first = false;
    }
    return true;
  }

  function translateOne(node, priority) {
    if (!node || isDetached(node)) return;
    if (node.nodeType === Node.TEXT_NODE) {
      if (shouldSkipNode(node)) return;
      const original = node.nodeValue;
      if (!original || original.length > 20000) return;
      // 快捷键里的 "," "." 等不能转成全角标点
      if (/^[?.!,;:]+$/.test(original.trim()) && isKeyboardShortcutContext(node)) return;
      if (tryCompositeSentence(node, original)) return;
      const translated = translateString(original);
      if (translated !== original) node.nodeValue = translated;
      return;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (shouldSkipNode(node)) return;
      for (let ai = 0; ai < ATTR_NAMES.length; ai++) {
        const attr = ATTR_NAMES[ai];
        if (!node.hasAttribute(attr)) continue;
        if (attr === 'value' && (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA')) continue;
        if (node.tagName === 'INPUT' && attr === 'value' && node.type !== 'button' && node.type !== 'submit') continue;
        const original = node.getAttribute(attr);
        if (!original) continue;
        const translated = translateString(original);
        if (translated !== original) node.setAttribute(attr, translated);
      }
      if (node.shadowRoot) enqueueNode(node.shadowRoot, priority);
      for (let i = 0; i < node.childNodes.length; i++) enqueueNode(node.childNodes[i], priority);
      return;
    }
    if (node.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
      for (let i = 0; i < node.childNodes.length; i++) enqueueNode(node.childNodes[i], priority);
    }
  }

  function processQueue(deadline) {
    scheduled = false;
    const start = performance.now();
    const budget = deadline && typeof deadline.timeRemaining === 'function'
      ? Math.max(2, Math.min(10, deadline.timeRemaining()))
      : 8;
    let processed = 0;
    const priorityBudget = 16;

    // 1) 优先处理新出现的 UI（设置弹窗、菜单、对话流），避免初始页面积压导致新内容迟迟不翻译
    while (priorityHead < priorityQueue.length) {
      const node = priorityQueue[priorityHead++];
      queuedNodes.delete(node);
      try {
        translateOne(node, true);
      } catch (e) {
        console.error('[Antigravity-ZH] translate error:', e);
      }
      processed++;
      if (processed >= 1000 || performance.now() - start > priorityBudget) break;
    }
    if (priorityHead >= priorityQueue.length) {
      priorityQueue = [];
      priorityHead = 0;
    } else if (priorityHead > 512 && priorityHead * 2 > priorityQueue.length) {
      priorityQueue = priorityQueue.slice(priorityHead);
      priorityHead = 0;
    }

    // 2) 空闲时间再处理初始页面/历史积压
    if (priorityHead >= priorityQueue.length) {
      processed = 0;
      while (pendingHead < pendingQueue.length) {
        const node = pendingQueue[pendingHead++];
        queuedNodes.delete(node);
        try {
          translateOne(node, false);
        } catch (e) {
          console.error('[Antigravity-ZH] translate error:', e);
        }
        processed++;
        if (processed >= 300 || performance.now() - start > budget) break;
      }
      if (pendingHead > 512 && pendingHead * 2 > pendingQueue.length) {
        pendingQueue = pendingQueue.slice(pendingHead);
        pendingHead = 0;
      }
      if (pendingHead >= pendingQueue.length) {
        pendingQueue = [];
        pendingHead = 0;
      }
    }

    if (priorityHead < priorityQueue.length || pendingHead < pendingQueue.length) {
      scheduleQueue();
    }
  }

  const observerConfig = {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['placeholder', 'title', 'aria-label', 'value']
  };

  const observers = [];

  function handleMutations(mutations) {
    for (let mi = 0; mi < mutations.length; mi++) {
      const m = mutations[mi];
      if (m.type === 'childList') {
        for (let i = 0; i < m.addedNodes.length; i++) enqueueNode(m.addedNodes[i], true);
      } else if (m.type === 'characterData') {
        // 跳过引擎自己写入的中文，避免“翻译→再次入队”的反馈循环
        const v = m.target.nodeValue || '';
        if (/[A-Za-z]/.test(v)) enqueueNode(m.target, true);
      } else if (m.type === 'attributes') {
        const v = m.target.getAttribute(m.attributeName) || '';
        if (/[A-Za-z]/.test(v)) enqueueNode(m.target, true);
      }
    }
  }

  function observeRoot(root) {
    const observer = new MutationObserver(handleMutations);
    observer.observe(root, observerConfig);
    observers.push(observer);
  }

  // Hook attachShadow
  const originalAttachShadow = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function() {
    const shadowRoot = originalAttachShadow.apply(this, arguments);
    observeRoot(shadowRoot);
    enqueueNode(shadowRoot, true);
    return shadowRoot;
  };

  function startObserver() {
    if (!document.body) {
      document.addEventListener('DOMContentLoaded', startObserver);
      return;
    }
    enqueueNode(document.body, false);
    observeRoot(document.body);
  }

  // 外部词典热加载（函数定义在上方；此处调用时队列/观察器均已就绪）
  loadExternalDict();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserver);
  } else {
    startObserver();
  }

  // 诊断接口（DevTools Console 可查看）
  try {
    window.__AG_ZH__ = {
      version: 'v4',
      dictSize: Object.keys(combinedDict).length,
      translate: translateString,
      pending: function () { return (priorityQueue.length - priorityHead) + (pendingQueue.length - pendingHead); }
    };
  } catch (e) {}
})();

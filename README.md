<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-orange.svg" alt="Dependencies">
</p>

<p align="center">
  <a href="README.md">简体中文</a> | 
  <a href="README_EN.md">English</a> | 
  <a href="README_TW.md">繁體中文</a>
</p>

<h1 align="center">🔔 NotifyPilot</h1>

<h3 align="center">轻量级终端智能通知管理与调度引擎</h3>

<p align="center">
  <strong>零依赖 · 跨平台 · 智能优先级 · TUI仪表盘 · 多渠道支持</strong>
</p>

---

## 🎉 项目介绍

**NotifyPilot** 是一款专为开发者和运维人员打造的**轻量级终端智能通知管理与调度引擎**。它帮助您高效管理来自多个渠道的通知，通过智能优先级分析确保重要信息不被遗漏，并提供优雅的TUI仪表盘进行可视化操作。

### 🎯 解决的痛点

- **通知混乱**：来自系统、监控、部署等多渠道的通知难以统一管理
- **优先级不明**：无法快速识别哪些通知需要立即处理
- **调度困难**：缺乏灵活的通知定时和静默时段管理
- **重复劳动**：相似通知需要反复手动创建

### ✨ 自研差异化亮点

- 🧠 **智能优先级引擎**：基于关键词、来源、紧急程度的加权计算
- 📋 **模板系统**：支持变量替换的通知模板，减少重复工作
- ⏰ **智能调度**：支持静默时段、定时发送、延期提醒
- 📊 **TUI仪表盘**：优雅的终端交互界面，无需离开命令行
- 🔌 **多渠道支持**：终端、系统通知、Webhook、邮件等
- 📤 **多格式导出**：JSON、Markdown、HTML报告导出
- 🚀 **零依赖**：纯Python标准库实现，安装即用

---

## ✨ 核心特性

### 📬 多渠道通知聚合
- **终端输出**：格式化的终端通知显示
- **系统通知**：支持 macOS、Linux、Windows 原生通知
- **Webhook**：支持自定义Webhook推送
- **可扩展**：易于添加新的通知渠道

### 🎯 智能优先级评估
- **关键词分析**：自动识别紧急、重要、普通关键词
- **来源权重**：根据通知来源自动调整优先级
- **加权计算**：可配置的多维度评分系统
- **阈值分级**：Critical / High / Medium / Low / Info 五级分类

### ⏰ 定时调度
- **定时发送**：支持ISO格式时间调度
- **静默时段**：配置免打扰时间段
- **延期提醒**：Snooze功能支持自定义时长
- **自动清理**：过期通知自动清理

### 📝 通知模板系统
- **变量模板**：支持 `{variable}` 格式的变量替换
- **模板管理**：创建、列表、删除模板
- **快速使用**：一行命令从模板创建通知

### 📊 TUI仪表盘
- **实时统计**：通知总数、未读数、24小时新增
- **交互浏览**：键盘导航、筛选、详情查看
- **快捷操作**：标记已读、忽略、延期、删除

### 📤 多格式导出
- **JSON**：结构化数据导出
- **Markdown**：文档格式导出
- **HTML**：可视化报告导出

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: macOS / Linux / Windows

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/NotifyPilot.git
cd NotifyPilot

# 安装（零依赖，无需pip install）
python notify_pilot.py --help
```

### 本地启动

```bash
# 发送一条通知
python notify_pilot.py send "构建完成" "所有测试通过" -p high

# 启动TUI仪表盘
python notify_pilot.py tui

# 查看通知列表
python notify_pilot.py list

# 查看统计信息
python notify_pilot.py stats
```

---

## 📖 详细使用指南

### 基本命令

#### 发送通知

```bash
# 基本发送
python notify_pilot.py send "标题" "消息内容"

# 指定优先级
python notify_pilot.py send "紧急警报" "服务器宕机" -p critical

# 指定来源和渠道
python notify_pilot.py send "部署完成" "生产环境部署成功" -s deployment -c system

# 添加标签
python notify_pilot.py send "测试通知" "这是一条测试" -t "test,dev,ci"

# 定时发送
python notify_pilot.py send "提醒" "会议即将开始" --schedule "2025-05-28T15:00:00"
```

#### 列出通知

```bash
# 列出所有通知
python notify_pilot.py list

# 按优先级筛选
python notify_pilot.py list -p critical

# 按状态筛选
python notify_pilot.py list -s pending

# 限制数量
python notify_pilot.py list -l 50
```

#### 管理通知

```bash
# 标记已读
python notify_pilot.py read <notification_id>

# 忽略通知
python notify_pilot.py dismiss <notification_id>

# 延期提醒
python notify_pilot.py snooze <notification_id> -d 60  # 60分钟后提醒

# 删除通知
python notify_pilot.py delete <notification_id>
```

### 模板系统

```bash
# 创建模板
python notify_pilot.py template create deploy \
  --title "部署 {env} 完成" \
  --message "已成功部署到 {env} 环境，版本 {version}" \
  -p high

# 列出模板
python notify_pilot.py template list

# 使用模板
python notify_pilot.py template use <template_id> -v env=production,version=v1.2.0
```

### 导出功能

```bash
# 导出为JSON
python notify_pilot.py export -f json -o notifications.json

# 导出为Markdown
python notify_pilot.py export -f markdown -o report.md

# 导出为HTML
python notify_pilot.py export -f html -o report.html
```

### 配置管理

```bash
# 查看配置
python notify_pilot.py config show

# 设置配置项
python notify_pilot.py config set display.theme dark

# 重置配置
python notify_pilot.py config reset
```

### TUI仪表盘

启动交互式终端界面：

```bash
python notify_pilot.py tui
```

**快捷键**：
- `↑/↓` - 导航通知列表
- `Enter` - 查看详情
- `n` - 创建新通知
- `f` - 按优先级筛选
- `s` - 按状态筛选
- `r` - 刷新列表
- `h` - 帮助
- `q` - 退出

---

## 💡 设计思路与迭代规划

### 设计理念

NotifyPilot 的设计遵循以下原则：

1. **零依赖优先**：使用Python标准库，确保最大兼容性
2. **本地优先**：数据存储在本地，保护隐私
3. **智能优先**：通过算法帮助用户识别重要信息
4. **简洁易用**：CLI优先，TUI辅助，降低学习成本

### 技术选型原因

- **Python标准库**：无需安装额外依赖，开箱即用
- **JSON存储**：轻量级、易读、易备份
- **Dataclass模型**：类型安全、代码清晰
- **Enum枚举**：状态和优先级管理更规范

### 后续迭代计划

- [ ] 支持更多通知渠道（Slack、钉钉、企业微信）
- [ ] 添加Web UI界面
- [ ] 支持通知规则引擎（条件触发）
- [ ] 集成系统监控（CPU、内存、磁盘告警）
- [ ] 支持通知聚合（相似通知合并）
- [ ] 添加通知分析报告（周报、月报）

### 社区贡献方向

欢迎贡献以下内容：
- 🌐 多语言翻译
- 🔌 新的通知渠道适配器
- 🎨 TUI主题设计
- 📝 文档改进
- 🐛 Bug修复

---

## 📦 打包与部署指南

### 作为Python模块使用

```python
from notify_pilot import NotifyPilotEngine

# 初始化引擎
engine = NotifyPilotEngine()

# 创建通知
nid = engine.create_notification(
    title="构建完成",
    message="所有测试通过，可以部署",
    priority="high",
    source="ci",
    tags=["build", "test"]
)

# 发送通知
engine.send_notification(nid)

# 获取统计
stats = engine.get_stats()
print(stats)
```

### 打包为可执行文件

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --name notifypilot notify_pilot.py

# 生成的可执行文件在 dist/ 目录
```

### 系统集成

**作为系统服务运行**：

```bash
# 创建systemd服务
sudo cat > /etc/systemd/system/notifypilot.service << EOF
[Unit]
Description=NotifyPilot Notification Service
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/bin/python3 /path/to/notify_pilot.py tui
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable notifypilot
sudo systemctl start notifypilot
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个很棒的功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### Issue反馈

提交Issue时请包含：
- 操作系统和Python版本
- 复现步骤
- 期望行为
- 实际行为
- 相关日志

---

## 📄 开源协议说明

本项目采用 **MIT License** 开源协议。

这意味着您可以：
- ✅ 商业使用
- ✅ 修改代码
- ✅ 分发代码
- ✅ 私人使用

唯一要求是保留版权声明和许可声明。

---

<p align="center">
  Made with ❤️ by NotifyPilot Team
</p>

<p align="center">
  如果这个项目对您有帮助，请给一个 ⭐️ Star！
</p>

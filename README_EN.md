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

<h3 align="center">Lightweight Terminal Intelligent Notification Management & Scheduling Engine</h3>

<p align="center">
  <strong>Zero Dependencies · Cross-Platform · Smart Priority · TUI Dashboard · Multi-Channel Support</strong>
</p>

---

## 🎉 Introduction

**NotifyPilot** is a **lightweight terminal intelligent notification management and scheduling engine** designed for developers and DevOps professionals. It helps you efficiently manage notifications from multiple channels, ensures important information is never missed through intelligent priority analysis, and provides an elegant TUI dashboard for visual operations.

### 🎯 Problems Solved

- **Notification Chaos**: Notifications from systems, monitoring, deployments, etc. are hard to manage uniformly
- **Unclear Priorities**: Cannot quickly identify which notifications need immediate attention
- **Scheduling Difficulties**: Lack of flexible notification timing and quiet period management
- **Repetitive Work**: Similar notifications need to be created manually repeatedly

### ✨ Unique Features

- 🧠 **Smart Priority Engine**: Weighted calculation based on keywords, sources, and urgency
- 📋 **Template System**: Notification templates with variable substitution to reduce repetitive work
- ⏰ **Smart Scheduling**: Support for quiet hours, scheduled sending, and snooze reminders
- 📊 **TUI Dashboard**: Elegant terminal interactive interface without leaving the command line
- 🔌 **Multi-Channel Support**: Terminal, system notifications, webhooks, email, etc.
- 📤 **Multi-Format Export**: JSON, Markdown, HTML report export
- 🚀 **Zero Dependencies**: Pure Python standard library implementation, ready to use

---

## ✨ Core Features

### 📬 Multi-Channel Notification Aggregation
- **Terminal Output**: Formatted terminal notification display
- **System Notifications**: Native notifications for macOS, Linux, Windows
- **Webhook**: Support for custom webhook push
- **Extensible**: Easy to add new notification channels

### 🎯 Smart Priority Assessment
- **Keyword Analysis**: Automatic identification of urgent, important, and normal keywords
- **Source Weighting**: Automatic priority adjustment based on notification source
- **Weighted Calculation**: Configurable multi-dimensional scoring system
- **Threshold Classification**: Five levels - Critical / High / Medium / Low / Info

### ⏰ Scheduled Dispatch
- **Scheduled Sending**: Support for ISO format time scheduling
- **Quiet Hours**: Configure do-not-disturb time periods
- **Snooze Reminders**: Snooze function with customizable duration
- **Auto Cleanup**: Automatic cleanup of expired notifications

### 📝 Notification Template System
- **Variable Templates**: Support for `{variable}` format variable substitution
- **Template Management**: Create, list, delete templates
- **Quick Use**: Create notifications from templates with one command

### 📊 TUI Dashboard
- **Real-time Statistics**: Total notifications, unread count, 24-hour new additions
- **Interactive Browsing**: Keyboard navigation, filtering, detail viewing
- **Quick Actions**: Mark as read, dismiss, snooze, delete

### 📤 Multi-Format Export
- **JSON**: Structured data export
- **Markdown**: Document format export
- **HTML**: Visual report export

---

## 🚀 Quick Start

### Requirements

- **Python**: 3.8 or higher
- **Operating System**: macOS / Linux / Windows

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/NotifyPilot.git
cd NotifyPilot

# Run (zero dependencies, no pip install required)
python notify_pilot.py --help
```

### Local Startup

```bash
# Send a notification
python notify_pilot.py send "Build Complete" "All tests passed" -p high

# Launch TUI dashboard
python notify_pilot.py tui

# View notification list
python notify_pilot.py list

# View statistics
python notify_pilot.py stats
```

---

## 📖 Detailed Usage Guide

### Basic Commands

#### Send Notification

```bash
# Basic send
python notify_pilot.py send "Title" "Message content"

# Specify priority
python notify_pilot.py send "Urgent Alert" "Server down" -p critical

# Specify source and channel
python notify_pilot.py send "Deploy Complete" "Production deployment successful" -s deployment -c system

# Add tags
python notify_pilot.py send "Test Notification" "This is a test" -t "test,dev,ci"

# Scheduled send
python notify_pilot.py send "Reminder" "Meeting starting soon" --schedule "2025-05-28T15:00:00"
```

#### List Notifications

```bash
# List all notifications
python notify_pilot.py list

# Filter by priority
python notify_pilot.py list -p critical

# Filter by status
python notify_pilot.py list -s pending

# Limit count
python notify_pilot.py list -l 50
```

#### Manage Notifications

```bash
# Mark as read
python notify_pilot.py read <notification_id>

# Dismiss notification
python notify_pilot.py dismiss <notification_id>

# Snooze reminder
python notify_pilot.py snooze <notification_id> -d 60  # Remind in 60 minutes

# Delete notification
python notify_pilot.py delete <notification_id>
```

### Template System

```bash
# Create template
python notify_pilot.py template create deploy \
  --title "Deploy {env} Complete" \
  --message "Successfully deployed to {env} environment, version {version}" \
  -p high

# List templates
python notify_pilot.py template list

# Use template
python notify_pilot.py template use <template_id> -v env=production,version=v1.2.0
```

### Export Functionality

```bash
# Export as JSON
python notify_pilot.py export -f json -o notifications.json

# Export as Markdown
python notify_pilot.py export -f markdown -o report.md

# Export as HTML
python notify_pilot.py export -f html -o report.html
```

### Configuration Management

```bash
# View configuration
python notify_pilot.py config show

# Set configuration item
python notify_pilot.py config set display.theme dark

# Reset configuration
python notify_pilot.py config reset
```

### TUI Dashboard

Launch the interactive terminal interface:

```bash
python notify_pilot.py tui
```

**Keyboard Shortcuts**:
- `↑/↓` - Navigate notification list
- `Enter` - View details
- `n` - Create new notification
- `f` - Filter by priority
- `s` - Filter by status
- `r` - Refresh list
- `h` - Help
- `q` - Quit

---

## 💡 Design Philosophy & Roadmap

### Design Principles

NotifyPilot follows these principles:

1. **Zero Dependencies First**: Use Python standard library for maximum compatibility
2. **Local First**: Data stored locally to protect privacy
3. **Intelligence First**: Algorithms help users identify important information
4. **Simple & Easy**: CLI first, TUI assisted, low learning curve

### Technology Choices

- **Python Standard Library**: No additional dependencies required, works out of the box
- **JSON Storage**: Lightweight, readable, easy to backup
- **Dataclass Models**: Type-safe, clean code
- **Enum Enumeration**: More standardized state and priority management

### Future Roadmap

- [ ] Support for more notification channels (Slack, DingTalk, WeCom)
- [ ] Add Web UI interface
- [ ] Support notification rule engine (conditional triggers)
- [ ] Integrate system monitoring (CPU, memory, disk alerts)
- [ ] Support notification aggregation (similar notification merging)
- [ ] Add notification analysis reports (weekly, monthly)

### Community Contribution Areas

Contributions welcome in:
- 🌐 Multi-language translations
- 🔌 New notification channel adapters
- 🎨 TUI theme designs
- 📝 Documentation improvements
- 🐛 Bug fixes

---

## 📦 Packaging & Deployment Guide

### Use as Python Module

```python
from notify_pilot import NotifyPilotEngine

# Initialize engine
engine = NotifyPilotEngine()

# Create notification
nid = engine.create_notification(
    title="Build Complete",
    message="All tests passed, ready to deploy",
    priority="high",
    source="ci",
    tags=["build", "test"]
)

# Send notification
engine.send_notification(nid)

# Get statistics
stats = engine.get_stats()
print(stats)
```

### Package as Executable

```bash
# Package with PyInstaller
pip install pyinstaller
pyinstaller --onefile --name notifypilot notify_pilot.py

# Generated executable in dist/ directory
```

### System Integration

**Run as system service**:

```bash
# Create systemd service
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

# Enable service
sudo systemctl enable notifypilot
sudo systemctl start notifypilot
```

---

## 🤝 Contributing Guide

We welcome all forms of contributions!

### Submit PR

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Submit Pull Request

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool related

### Issue Feedback

When submitting an issue, please include:
- Operating system and Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs

---

## 📄 License

This project is licensed under the **MIT License**.

This means you can:
- ✅ Commercial use
- ✅ Modify code
- ✅ Distribute code
- ✅ Private use

The only requirement is to retain the copyright notice and license notice.

---

<p align="center">
  Made with ❤️ by NotifyPilot Team
</p>

<p align="center">
  If this project helps you, please give it a ⭐️ Star!
</p>

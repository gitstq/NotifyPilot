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

<h3 align="center">輕量級終端智慧通知管理與排程引擎</h3>

<p align="center">
  <strong>零依賴 · 跨平台 · 智慧優先級 · TUI儀表板 · 多管道支援</strong>
</p>

---

## 🎉 專案介紹

**NotifyPilot** 是一款專為開發者和維運人員打造的**輕量級終端智慧通知管理與排程引擎**。它幫助您高效管理來自多個管道的通知，透過智慧優先級分析確保重要資訊不被遺漏，並提供優雅的TUI儀表板進行視覺化操作。

### 🎯 解決的痛點

- **通知混亂**：來自系統、監控、部署等多管道的通知難以統一管理
- **優先級不明**：無法快速識別哪些通知需要立即處理
- **排程困難**：缺乏靈活的通知定時和靜默時段管理
- **重複勞動**：相似通知需要反覆手動建立

### ✨ 自研差異化亮點

- 🧠 **智慧優先級引擎**：基於關鍵字、來源、緊急程度的加權計算
- 📋 **模板系統**：支援變數替換的通知模板，減少重複工作
- ⏰ **智慧排程**：支援靜默時段、定時發送、延期提醒
- 📊 **TUI儀表板**：優雅的終端互動介面，無需離開命令列
- 🔌 **多管道支援**：終端、系統通知、Webhook、郵件等
- 📤 **多格式匯出**：JSON、Markdown、HTML報告匯出
- 🚀 **零依賴**：純Python標準庫實現，安裝即用

---

## ✨ 核心特性

### 📬 多管道通知聚合
- **終端輸出**：格式化的終端通知顯示
- **系統通知**：支援 macOS、Linux、Windows 原生通知
- **Webhook**：支援自訂Webhook推送
- **可擴展**：易於新增新的通知管道

### 🎯 智慧優先級評估
- **關鍵字分析**：自動識別緊急、重要、普通關鍵字
- **來源權重**：根據通知來源自動調整優先級
- **加權計算**：可設定的多維度評分系統
- **閾值分級**：Critical / High / Medium / Low / Info 五級分類

### ⏰ 定時排程
- **定時發送**：支援ISO格式時間排程
- **靜默時段**：設定免打擾時間段
- **延期提醒**：Snooze功能支援自訂時長
- **自動清理**：過期通知自動清理

### 📝 通知模板系統
- **變數模板**：支援 `{variable}` 格式的變數替換
- **模板管理**：建立、列表、刪除模板
- **快速使用**：一行命令從模板建立通知

### 📊 TUI儀表板
- **即時統計**：通知總數、未讀數、24小時新增
- **互動瀏覽**：鍵盤導航、篩選、詳情查看
- **快捷操作**：標記已讀、忽略、延期、刪除

### 📤 多格式匯出
- **JSON**：結構化資料匯出
- **Markdown**：文件格式匯出
- **HTML**：視覺化報告匯出

---

## 🚀 快速開始

### 環境要求

- **Python**: 3.8 或更高版本
- **作業系統**: macOS / Linux / Windows

### 安裝

```bash
# 複製儲存庫
git clone https://github.com/gitstq/NotifyPilot.git
cd NotifyPilot

# 執行（零依賴，無需pip install）
python notify_pilot.py --help
```

### 本地啟動

```bash
# 發送一則通知
python notify_pilot.py send "建置完成" "所有測試通過" -p high

# 啟動TUI儀表板
python notify_pilot.py tui

# 查看通知列表
python notify_pilot.py list

# 查看統計資訊
python notify_pilot.py stats
```

---

## 📖 詳細使用指南

### 基本命令

#### 發送通知

```bash
# 基本發送
python notify_pilot.py send "標題" "訊息內容"

# 指定優先級
python notify_pilot.py send "緊急警報" "伺服器當機" -p critical

# 指定來源和管道
python notify_pilot.py send "部署完成" "正式環境部署成功" -s deployment -c system

# 新增標籤
python notify_pilot.py send "測試通知" "這是一則測試" -t "test,dev,ci"

# 定時發送
python notify_pilot.py send "提醒" "會議即將開始" --schedule "2025-05-28T15:00:00"
```

#### 列出通知

```bash
# 列出所有通知
python notify_pilot.py list

# 按優先級篩選
python notify_pilot.py list -p critical

# 按狀態篩選
python notify_pilot.py list -s pending

# 限制數量
python notify_pilot.py list -l 50
```

#### 管理通知

```bash
# 標記已讀
python notify_pilot.py read <notification_id>

# 忽略通知
python notify_pilot.py dismiss <notification_id>

# 延期提醒
python notify_pilot.py snooze <notification_id> -d 60  # 60分鐘後提醒

# 刪除通知
python notify_pilot.py delete <notification_id>
```

### 模板系統

```bash
# 建立模板
python notify_pilot.py template create deploy \
  --title "部署 {env} 完成" \
  --message "已成功部署到 {env} 環境，版本 {version}" \
  -p high

# 列出模板
python notify_pilot.py template list

# 使用模板
python notify_pilot.py template use <template_id> -v env=production,version=v1.2.0
```

### 匯出功能

```bash
# 匯出為JSON
python notify_pilot.py export -f json -o notifications.json

# 匯出為Markdown
python notify_pilot.py export -f markdown -o report.md

# 匯出為HTML
python notify_pilot.py export -f html -o report.html
```

### 設定管理

```bash
# 查看設定
python notify_pilot.py config show

# 設定項目
python notify_pilot.py config set display.theme dark

# 重置設定
python notify_pilot.py config reset
```

### TUI儀表板

啟動互動式終端介面：

```bash
python notify_pilot.py tui
```

**快捷鍵**：
- `↑/↓` - 導航通知列表
- `Enter` - 查看詳情
- `n` - 建立新通知
- `f` - 按優先級篩選
- `s` - 按狀態篩選
- `r` - 重新整理列表
- `h` - 說明
- `q` - 離開

---

## 💡 設計思路與迭代規劃

### 設計理念

NotifyPilot 的設計遵循以下原則：

1. **零依賴優先**：使用Python標準庫，確保最大相容性
2. **本地優先**：資料儲存在本地，保護隱私
3. **智慧優先**：透過演算法幫助使用者識別重要資訊
4. **簡潔易用**：CLI優先，TUI輔助，降低學習成本

### 技術選型原因

- **Python標準庫**：無需安裝額外依賴，開箱即用
- **JSON儲存**：輕量級、易讀、易備份
- **Dataclass模型**：型別安全、程式碼清晰
- **Enum列舉**：狀態和優先級管理更規範

### 後續迭代計畫

- [ ] 支援更多通知管道（Slack、釘釘、企業微信）
- [ ] 新增Web UI介面
- [ ] 支援通知規則引擎（條件觸發）
- [ ] 整合系統監控（CPU、記憶體、磁碟告警）
- [ ] 支援通知聚合（相似通知合併）
- [ ] 新增通知分析報告（週報、月報）

### 社群貢獻方向

歡迎貢獻以下內容：
- 🌐 多語言翻譯
- 🔌 新的通知管道適配器
- 🎨 TUI主題設計
- 📝 文件改進
- 🐛 Bug修復

---

## 📦 打包與部署指南

### 作為Python模組使用

```python
from notify_pilot import NotifyPilotEngine

# 初始化引擎
engine = NotifyPilotEngine()

# 建立通知
nid = engine.create_notification(
    title="建置完成",
    message="所有測試通過，可以部署",
    priority="high",
    source="ci",
    tags=["build", "test"]
)

# 發送通知
engine.send_notification(nid)

# 取得統計
stats = engine.get_stats()
print(stats)
```

### 打包為可執行檔

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --name notifypilot notify_pilot.py

# 產生的可執行檔在 dist/ 目錄
```

### 系統整合

**作為系統服務執行**：

```bash
# 建立systemd服務
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

# 啟用服務
sudo systemctl enable notifypilot
sudo systemctl start notifypilot
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 提交PR

1. Fork 本儲存庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'feat: 新增某個很棒的功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 提交規範

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat:` 新功能
- `fix:` Bug修復
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建置/工具相關

### Issue回饋

提交Issue時請包含：
- 作業系統和Python版本
- 重現步驟
- 預期行為
- 實際行為
- 相關日誌

---

## 📄 開源協議說明

本專案採用 **MIT License** 開源協議。

這意味著您可以：
- ✅ 商業使用
- ✅ 修改程式碼
- ✅ 分發程式碼
- ✅ 私人使用

唯一要求是保留版權聲明和許可聲明。

---

<p align="center">
  Made with ❤️ by NotifyPilot Team
</p>

<p align="center">
  如果這個專案對您有幫助，請給一個 ⭐️ Star！
</p>

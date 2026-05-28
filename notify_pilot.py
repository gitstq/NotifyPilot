#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotifyPilot - Lightweight Terminal Intelligent Notification Management Engine
轻量级终端智能通知管理与调度引擎

A zero-dependency CLI tool for intelligent notification management, scheduling,
and priority analysis across multiple channels.

Author: NotifyPilot Team
License: MIT
Version: 1.0.0
"""

import os
import sys
import json
import time
import uuid
import hashlib
import argparse
import subprocess
import threading
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from collections import defaultdict
import re
import shlex
import platform
import tempfile

# ============================================================================
# Constants & Configuration
# ============================================================================

VERSION = "1.0.0"
APP_NAME = "NotifyPilot"
APP_DIR = Path.home() / ".notifypilot"
CONFIG_FILE = APP_DIR / "config.json"
DATA_FILE = APP_DIR / "notifications.json"
TEMPLATE_FILE = APP_DIR / "templates.json"
HISTORY_FILE = APP_DIR / "history.json"

# Default configuration
DEFAULT_CONFIG = {
    "version": VERSION,
    "storage": {
        "max_notifications": 1000,
        "retention_days": 30,
        "auto_cleanup": True
    },
    "priority": {
        "weights": {
            "urgency": 0.4,
            "source": 0.3,
            "keywords": 0.3
        },
        "thresholds": {
            "critical": 80,
            "high": 60,
            "medium": 40,
            "low": 20
        }
    },
    "channels": {
        "system": {"enabled": True, "sound": True},
        "webhook": {"enabled": False, "url": ""},
        "email": {"enabled": False, "smtp": "", "port": 587}
    },
    "schedule": {
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "timezone": "local"
    },
    "display": {
        "theme": "default",
        "max_width": 80,
        "show_icons": True,
        "date_format": "%Y-%m-%d %H:%M:%S"
    }
}

# Priority levels
class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

# Notification status
class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"
    SNOOZED = "snoozed"

# Notification channels
class Channel(Enum):
    SYSTEM = "system"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    DESKTOP = "desktop"
    TERMINAL = "terminal"

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Notification:
    """Notification data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    message: str = ""
    source: str = "manual"
    channel: str = "terminal"
    priority: str = "medium"
    status: str = "pending"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    read_at: Optional[str] = None
    expires_at: Optional[str] = None
    snoozed_until: Optional[str] = None
    repeat: Optional[str] = None  # cron expression
    actions: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        return cls(**data)

@dataclass
class NotificationTemplate:
    """Notification template"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    title_template: str = ""
    message_template: str = ""
    priority: str = "medium"
    channel: str = "terminal"
    tags: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def render(self, **kwargs) -> Notification:
        """Render template with variables"""
        title = self.title_template.format(**kwargs)
        message = self.message_template.format(**kwargs)
        return Notification(
            title=title,
            message=message,
            priority=self.priority,
            channel=self.channel,
            tags=self.tags.copy()
        )

@dataclass
class ScheduleRule:
    """Scheduling rule"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    cron_expression: str = ""
    notification_template_id: str = ""
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# ============================================================================
# Core Engine
# ============================================================================

class PriorityEngine:
    """Intelligent priority calculation engine"""
    
    CRITICAL_KEYWORDS = [
        "urgent", "critical", "emergency", "alert", "error", "fail",
        "紧急", "严重", "错误", "失败", "崩溃", "宕机"
    ]
    
    HIGH_KEYWORDS = [
        "important", "warning", "attention", "required", "deadline",
        "重要", "警告", "注意", "截止", "必须"
    ]
    
    LOW_KEYWORDS = [
        "info", "notice", "update", "fyi", "reminder",
        "通知", "提醒", "更新", "提示"
    ]
    
    SOURCE_WEIGHTS = {
        "system": 0.9,
        "monitoring": 0.85,
        "security": 0.9,
        "deployment": 0.8,
        "backup": 0.7,
        "schedule": 0.6,
        "email": 0.5,
        "chat": 0.4,
        "manual": 0.5
    }
    
    @classmethod
    def calculate(cls, notification: Notification, config: Dict) -> int:
        """Calculate priority score (0-100)"""
        weights = config.get("priority", {}).get("weights", {})
        
        # Base score from explicit priority
        base_scores = {
            "critical": 90,
            "high": 70,
            "medium": 50,
            "low": 30,
            "info": 20
        }
        base = base_scores.get(notification.priority, 50)
        
        # Keyword analysis
        text = f"{notification.title} {notification.message}".lower()
        keyword_score = 50
        
        for kw in cls.CRITICAL_KEYWORDS:
            if kw in text:
                keyword_score = 100
                break
        else:
            for kw in cls.HIGH_KEYWORDS:
                if kw in text:
                    keyword_score = 75
                    break
            else:
                for kw in cls.LOW_KEYWORDS:
                    if kw in text:
                        keyword_score = 25
                        break
        
        # Source weight
        source_score = cls.SOURCE_WEIGHTS.get(notification.source, 50) * 100
        
        # Calculate weighted score
        urgency_weight = weights.get("urgency", 0.4)
        source_weight = weights.get("source", 0.3)
        keywords_weight = weights.get("keywords", 0.3)
        
        final_score = (
            base * urgency_weight +
            source_score * source_weight +
            keyword_score * keywords_weight
        )
        
        return min(100, max(0, int(final_score)))
    
    @classmethod
    def get_priority_level(cls, score: int, config: Dict) -> Priority:
        """Get priority level from score"""
        thresholds = config.get("priority", {}).get("thresholds", {})
        
        if score >= thresholds.get("critical", 80):
            return Priority.CRITICAL
        elif score >= thresholds.get("high", 60):
            return Priority.HIGH
        elif score >= thresholds.get("medium", 40):
            return Priority.MEDIUM
        elif score >= thresholds.get("low", 20):
            return Priority.LOW
        return Priority.INFO

class NotificationStorage:
    """Notification storage manager"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.notifications: Dict[str, Notification] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.history: List[Dict] = []
        self._ensure_dirs()
        self._load_data()
    
    def _ensure_dirs(self):
        """Ensure data directories exist"""
        APP_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load data from files"""
        # Load notifications
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notifications = {
                        k: Notification.from_dict(v) for k, v in data.items()
                    }
            except Exception:
                self.notifications = {}
        
        # Load templates
        if TEMPLATE_FILE.exists():
            try:
                with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = {
                        k: NotificationTemplate(**v) for k, v in data.items()
                    }
            except Exception:
                self.templates = {}
        
        # Load history
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
    
    def _save_notifications(self):
        """Save notifications to file"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({k: v.to_dict() for k, v in self.notifications.items()}, f, indent=2)
    
    def _save_templates(self):
        """Save templates to file"""
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.templates.items()}, f, indent=2)
    
    def _save_history(self):
        """Save history to file"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
    
    def add_notification(self, notification: Notification) -> str:
        """Add a new notification"""
        self.notifications[notification.id] = notification
        self._save_notifications()
        return notification.id
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        return self.notifications.get(notification_id)
    
    def update_notification(self, notification: Notification):
        """Update notification"""
        self.notifications[notification.id] = notification
        self._save_notifications()
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        if notification_id in self.notifications:
            del self.notifications[notification_id]
            self._save_notifications()
            return True
        return False
    
    def list_notifications(self, 
                          status: Optional[str] = None,
                          priority: Optional[str] = None,
                          source: Optional[str] = None,
                          limit: int = 100) -> List[Notification]:
        """List notifications with filters"""
        result = list(self.notifications.values())
        
        if status:
            result = [n for n in result if n.status == status]
        if priority:
            result = [n for n in result if n.priority == priority]
        if source:
            result = [n for n in result if n.source == source]
        
        # Sort by created_at descending
        result.sort(key=lambda x: x.created_at, reverse=True)
        
        return result[:limit]
    
    def add_template(self, template: NotificationTemplate) -> str:
        """Add a new template"""
        self.templates[template.id] = template
        self._save_templates()
        return template.id
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[NotificationTemplate]:
        """List all templates"""
        return list(self.templates.values())
    
    def delete_template(self, template_id: str) -> bool:
        """Delete template"""
        if template_id in self.templates:
            del self.templates[template_id]
            self._save_templates()
            return True
        return False
    
    def add_history(self, event: Dict):
        """Add history event"""
        event["timestamp"] = datetime.now().isoformat()
        self.history.append(event)
        # Keep last 1000 events
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        self._save_history()
    
    def cleanup_expired(self):
        """Clean up expired notifications"""
        now = datetime.now()
        expired = []
        
        for nid, notification in self.notifications.items():
            if notification.expires_at:
                try:
                    expire_time = datetime.fromisoformat(notification.expires_at)
                    if expire_time < now:
                        expired.append(nid)
                except Exception:
                    pass
        
        for nid in expired:
            del self.notifications[nid]
        
        if expired:
            self._save_notifications()
        
        return len(expired)

class NotificationDispatcher:
    """Notification dispatch engine"""
    
    def __init__(self, config: Dict, storage: NotificationStorage):
        self.config = config
        self.storage = storage
    
    def dispatch(self, notification: Notification) -> bool:
        """Dispatch notification through configured channels"""
        channel = Channel(notification.channel)
        
        try:
            if channel == Channel.TERMINAL:
                return self._dispatch_terminal(notification)
            elif channel == Channel.SYSTEM:
                return self._dispatch_system(notification)
            elif channel == Channel.WEBHOOK:
                return self._dispatch_webhook(notification)
            elif channel == Channel.DESKTOP:
                return self._dispatch_desktop(notification)
            else:
                return self._dispatch_terminal(notification)
        except Exception as e:
            print(f"Error dispatching notification: {e}")
            return False
    
    def _dispatch_terminal(self, notification: Notification) -> bool:
        """Display notification in terminal"""
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }
        
        icon = priority_icons.get(notification.priority, "⚪")
        timestamp = datetime.now().strftime(self.config.get("display", {}).get("date_format", "%Y-%m-%d %H:%M:%S"))
        
        # ANSI colors
        colors = {
            "critical": "\033[91m",
            "high": "\033[93m",
            "medium": "\033[94m",
            "low": "\033[92m",
            "info": "\033[96m"
        }
        reset = "\033[0m"
        color = colors.get(notification.priority, "")
        
        print(f"\n{color}{'='*60}{reset}")
        print(f"{icon} [{notification.priority.upper()}] {notification.title}")
        print(f"📅 {timestamp} | 📍 {notification.source}")
        print(f"{'-'*60}")
        print(notification.message)
        if notification.tags:
            print(f"🏷️ Tags: {', '.join(notification.tags)}")
        print(f"{color}{'='*60}{reset}\n")
        
        return True
    
    def _dispatch_system(self, notification: Notification) -> bool:
        """Send system notification"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            cmd = [
                "osascript", "-e",
                f'display notification "{notification.message}" with title "{notification.title}"'
            ]
        elif system == "Linux":
            cmd = ["notify-send", notification.title, notification.message]
        elif system == "Windows":
            # PowerShell notification
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{notification.title}</text>
                        <text id="2">{notification.message}</text>
                    </binding>
                </visual>
            </toast>
"@
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("NotifyPilot").Show($toast)
            '''
            cmd = ["powershell", "-Command", ps_script]
        else:
            return self._dispatch_terminal(notification)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception:
            return self._dispatch_terminal(notification)
    
    def _dispatch_webhook(self, notification: Notification) -> bool:
        """Send webhook notification"""
        import urllib.request
        import urllib.error
        
        webhook_config = self.config.get("channels", {}).get("webhook", {})
        url = webhook_config.get("url", "")
        
        if not url:
            print("Webhook URL not configured")
            return False
        
        payload = json.dumps({
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "source": notification.source,
            "timestamp": datetime.now().isoformat()
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def _dispatch_desktop(self, notification: Notification) -> bool:
        """Send desktop notification (cross-platform)"""
        return self._dispatch_system(notification)

class NotifyPilotEngine:
    """Main NotifyPilot engine"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.storage = NotificationStorage(self.config)
        self.dispatcher = NotificationDispatcher(self.config, self.storage)
        self.priority_engine = PriorityEngine()
        self._scheduler_running = False
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration"""
        if config_path:
            path = Path(config_path)
        else:
            path = CONFIG_FILE
        
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """Save configuration"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    # =========================================================================
    # Notification Operations
    # =========================================================================
    
    def create_notification(self,
                           title: str,
                           message: str,
                           priority: str = "medium",
                           source: str = "manual",
                           channel: str = "terminal",
                           tags: Optional[List[str]] = None,
                           scheduled_at: Optional[str] = None,
                           expires_at: Optional[str] = None,
                           actions: Optional[List[Dict]] = None) -> str:
        """Create a new notification"""
        notification = Notification(
            title=title,
            message=message,
            priority=priority,
            source=source,
            channel=channel,
            tags=tags or [],
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            actions=actions or []
        )
        
        # Calculate intelligent priority
        score = self.priority_engine.calculate(notification, self.config)
        notification.priority = self.priority_engine.get_priority_level(score, self.config).value
        
        nid = self.storage.add_notification(notification)
        
        self.storage.add_history({
            "event": "created",
            "notification_id": nid,
            "title": title
        })
        
        return nid
    
    def send_notification(self, notification_id: str) -> bool:
        """Send a notification"""
        notification = self.storage.get_notification(notification_id)
        if not notification:
            return False
        
        # Check quiet hours
        if self._is_quiet_hours():
            notification.status = NotificationStatus.SNOOZED.value
            notification.snoozed_until = self._get_quiet_hours_end()
            self.storage.update_notification(notification)
            return False
        
        success = self.dispatcher.dispatch(notification)
        
        if success:
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.now().isoformat()
            self.storage.update_notification(notification)
            
            self.storage.add_history({
                "event": "sent",
                "notification_id": notification_id
            })
        
        return success
    
    def mark_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        notification = self.storage.get_notification(notification_id)
        if not notification:
            return False
        
        notification.status = NotificationStatus.READ.value
        notification.read_at = datetime.now().isoformat()
        self.storage.update_notification(notification)
        
        return True
    
    def dismiss(self, notification_id: str) -> bool:
        """Dismiss notification"""
        notification = self.storage.get_notification(notification_id)
        if not notification:
            return False
        
        notification.status = NotificationStatus.DISMISSED.value
        self.storage.update_notification(notification)
        
        return True
    
    def snooze(self, notification_id: str, duration_minutes: int) -> bool:
        """Snooze notification"""
        notification = self.storage.get_notification(notification_id)
        if not notification:
            return False
        
        notification.status = NotificationStatus.SNOOZED.value
        notification.snoozed_until = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
        self.storage.update_notification(notification)
        
        return True
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        return self.storage.delete_notification(notification_id)
    
    def list_notifications(self, **kwargs) -> List[Notification]:
        """List notifications"""
        return self.storage.list_notifications(**kwargs)
    
    # =========================================================================
    # Template Operations
    # =========================================================================
    
    def create_template(self,
                       name: str,
                       title_template: str,
                       message_template: str,
                       priority: str = "medium",
                       channel: str = "terminal",
                       tags: Optional[List[str]] = None) -> str:
        """Create notification template"""
        # Extract variables from templates
        variables = list(set(
            re.findall(r'\{(\w+)\}', title_template + message_template)
        ))
        
        template = NotificationTemplate(
            name=name,
            title_template=title_template,
            message_template=message_template,
            priority=priority,
            channel=channel,
            tags=tags or [],
            variables=variables
        )
        
        return self.storage.add_template(template)
    
    def use_template(self, template_id: str, **kwargs) -> str:
        """Use template to create notification"""
        template = self.storage.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        notification = template.render(**kwargs)
        return self.storage.add_notification(notification)
    
    def list_templates(self) -> List[NotificationTemplate]:
        """List all templates"""
        return self.storage.list_templates()
    
    def delete_template(self, template_id: str) -> bool:
        """Delete template"""
        return self.storage.delete_template(template_id)
    
    # =========================================================================
    # Scheduling
    # =========================================================================
    
    def _is_quiet_hours(self) -> bool:
        """Check if currently in quiet hours"""
        schedule = self.config.get("schedule", {})
        start = schedule.get("quiet_hours_start", "22:00")
        end = schedule.get("quiet_hours_end", "08:00")
        
        now = datetime.now().time()
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        
        if start_time > end_time:  # Spans midnight
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time
    
    def _get_quiet_hours_end(self) -> str:
        """Get end of quiet hours"""
        schedule = self.config.get("schedule", {})
        end = schedule.get("quiet_hours_end", "08:00")
        today = datetime.now().date()
        end_time = datetime.strptime(end, "%H:%M").time()
        return datetime.combine(today, end_time).isoformat()
    
    def process_scheduled(self) -> List[str]:
        """Process scheduled notifications"""
        now = datetime.now()
        sent_ids = []
        
        for notification in self.storage.list_notifications(status="pending"):
            if notification.scheduled_at:
                try:
                    scheduled = datetime.fromisoformat(notification.scheduled_at)
                    if scheduled <= now:
                        if self.send_notification(notification.id):
                            sent_ids.append(notification.id)
                except Exception:
                    pass
            
            # Check snoozed notifications
            if notification.status == NotificationStatus.SNOOZED.value and notification.snoozed_until:
                try:
                    snoozed_until = datetime.fromisoformat(notification.snoozed_until)
                    if snoozed_until <= now:
                        notification.status = NotificationStatus.PENDING.value
                        notification.snoozed_until = None
                        self.storage.update_notification(notification)
                except Exception:
                    pass
        
        return sent_ids
    
    # =========================================================================
    # Statistics & Reports
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        notifications = self.storage.list_notifications(limit=1000)
        
        stats = {
            "total": len(notifications),
            "by_status": defaultdict(int),
            "by_priority": defaultdict(int),
            "by_source": defaultdict(int),
            "by_channel": defaultdict(int),
            "recent_24h": 0,
            "unread": 0
        }
        
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        
        for n in notifications:
            stats["by_status"][n.status] += 1
            stats["by_priority"][n.priority] += 1
            stats["by_source"][n.source] += 1
            stats["by_channel"][n.channel] += 1
            
            if n.status == NotificationStatus.PENDING.value:
                stats["unread"] += 1
            
            try:
                created = datetime.fromisoformat(n.created_at)
                if created > day_ago:
                    stats["recent_24h"] += 1
            except Exception:
                pass
        
        return stats
    
    def export_notifications(self, 
                            format: str = "json",
                            output_path: Optional[str] = None) -> str:
        """Export notifications to file"""
        notifications = self.storage.list_notifications(limit=1000)
        
        if format == "json":
            data = json.dumps([n.to_dict() for n in notifications], indent=2)
        elif format == "markdown":
            lines = ["# NotifyPilot Export\n"]
            for n in notifications:
                lines.append(f"## {n.title}")
                lines.append(f"- **Priority**: {n.priority}")
                lines.append(f"- **Status**: {n.status}")
                lines.append(f"- **Source**: {n.source}")
                lines.append(f"- **Created**: {n.created_at}")
                lines.append(f"\n{n.message}\n")
            data = "\n".join(lines)
        elif format == "html":
            lines = [
                "<!DOCTYPE html>",
                "<html><head><title>NotifyPilot Export</title>",
                "<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px}",
                ".notification{border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:5px}",
                ".critical{border-left:4px solid #e74c3c}",
                ".high{border-left:4px solid #e67e22}",
                ".medium{border-left:4px solid #f1c40f}",
                ".low{border-left:4px solid #2ecc71}",
                "</style></head><body>",
                "<h1>NotifyPilot Export</h1>"
            ]
            for n in notifications:
                lines.append(f'<div class="notification {n.priority}">')
                lines.append(f'<h3>{n.title}</h3>')
                lines.append(f'<p><strong>Priority:</strong> {n.priority} | ')
                lines.append(f'<strong>Status:</strong> {n.status} | ')
                lines.append(f'<strong>Source:</strong> {n.source}</p>')
                lines.append(f'<p>{n.message}</p>')
                lines.append(f'<small>Created: {n.created_at}</small>')
                lines.append('</div>')
            lines.append("</body></html>")
            data = "\n".join(lines)
        else:
            data = json.dumps([n.to_dict() for n in notifications], indent=2)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(data)
            return output_path
        
        return data
    
    # =========================================================================
    # Cleanup
    # =========================================================================
    
    def cleanup(self) -> int:
        """Clean up expired notifications"""
        return self.storage.cleanup_expired()

# ============================================================================
# TUI Dashboard
# ============================================================================

class NotifyPilotTUI:
    """Terminal User Interface Dashboard"""
    
    def __init__(self, engine: NotifyPilotEngine):
        self.engine = engine
        self.running = True
        self.current_view = "list"
        self.selected_index = 0
        self.notifications: List[Notification] = []
        self.filter_priority = None
        self.filter_status = None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if platform.system() == "Windows" else 'clear')
    
    def get_terminal_size(self) -> tuple:
        """Get terminal size"""
        try:
            return os.get_terminal_size()
        except Exception:
            return (80, 24)
    
    def draw_header(self):
        """Draw header"""
        width = self.get_terminal_size()[0]
        print(f"\033[1;36m{'='*width}\033[0m")
        print(f"\033[1;37m  🔔 NotifyPilot v{VERSION} - Intelligent Notification Manager\033[0m")
        print(f"\033[1;36m{'='*width}\033[0m\n")
    
    def draw_stats(self):
        """Draw statistics"""
        stats = self.engine.get_stats()
        print(f"\033[1;33m📊 Statistics:\033[0m")
        print(f"   Total: {stats['total']} | Unread: {stats['unread']} | Last 24h: {stats['recent_24h']}")
        print(f"   Priority: 🔴 Critical: {stats['by_priority']['critical']} | "
              f"🟠 High: {stats['by_priority']['high']} | "
              f"🟡 Medium: {stats['by_priority']['medium']} | "
              f"🟢 Low: {stats['by_priority']['low']}")
        print()
    
    def draw_notification_list(self):
        """Draw notification list"""
        self.notifications = self.engine.list_notifications(
            priority=self.filter_priority,
            status=self.filter_status,
            limit=50
        )
        
        if not self.notifications:
            print("\033[90m   No notifications found.\033[0m\n")
            return
        
        print(f"\033[1;33m📬 Notifications ({len(self.notifications)}):\033[0m\n")
        
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }
        
        status_icons = {
            "pending": "⏳",
            "sent": "✅",
            "read": "📖",
            "dismissed": "🗑️",
            "snoozed": "💤"
        }
        
        for i, n in enumerate(self.notifications[:20]):
            icon = priority_icons.get(n.priority, "⚪")
            status_icon = status_icons.get(n.status, "❓")
            
            # Highlight selected
            if i == self.selected_index:
                print(f"\033[7m  {icon} [{status_icon}] {n.title[:50]:<50} {n.created_at[:10]}\033[0m")
            else:
                print(f"  {icon} [{status_icon}] {n.title[:50]:<50} {n.created_at[:10]}")
        
        if len(self.notifications) > 20:
            print(f"\n  ... and {len(self.notifications) - 20} more")
    
    def draw_notification_detail(self, notification: Notification):
        """Draw notification detail"""
        self.clear_screen()
        self.draw_header()
        
        priority_colors = {
            "critical": "\033[91m",
            "high": "\033[93m",
            "medium": "\033[94m",
            "low": "\033[92m",
            "info": "\033[96m"
        }
        color = priority_colors.get(notification.priority, "")
        reset = "\033[0m"
        
        print(f"{color}{'─'*60}{reset}")
        print(f"{color}  📌 {notification.title}{reset}")
        print(f"{color}{'─'*60}{reset}\n")
        
        print(f"  🎯 Priority: {notification.priority.upper()}")
        print(f"  📍 Source: {notification.source}")
        print(f"  📢 Channel: {notification.channel}")
        print(f"  📊 Status: {notification.status}")
        print(f"  🕐 Created: {notification.created_at}")
        
        if notification.sent_at:
            print(f"  ✉️ Sent: {notification.sent_at}")
        if notification.scheduled_at:
            print(f"  ⏰ Scheduled: {notification.scheduled_at}")
        if notification.tags:
            print(f"  🏷️ Tags: {', '.join(notification.tags)}")
        
        print(f"\n{color}  Message:{reset}")
        print(f"  {notification.message}\n")
        
        print(f"{color}{'─'*60}{reset}")
        print("  [R] Read  [D] Dismiss  [S] Snooze  [X] Delete  [B] Back")
    
    def draw_help(self):
        """Draw help screen"""
        self.clear_screen()
        self.draw_header()
        
        print("\033[1;33m📖 Help & Commands:\033[0m\n")
        
        commands = [
            ("↑/↓", "Navigate notifications"),
            ("Enter", "View notification detail"),
            ("n", "Create new notification"),
            ("t", "Manage templates"),
            ("f", "Filter by priority"),
            ("s", "Filter by status"),
            ("c", "Clear all filters"),
            ("r", "Refresh list"),
            ("e", "Export notifications"),
            ("q", "Quit"),
        ]
        
        for key, desc in commands:
            print(f"  \033[1;37m{key:<10}\033[0m {desc}")
        
        print("\n\033[90mPress any key to go back...\033[0m")
    
    def draw_create_form(self):
        """Draw create notification form"""
        self.clear_screen()
        self.draw_header()
        
        print("\033[1;33m✨ Create New Notification:\033[0m\n")
        
        try:
            title = input("  Title: ").strip()
            if not title:
                return
            
            message = input("  Message: ").strip()
            if not message:
                message = title
            
            print("\n  Priority: [1] Critical  [2] High  [3] Medium  [4] Low  [5] Info")
            priority_choice = input("  Select (1-5) [default: 3]: ").strip()
            priorities = ["critical", "high", "medium", "low", "info"]
            priority = priorities[int(priority_choice) - 1] if priority_choice.isdigit() and 1 <= int(priority_choice) <= 5 else "medium"
            
            print("\n  Channel: [1] Terminal  [2] System  [3] Webhook")
            channel_choice = input("  Select (1-3) [default: 1]: ").strip()
            channels = ["terminal", "system", "webhook"]
            channel = channels[int(channel_choice) - 1] if channel_choice.isdigit() and 1 <= int(channel_choice) <= 3 else "terminal"
            
            tags_input = input("  Tags (comma-separated): ").strip()
            tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
            
            nid = self.engine.create_notification(
                title=title,
                message=message,
                priority=priority,
                channel=channel,
                tags=tags
            )
            
            send_now = input("\n  Send now? [Y/n]: ").strip().lower()
            if send_now != 'n':
                self.engine.send_notification(nid)
            
            print(f"\n  \033[92m✓ Notification created: {nid}\033[0m")
            input("  Press Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n  Cancelled.")
    
    def run(self):
        """Run TUI dashboard"""
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            while self.running:
                self.clear_screen()
                self.draw_header()
                self.draw_stats()
                self.draw_notification_list()
                
                print("\n\033[90m  [h] Help  [n] New  [f] Filter  [r] Refresh  [q] Quit\033[0m")
                
                # Read single key
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                if ch == 'q':
                    self.running = False
                elif ch == 'h':
                    self.draw_help()
                    sys.stdin.read(1)  # Wait for key
                elif ch == 'n':
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    self.draw_create_form()
                elif ch == 'r':
                    pass  # Refresh
                elif ch == 'f':
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print("\n  Filter by priority: [1] Critical [2] High [3] Medium [4] Low [5] Info [0] Clear")
                    choice = input("  Select: ").strip()
                    if choice == '0':
                        self.filter_priority = None
                    elif choice.isdigit() and 1 <= int(choice) <= 5:
                        priorities = ["critical", "high", "medium", "low", "info"]
                        self.filter_priority = priorities[int(choice) - 1]
                elif ch == 's':
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print("\n  Filter by status: [1] Pending [2] Sent [3] Read [4] Dismissed [0] Clear")
                    choice = input("  Select: ").strip()
                    if choice == '0':
                        self.filter_status = None
                    elif choice.isdigit() and 1 <= int(choice) <= 4:
                        statuses = ["pending", "sent", "read", "dismissed"]
                        self.filter_status = statuses[int(choice) - 1]
                elif ch == 'c':
                    self.filter_priority = None
                    self.filter_status = None
                elif ch == '\x1b':  # Arrow keys
                    ch2 = sys.stdin.read(2)
                    if ch2 == '[A':  # Up
                        self.selected_index = max(0, self.selected_index - 1)
                    elif ch2 == '[B':  # Down
                        self.selected_index = min(len(self.notifications) - 1, self.selected_index + 1)
                elif ch == '\r' or ch == '\n':  # Enter
                    if self.notifications and 0 <= self.selected_index < len(self.notifications):
                        self.draw_notification_detail(self.notifications[self.selected_index])
                        # Wait for action key
                        tty.setraw(fd)
                        action = sys.stdin.read(1)
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        
                        n = self.notifications[self.selected_index]
                        if action == 'r':
                            self.engine.mark_read(n.id)
                        elif action == 'd':
                            self.engine.dismiss(n.id)
                        elif action == 'x':
                            self.engine.delete_notification(n.id)
                            self.selected_index = max(0, self.selected_index - 1)
                        elif action == 's':
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            mins = input("  Snooze for (minutes): ").strip()
                            if mins.isdigit():
                                self.engine.snooze(n.id, int(mins))
        
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ============================================================================
# CLI Interface
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog="notifypilot",
        description="🔔 NotifyPilot - Lightweight Terminal Intelligent Notification Management Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  notifypilot send "Build Complete" "All tests passed" -p high
  notifypilot list --priority critical
  notifypilot tui
  notifypilot stats
  notifypilot template create deploy "Deploy {env}" "Deployment to {env} completed"
  notifypilot export --format html --output report.html
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Send command
    send_parser = subparsers.add_parser("send", help="Send a notification")
    send_parser.add_argument("title", help="Notification title")
    send_parser.add_argument("message", help="Notification message")
    send_parser.add_argument("-p", "--priority", choices=["critical", "high", "medium", "low", "info"],
                            default="medium", help="Priority level")
    send_parser.add_argument("-s", "--source", default="cli", help="Notification source")
    send_parser.add_argument("-c", "--channel", choices=["terminal", "system", "webhook"],
                            default="terminal", help="Notification channel")
    send_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    send_parser.add_argument("--schedule", help="Schedule time (ISO format)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List notifications")
    list_parser.add_argument("-p", "--priority", help="Filter by priority")
    list_parser.add_argument("-s", "--status", help="Filter by status")
    list_parser.add_argument("--source", help="Filter by source")
    list_parser.add_argument("-l", "--limit", type=int, default=20, help="Limit results")
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Mark notification as read")
    read_parser.add_argument("id", help="Notification ID")
    
    # Dismiss command
    dismiss_parser = subparsers.add_parser("dismiss", help="Dismiss notification")
    dismiss_parser.add_argument("id", help="Notification ID")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete notification")
    delete_parser.add_argument("id", help="Notification ID")
    
    # Snooze command
    snooze_parser = subparsers.add_parser("snooze", help="Snooze notification")
    snooze_parser.add_argument("id", help="Notification ID")
    snooze_parser.add_argument("-d", "--duration", type=int, default=30, help="Duration in minutes")
    
    # Template commands
    template_parser = subparsers.add_parser("template", help="Template management")
    template_parser.add_argument("action", choices=["create", "list", "delete", "use"])
    template_parser.add_argument("name", nargs="?", help="Template name")
    template_parser.add_argument("--title", help="Title template")
    template_parser.add_argument("--message", help="Message template")
    template_parser.add_argument("-p", "--priority", default="medium")
    template_parser.add_argument("-c", "--channel", default="terminal")
    template_parser.add_argument("-v", "--vars", help="Variables as key=value,...")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export notifications")
    export_parser.add_argument("-f", "--format", choices=["json", "markdown", "html"],
                              default="json", help="Export format")
    export_parser.add_argument("-o", "--output", help="Output file path")
    
    # TUI command
    subparsers.add_parser("tui", help="Launch TUI dashboard")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("action", choices=["show", "set", "reset"])
    config_parser.add_argument("key", nargs="?", help="Config key")
    config_parser.add_argument("value", nargs="?", help="Config value")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up expired notifications")
    
    return parser

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    engine = NotifyPilotEngine()
    
    if args.command == "send":
        tags = args.tags.split(",") if args.tags else []
        nid = engine.create_notification(
            title=args.title,
            message=args.message,
            priority=args.priority,
            source=args.source,
            channel=args.channel,
            tags=tags,
            scheduled_at=args.schedule
        )
        
        if not args.schedule:
            engine.send_notification(nid)
        
        print(f"✓ Notification created: {nid}")
        return 0
    
    elif args.command == "list":
        notifications = engine.list_notifications(
            priority=args.priority,
            status=args.status,
            source=args.source,
            limit=args.limit
        )
        
        if not notifications:
            print("No notifications found.")
            return 0
        
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }
        
        for n in notifications:
            icon = priority_icons.get(n.priority, "⚪")
            print(f"{icon} [{n.id}] {n.title}")
            print(f"   Status: {n.status} | Created: {n.created_at[:19]}")
            print(f"   {n.message[:60]}...")
            print()
        
        return 0
    
    elif args.command == "read":
        if engine.mark_read(args.id):
            print(f"✓ Notification {args.id} marked as read")
            return 0
        print(f"✗ Notification not found: {args.id}")
        return 1
    
    elif args.command == "dismiss":
        if engine.dismiss(args.id):
            print(f"✓ Notification {args.id} dismissed")
            return 0
        print(f"✗ Notification not found: {args.id}")
        return 1
    
    elif args.command == "delete":
        if engine.delete_notification(args.id):
            print(f"✓ Notification {args.id} deleted")
            return 0
        print(f"✗ Notification not found: {args.id}")
        return 1
    
    elif args.command == "snooze":
        if engine.snooze(args.id, args.duration):
            print(f"✓ Notification {args.id} snoozed for {args.duration} minutes")
            return 0
        print(f"✗ Notification not found: {args.id}")
        return 1
    
    elif args.command == "template":
        if args.action == "create":
            if not args.name or not args.title or not args.message:
                print("Usage: notifypilot template create <name> --title <template> --message <template>")
                return 1
            tid = engine.create_template(
                name=args.name,
                title_template=args.title,
                message_template=args.message,
                priority=args.priority,
                channel=args.channel
            )
            print(f"✓ Template created: {tid}")
            return 0
        
        elif args.action == "list":
            templates = engine.list_templates()
            for t in templates:
                print(f"[{t.id}] {t.name}")
                print(f"   Title: {t.title_template}")
                print(f"   Variables: {', '.join(t.variables) if t.variables else 'None'}")
                print()
            return 0
        
        elif args.action == "delete":
            if engine.delete_template(args.name):
                print(f"✓ Template deleted: {args.name}")
                return 0
            print(f"✗ Template not found: {args.name}")
            return 1
        
        elif args.action == "use":
            if not args.name or not args.vars:
                print("Usage: notifypilot template use <template_id> -v key=value,...")
                return 1
            vars_dict = dict(v.split("=") for v in args.vars.split(","))
            nid = engine.use_template(args.name, **vars_dict)
            print(f"✓ Notification created from template: {nid}")
            return 0
    
    elif args.command == "stats":
        stats = engine.get_stats()
        print("📊 NotifyPilot Statistics\n")
        print(f"Total Notifications: {stats['total']}")
        print(f"Unread: {stats['unread']}")
        print(f"Last 24 Hours: {stats['recent_24h']}")
        print("\nBy Priority:")
        for p, count in stats['by_priority'].items():
            print(f"  {p}: {count}")
        print("\nBy Status:")
        for s, count in stats['by_status'].items():
            print(f"  {s}: {count}")
        return 0
    
    elif args.command == "export":
        result = engine.export_notifications(format=args.format, output_path=args.output)
        if args.output:
            print(f"✓ Exported to: {result}")
        else:
            print(result)
        return 0
    
    elif args.command == "tui":
        tui = NotifyPilotTUI(engine)
        tui.run()
        return 0
    
    elif args.command == "config":
        if args.action == "show":
            print(json.dumps(engine.config, indent=2))
            return 0
        elif args.action == "set":
            if not args.key or not args.value:
                print("Usage: notifypilot config set <key> <value>")
                return 1
            # Simple key=value setting
            keys = args.key.split(".")
            config = engine.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            try:
                config[keys[-1]] = json.loads(args.value)
            except json.JSONDecodeError:
                config[keys[-1]] = args.value
            engine._save_config()
            print(f"✓ Config updated: {args.key} = {args.value}")
            return 0
        elif args.action == "reset":
            engine.config = DEFAULT_CONFIG.copy()
            engine._save_config()
            print("✓ Config reset to defaults")
            return 0
    
    elif args.command == "cleanup":
        count = engine.cleanup()
        print(f"✓ Cleaned up {count} expired notifications")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

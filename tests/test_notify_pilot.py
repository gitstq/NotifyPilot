#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotifyPilot Test Suite
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notify_pilot import (
    NotifyPilotEngine,
    Notification,
    NotificationTemplate,
    PriorityEngine,
    NotificationStorage,
    Priority,
    NotificationStatus,
    DEFAULT_CONFIG
)


class TestPriorityEngine(unittest.TestCase):
    """Test priority calculation engine"""
    
    def test_critical_keywords(self):
        """Test critical keyword detection"""
        notification = Notification(
            title="URGENT: Server Down",
            message="Emergency: Critical system failure"
        )
        score = PriorityEngine.calculate(notification, DEFAULT_CONFIG)
        self.assertGreaterEqual(score, 80)
    
    def test_high_keywords(self):
        """Test high priority keyword detection"""
        notification = Notification(
            title="Important Update",
            message="Warning: Action required"
        )
        score = PriorityEngine.calculate(notification, DEFAULT_CONFIG)
        self.assertGreaterEqual(score, 60)
    
    def test_low_keywords(self):
        """Test low priority keyword detection"""
        notification = Notification(
            title="FYI Update",
            message="Just a notice for you"
        )
        score = PriorityEngine.calculate(notification, DEFAULT_CONFIG)
        self.assertLess(score, 60)
    
    def test_source_weighting(self):
        """Test source-based priority weighting"""
        n1 = Notification(title="Test", message="Test", source="system")
        n2 = Notification(title="Test", message="Test", source="chat")
        
        score1 = PriorityEngine.calculate(n1, DEFAULT_CONFIG)
        score2 = PriorityEngine.calculate(n2, DEFAULT_CONFIG)
        
        self.assertGreater(score1, score2)
    
    def test_priority_level_determination(self):
        """Test priority level from score"""
        self.assertEqual(PriorityEngine.get_priority_level(90, DEFAULT_CONFIG), Priority.CRITICAL)
        self.assertEqual(PriorityEngine.get_priority_level(70, DEFAULT_CONFIG), Priority.HIGH)
        self.assertEqual(PriorityEngine.get_priority_level(50, DEFAULT_CONFIG), Priority.MEDIUM)
        self.assertEqual(PriorityEngine.get_priority_level(30, DEFAULT_CONFIG), Priority.LOW)


class TestNotificationStorage(unittest.TestCase):
    """Test notification storage"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = DEFAULT_CONFIG.copy()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_add_notification(self):
        """Test adding notification"""
        storage = NotificationStorage(self.config)
        notification = Notification(
            title="Test",
            message="Test message"
        )
        nid = storage.add_notification(notification)
        self.assertIsNotNone(nid)
        self.assertEqual(storage.get_notification(nid).title, "Test")
    
    def test_update_notification(self):
        """Test updating notification"""
        storage = NotificationStorage(self.config)
        notification = Notification(title="Test", message="Test")
        nid = storage.add_notification(notification)
        
        notification.status = NotificationStatus.READ.value
        storage.update_notification(notification)
        
        updated = storage.get_notification(nid)
        self.assertEqual(updated.status, NotificationStatus.READ.value)
    
    def test_delete_notification(self):
        """Test deleting notification"""
        storage = NotificationStorage(self.config)
        notification = Notification(title="Test", message="Test")
        nid = storage.add_notification(notification)
        
        self.assertTrue(storage.delete_notification(nid))
        self.assertIsNone(storage.get_notification(nid))
    
    def test_list_notifications(self):
        """Test listing notifications"""
        storage = NotificationStorage(self.config)
        
        for i in range(5):
            storage.add_notification(Notification(
                title=f"Test {i}",
                message=f"Message {i}",
                priority="high" if i < 2 else "low"
            ))
        
        all_notifications = storage.list_notifications()
        self.assertEqual(len(all_notifications), 5)
        
        high_priority = storage.list_notifications(priority="high")
        self.assertEqual(len(high_priority), 2)
    
    def test_template_operations(self):
        """Test template operations"""
        storage = NotificationStorage(self.config)
        
        template = NotificationTemplate(
            name="deploy",
            title_template="Deploy {env}",
            message_template="Deployed to {env}"
        )
        tid = storage.add_template(template)
        
        self.assertIsNotNone(storage.get_template(tid))
        self.assertEqual(len(storage.list_templates()), 1)
        
        self.assertTrue(storage.delete_template(tid))
        self.assertIsNone(storage.get_template(tid))


class TestNotifyPilotEngine(unittest.TestCase):
    """Test main engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.engine = NotifyPilotEngine()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_create_notification(self):
        """Test creating notification"""
        nid = self.engine.create_notification(
            title="Test Notification",
            message="This is a test",
            priority="high"
        )
        self.assertIsNotNone(nid)
    
    def test_list_notifications(self):
        """Test listing notifications"""
        self.engine.create_notification("Test 1", "Message 1")
        self.engine.create_notification("Test 2", "Message 2")
        
        notifications = self.engine.list_notifications()
        self.assertEqual(len(notifications), 2)
    
    def test_mark_read(self):
        """Test marking notification as read"""
        nid = self.engine.create_notification("Test", "Message")
        self.assertTrue(self.engine.mark_read(nid))
        
        notification = self.engine.storage.get_notification(nid)
        self.assertEqual(notification.status, NotificationStatus.READ.value)
    
    def test_dismiss(self):
        """Test dismissing notification"""
        nid = self.engine.create_notification("Test", "Message")
        self.assertTrue(self.engine.dismiss(nid))
        
        notification = self.engine.storage.get_notification(nid)
        self.assertEqual(notification.status, NotificationStatus.DISMISSED.value)
    
    def test_snooze(self):
        """Test snoozing notification"""
        nid = self.engine.create_notification("Test", "Message")
        self.assertTrue(self.engine.snooze(nid, 30))
        
        notification = self.engine.storage.get_notification(nid)
        self.assertEqual(notification.status, NotificationStatus.SNOOZED.value)
        self.assertIsNotNone(notification.snoozed_until)
    
    def test_delete(self):
        """Test deleting notification"""
        nid = self.engine.create_notification("Test", "Message")
        self.assertTrue(self.engine.delete_notification(nid))
        self.assertIsNone(self.engine.storage.get_notification(nid))
    
    def test_template_workflow(self):
        """Test template workflow"""
        tid = self.engine.create_template(
            name="deploy",
            title_template="Deploy {env}",
            message_template="Deployed to {env}",
            priority="high"
        )
        self.assertIsNotNone(tid)
        
        nid = self.engine.use_template(tid, env="production")
        self.assertIsNotNone(nid)
        
        notification = self.engine.storage.get_notification(nid)
        self.assertEqual(notification.title, "Deploy production")
    
    def test_stats(self):
        """Test statistics"""
        self.engine.create_notification("Test 1", "Message 1", priority="high")
        self.engine.create_notification("Test 2", "Message 2", priority="low")
        
        stats = self.engine.get_stats()
        self.assertEqual(stats["total"], 2)
        self.assertIn("high", stats["by_priority"])
        self.assertIn("low", stats["by_priority"])
    
    def test_export_json(self):
        """Test JSON export"""
        self.engine.create_notification("Test", "Message")
        export = self.engine.export_notifications(format="json")
        
        data = json.loads(export)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
    
    def test_export_markdown(self):
        """Test Markdown export"""
        self.engine.create_notification("Test", "Message")
        export = self.engine.export_notifications(format="markdown")
        
        self.assertIn("# NotifyPilot Export", export)
        self.assertIn("Test", export)
    
    def test_export_html(self):
        """Test HTML export"""
        self.engine.create_notification("Test", "Message")
        export = self.engine.export_notifications(format="html")
        
        self.assertIn("<!DOCTYPE html>", export)
        self.assertIn("Test", export)


class TestNotificationModel(unittest.TestCase):
    """Test notification data model"""
    
    def test_notification_creation(self):
        """Test notification creation"""
        n = Notification(
            title="Test",
            message="Test message",
            priority="high"
        )
        
        self.assertIsNotNone(n.id)
        self.assertEqual(n.title, "Test")
        self.assertEqual(n.priority, "high")
        self.assertEqual(n.status, NotificationStatus.PENDING.value)
    
    def test_notification_to_dict(self):
        """Test notification serialization"""
        n = Notification(title="Test", message="Message")
        d = n.to_dict()
        
        self.assertIn("id", d)
        self.assertIn("title", d)
        self.assertEqual(d["title"], "Test")
    
    def test_notification_from_dict(self):
        """Test notification deserialization"""
        data = {
            "id": "test123",
            "title": "Test",
            "message": "Message",
            "priority": "high",
            "status": "pending",
            "source": "manual",
            "channel": "terminal",
            "tags": [],
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "actions": []
        }
        
        n = Notification.from_dict(data)
        self.assertEqual(n.id, "test123")
        self.assertEqual(n.title, "Test")


class TestTemplateModel(unittest.TestCase):
    """Test template data model"""
    
    def test_template_creation(self):
        """Test template creation"""
        t = NotificationTemplate(
            name="deploy",
            title_template="Deploy {env}",
            message_template="Deployed to {env}"
        )
        
        self.assertEqual(t.name, "deploy")
        self.assertIn("env", t.variables)
    
    def test_template_render(self):
        """Test template rendering"""
        t = NotificationTemplate(
            name="deploy",
            title_template="Deploy {env}",
            message_template="Deployed to {env} with version {version}",
            priority="high"
        )
        
        n = t.render(env="production", version="v1.0.0")
        
        self.assertEqual(n.title, "Deploy production")
        self.assertEqual(n.message, "Deployed to production with version v1.0.0")
        self.assertEqual(n.priority, "high")


if __name__ == "__main__":
    unittest.main(verbosity=2)

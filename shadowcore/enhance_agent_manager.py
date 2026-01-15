#!/usr/bin/env python3
"""
Enhance your Agent Manager with real scheduling and ACL
"""

import json
import time
from datetime import datetime

# Enhanced task scheduler
class EnhancedAgentManager:
    def __init__(self):
        self.task_queue = []
        self.acl_rules = {
            "analysts": ["read", "analyze"],
            "admins": ["read", "write", "delete", "schedule"],
            "automation": ["read", "analyze", "schedule"]
        }
    
    def schedule_analysis(self, ioc, priority="medium", requester="automation"):
        """Enhanced scheduling with ACL"""
        task_id = f"task_{int(time.time())}_{hash(ioc) % 1000:04d}"
        
        task = {
            "id": task_id,
            "ioc": ioc,
            "type": self._detect_ioc_type(ioc),
            "priority": priority,
            "requester": requester,
            "scheduled_at": datetime.now().isoformat(),
            "status": "queued",
            "assigned_workers": self._assign_workers(ioc),
            "acl": self._get_acl_for_requester(requester)
        }
        
        self.task_queue.append(task)
        return task
    
    def _assign_workers(self, ioc):
        """Intelligently assign workers based on IOC type"""
        ioc_type = self._detect_ioc_type(ioc)
        
        workers = {
            "ip": ["geo_lookup", "reputation_check", "port_scan"],
            "domain": ["dns_resolution", "whois_lookup", "certificate_check"],
            "hash": ["virustotal_check", "malware_analysis", "sandbox_submit"],
            "url": ["content_fetch", "phishing_check", "screenshot"]
        }
        
        return workers.get(ioc_type, ["general_analysis"])
    
    def _detect_ioc_type(self, ioc):
        if ioc.count('.') == 3 and all(p.isdigit() for p in ioc.split('.')):
            return "ip"
        elif '.' in ioc and not ioc.startswith('http'):
            return "domain"
        elif ioc.startswith('http'):
            return "url"
        elif len(ioc) in [32, 40, 64]:
            return "hash"
        return "unknown"
    
    def _get_acl_for_requester(self, requester):
        return self.acl_rules.get(requester, ["read"])

# Test it
manager = EnhancedAgentManager()
task = manager.schedule_analysis("23.95.44.80", priority="high", requester="automation")

print("✅ Enhanced Agent Manager")
print(f"Task ID: {task['id']}")
print(f"Assigned Workers: {', '.join(task['assigned_workers'])}")
print(f"ACL: {task['acl']}")

# Save task to queue
with open("/opt/shadowcore/task_queue.json", "w") as f:
    json.dump(manager.task_queue, f, indent=2)

print(f"\n💾 Task saved to /opt/shadowcore/task_queue.json")

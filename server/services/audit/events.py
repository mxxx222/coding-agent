from typing import Dict, Any, Optional
from datetime import datetime
import json
import os


class AuditEvents:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.path.join("data", "audit", "events.log")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def emit(self, event_type: str, actor: str, payload: Dict[str, Any]):
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            "actor": actor,
            "payload": payload,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")



from datetime import datetime
import json
import re

def create_event(event: str, content: str = None):
    data = {
        'timestamp': datetime.now().isoformat(),
        'content': content
    }
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {json_data}\n\n"

def parse_sse_event(sse_string):
    event_match = re.search(r'event:\s*(.+)', sse_string)
    event = event_match.group(1).strip() if event_match else None
    
    data_match = re.search(r'data:\s*(.+)', sse_string)
    data_str = data_match.group(1).strip() if data_match else None
    
    data = json.loads(data_str) if data_str else None
    
    return event, data
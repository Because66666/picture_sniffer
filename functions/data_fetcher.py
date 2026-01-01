import requests
from typing import List, Dict, Any, Optional


class DataFetcher:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def get_group_list(self) -> Dict[str, Any]:
        url = f"{self.base_url}/get_group_list"
        response = requests.post(url, headers={"Authorization": self.token})
        return response.json()

    def get_group_message_history(
        self,
        group_id: str,
        message_seq: str,
        count: int = 100
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/get_group_msg_history"
        payload = {
            "group_id": group_id,
            "count": count,
            "reverse_order": False
        }
        if message_seq:
            payload["message_seq"] = message_seq
        response = requests.post(url, headers={"Authorization": self.token}, json=payload)
        return response.json()

    def get_new_messages(
        self,
        group_id: str,
        last_message_id: str,
        batch_size: int = 15
    ) -> List[Dict[str, Any]]:
        all_messages = []
        current_seq = last_message_id
        
        while True:
            result = self.get_group_message_history(group_id, current_seq, batch_size)
            
            if result.get("status") != "ok":
                break
            
            messages = result.get("data", {}).get("messages", [])
            if not messages:
                break
            
            all_messages.extend(messages)
            
            for msg in messages:
                msg_id = str(msg.get("message_id", ""))
                if msg_id == last_message_id:
                    return all_messages
            
            current_seq = str(messages[-1].get("message_seq", ""))
            
            if len(messages) < batch_size:
                break
        
        return all_messages

    def get_initial_messages(self, group_id: str, count: int = 100) -> List[Dict[str, Any]]:
        result = self.get_group_message_history(group_id, "", count)
        
        if result.get("status") != "ok":
            return []
        
        return result.get("data", {}).get("messages", [])

    def extract_image_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        image_messages = []
        
        for msg in messages:
            message_list = msg.get("message", [])
            for item in message_list:
                if item.get("type") == "image":
                    image_data = item.get("data", {})
                    image_messages.append({
                        "message_id": str(msg.get("message_id", "")),
                        "group_id": str(msg.get("group_id", "")),
                        "url": image_data.get("url", ""),
                        "file": image_data.get("file", ""),
                        "time": str(msg.get("time", ""))
                    })
                    break
        
        return image_messages

    def fetch_message_body(self, message_id: str) -> Optional[str]:
        url = f"{self.base_url}/get_msg"
        payload = {
            "message_id": message_id
        }
        response = requests.post(url, headers={"Authorization": self.token}, json=payload)
        data = response.json().get("data", {})
        return data.get("message", "")

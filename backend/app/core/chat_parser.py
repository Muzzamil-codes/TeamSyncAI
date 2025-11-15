"""
WhatsApp Chat Parser - Extracts messages from WhatsApp text exports
"""

import os
import re
from typing import List, Dict


def parse_whatsapp_chat(file_path: str) -> List[Dict[str, str]]:
    """Parse WhatsApp chat export file.
    
    Args:
        file_path: Path to the .txt file exported from WhatsApp
        
    Returns:
        List of message dicts with 'datetime', 'author', and 'text' keys
        
    Raises:
        FileNotFoundError: If the chat file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Chat file not found: {file_path}")
    
    # Regex patterns for parsing
    user_pattern = r"^(?P<datetime>[\d\/\-\.,\s:APMpm]+?)\s*-\s*(?P<author>[^:]+?):\s*(?P<text>.*)$"
    system_pattern = r"^(?P<datetime>[\d\/\-\.,\s:APMpm]+?)\s*-\s*(?P<text>[^:]+)$"
    
    messages = []
    current_message = None
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            
            # Try user message pattern
            user_match = re.match(user_pattern, line)
            if user_match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                current_message = {
                    "datetime": user_match.group("datetime"),
                    "author": user_match.group("author"),
                    "text": user_match.group("text"),
                }
                continue
            
            # Try system message pattern
            system_match = re.match(system_pattern, line)
            if system_match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                current_message = {
                    "datetime": system_match.group("datetime"),
                    "author": "System",
                    "text": system_match.group("text"),
                }
                continue
            
            # Multi-line continuation
            if current_message and line.strip():
                current_message["text"] += "\n" + line
    
    # Don't forget the last message
    if current_message:
        messages.append(current_message)
    
    return messages


def chat_to_string(messages: List[Dict[str, str]]) -> str:
    """Convert parsed messages back to chat string format.
    
    Args:
        messages: List of message dicts
        
    Returns:
        Formatted chat text
    """
    lines = []
    for msg in messages:
        if msg["author"] == "System":
            lines.append(f"{msg['datetime']} - {msg['text']}")
        else:
            lines.append(f"{msg['datetime']} - {msg['author']}: {msg['text']}")
    
    return "\n".join(lines)

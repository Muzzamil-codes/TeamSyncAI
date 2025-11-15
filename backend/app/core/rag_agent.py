"""
RAG Agent Core Logic - Backend Integration
Uses LangChain and Google Gemini for WhatsApp chat and document analysis
"""

import os
from typing import List, Optional, Generator, Dict
from datetime import datetime
from dotenv import load_dotenv
from collections import deque

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


class ChatAnalysisAgent:
    """Main RAG Agent for analyzing chat and document content."""
    
    def __init__(self, gemini_model: str = "gemini-2.5-flash"):
        """Initialize the chat analysis agent."""
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.model_name = gemini_model
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.7,
            streaming=True,
        )
        
        # Initialize conversation memory buffer (keep last 10 exchanges)
        self.memory_buffer: deque = deque(maxlen=10)
        self.current_chat_content = ""
    
    def _format_chat_history(self) -> str:
        """Format memory buffer into a string for context."""
        if not self.memory_buffer:
            return ""
        
        history = []
        for msg in self.memory_buffer:
            if msg["role"] == "user":
                history.append(f"User: {msg['content']}")
            else:
                history.append(f"Assistant: {msg['content']}")
        
        return "\n".join(history)
    
    def analyze_chat(self, chat_content: str, question: str) -> Generator[str, None, None]:
        """Analyze WhatsApp chat content and answer a question with streaming.
        
        Args:
            chat_content: The WhatsApp chat text
            question: User's question about the chat
            
        Yields:
            Streamed response chunks from Gemini
        """
        # Store current chat content for context
        self.current_chat_content = chat_content
        
        # Get chat history for context awareness
        chat_history = self._format_chat_history()
        
        # Check if we have actual chat content to analyze
        has_chat_data = chat_content and chat_content.strip() and len(chat_content.strip()) > 10
        
        # Create the prompt with memory context
        history_context = f"\nPrevious conversation:\n{chat_history}\n" if chat_history else ""
        
        if has_chat_data:
            # Prompt when chat data is available
            prompt = PromptTemplate(
                input_variables=["chat_content", "question", "history"],
                template="""You are TeamSync, a helpful AI assistant that analyzes WhatsApp group chats and helps with productivity.

{history}

Based on the following WhatsApp chat data:

<chat>
{chat_content}
</chat>

User: {question}

Answer concisely and naturally. If the question is not related to the chat, you can answer it normally but try to bring it back to the chat analysis if relevant.""",
            )
        else:
            # Prompt when no chat data is available
            prompt = PromptTemplate(
                input_variables=["chat_content", "question", "history"],
                template="""You are TeamSync, a helpful productivity AI assistant.

{history}

User: {question}

Note: No WhatsApp chat data has been uploaded yet. If the user asks anything about analyzing chats, extracting todos, or calendar events from messages, inform them that they need to upload a chat file first using the Upload section. Otherwise, feel free to have a normal conversation and help them with their questions.""",
            )
        
        chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Stream the response
        full_response = ""
        for chunk in chain.stream({"chat_content": chat_content, "question": question, "history": history_context}):
            full_response += chunk
            yield chunk
        
        # Store in memory buffer after streaming completes
        self.memory_buffer.append({"role": "user", "content": question})
        self.memory_buffer.append({"role": "assistant", "content": full_response})
    
    def extract_todos(self, chat_content: str) -> tuple[List[str], List[dict]]:
        """Extract action items, todos, and upcoming dates from chat content.
        
        Args:
            chat_content: The WhatsApp chat text
            
        Returns:
            Tuple of (todos list, important_dates list with only future dates)
        """
        from datetime import datetime
        import re
        
        # Extract todos
        todo_prompt = PromptTemplate(
            input_variables=["chat_content"],
            template="""You are TeamSyc, a productivity AI assistant.

Analyze the following WhatsApp group chat and identify all action items, tasks, and decisions:

<chat>
{chat_content}
</chat>

Please extract and list all actionable items. Format each as a clear todo starting with a dash (-):

- Item 1
- Item 2
- etc.

If no action items found, respond with: "No action items found."

Todo List:""",
        )
        
        todo_chain = (
            todo_prompt
            | self.llm
            | StrOutputParser()
        )
        
        todo_response = todo_chain.invoke({"chat_content": chat_content})
        
        # Parse todos
        todos = []
        for line in todo_response.strip().split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line[0].isdigit()):
                todos.append(line)
        
        # Extract dates directly from chat content using regex patterns
        important_dates = []
        today = datetime.now().date()
        date_set = set()  # To avoid duplicates
        
        # Pattern 1: Explicit dates in chat messages like [11/15/25, 2:30 PM]
        chat_date_pattern = r'\[(\d{1,2})/(\d{1,2})/(\d{2}),\s*(\d{1,2}):(\d{2})\s*(AM|PM)\]'
        
        # Pattern 2: Dates mentioned in text (various formats)
        # Format: November 15th, November 15, 11/15/25, 11-15-25, 2025-11-15, etc.
        text_date_patterns = [
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})', 'mdy'),  # November 15th, 2025
            (r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', 'dmy'),  # 15/11/25 or 15-11-2025
            (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', 'ymd'),  # 2025-11-15
        ]
        
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        def parse_date(match_obj, pattern_type):
            """Parse date from regex match."""
            try:
                if pattern_type == 'mdy':
                    month_name, day, year = match_obj.groups()
                    month = months[month_name.lower()]
                    year = int(year)
                    day = int(day)
                    return datetime(year, month, day).date()
                elif pattern_type == 'dmy':
                    day, month, year = match_obj.groups()
                    year = int(year)
                    if year < 100:
                        year += 2000
                    return datetime(year, int(month), int(day)).date()
                elif pattern_type == 'ymd':
                    year, month, day = match_obj.groups()
                    return datetime(int(year), int(month), int(day)).date()
            except (ValueError, IndexError):
                return None
            return None
        
        # Find all dates in chat content
        found_dates = {}  # {date_str: event_info}
        
        # First, extract dates from messages
        lines = chat_content.split('\n')
        for line in lines:
            # Extract message timestamp
            timestamp_match = re.search(chat_date_pattern, line)
            if timestamp_match:
                month, day, year, hour, minute, meridiem = timestamp_match.groups()
                try:
                    year = int(year)
                    if year < 100:
                        year += 2000
                    msg_date = datetime(year, int(month), int(day)).date()
                    if msg_date >= today:
                        date_key = msg_date.strftime("%Y-%m-%d")
                        if date_key not in found_dates:
                            found_dates[date_key] = {
                                "date": date_key,
                                "events": [],
                                "description": "Message timestamp"
                            }
                except (ValueError, TypeError):
                    pass
            
            # Extract dates mentioned in message text
            for pattern, pattern_type in text_date_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    parsed_date = parse_date(match, pattern_type)
                    if parsed_date and parsed_date >= today:
                        date_key = parsed_date.strftime("%Y-%m-%d")
                        # Extract the text around the date as context
                        event_text = line.replace('[', '').replace(']', '').split(' - ', 1)[-1] if ' - ' in line else line
                        if date_key not in found_dates:
                            found_dates[date_key] = {
                                "date": date_key,
                                "events": [],
                                "description": event_text[:100]  # First 100 chars as description
                            }
                        if event_text not in found_dates[date_key]["events"]:
                            found_dates[date_key]["events"].append(event_text[:80])
        
        # Also ask AI to extract important dates with context
        dates_prompt = PromptTemplate(
            input_variables=["chat_content"],
            template="""You are TeamSyc, a productivity AI assistant.

Analyze the following WhatsApp group chat and extract all important dates, deadlines, and scheduled events mentioned:

<chat>
{chat_content}
</chat>

For each date/event found, provide in this exact format:
DATE: [date in YYYY-MM-DD format if possible, or "TBD" if unclear] | EVENT: [event name/description]

Examples:
DATE: 2025-11-15 | EVENT: Hackathon event
DATE: 2025-11-20 | EVENT: Project deadline
DATE: TBD | EVENT: Team meeting to be scheduled

Only include dates and events (Summarize what the event is about.) that are clearly mentioned. If no dates found, respond with: "No dates found."

Important Dates:""",
        )
        
        dates_chain = (
            dates_prompt
            | self.llm
            | StrOutputParser()
        )
        
        dates_response = dates_chain.invoke({"chat_content": chat_content})
        
        # Parse AI-extracted dates
        for line in dates_response.strip().split("\n"):
            line = line.strip()
            if "DATE:" in line and "EVENT:" in line:
                try:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        date_str = parts[0].replace("DATE:", "").strip()
                        event_str = parts[1].replace("EVENT:", "").strip()
                        
                        # Try to parse the date
                        if date_str != "TBD":
                            try:
                                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                                # Only include future dates
                                if event_date >= today:
                                    if date_str not in found_dates:
                                        found_dates[date_str] = {
                                            "date": date_str,
                                            "events": [],
                                            "description": event_str
                                        }
                                    else:
                                        found_dates[date_str]["description"] = event_str
                                        if event_str not in found_dates[date_str]["events"]:
                                            found_dates[date_str]["events"].append(event_str)
                            except ValueError:
                                # If date parsing fails, include with TBD
                                if event_str:
                                    found_dates[f"TBD_{len(found_dates)}"] = {
                                        "date": "TBD",
                                        "events": [event_str],
                                        "description": event_str
                                    }
                        else:
                            # Include TBD dates
                            if event_str:
                                found_dates[f"TBD_{len(found_dates)}"] = {
                                    "date": "TBD",
                                    "events": [event_str],
                                    "description": event_str
                                }
                except Exception:
                    continue
        
        # Convert found_dates dictionary to list format for response
        important_dates = []
        for date_key, date_info in sorted(found_dates.items()):
            # Combine all events for this date
            event_desc = " | ".join(date_info.get("events", [date_info.get("description", "")]))
            important_dates.append({
                "date": date_info["date"],
                "event": event_desc[:150] if event_desc else date_info.get("description", "Important date"),
                "description": date_info.get("description", "")
            })
        
        return todos if todos else [], important_dates if important_dates else []



# Global agent instance
_agent = None


def get_agent() -> ChatAnalysisAgent:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = ChatAnalysisAgent()
    return _agent

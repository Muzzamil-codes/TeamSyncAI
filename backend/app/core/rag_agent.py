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
        from datetime import datetime, timedelta
        import re
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting extraction for chat content ({len(chat_content)} chars)")
        
        today = datetime.now().date()
        logger.info(f"Today's date for extraction: {today}")
        
        # Single unified prompt to extract both todos AND dates
        unified_prompt = PromptTemplate(
            input_variables=["chat_content", "today_date"],
            template="""You are TeamSyc, a productivity AI assistant.

**Today's date is: {today_date}**

Analyze the following WhatsApp group chat and extract BOTH action items AND important dates/events:

<chat>
{chat_content}
</chat>

Provide your response in TWO sections:

=== TODOS ===
List all actionable items, tasks, and decisions. Format each as:
- Task description

If no action items found, write: "No action items found."

=== DATES ===
List all important dates, deadlines, and scheduled events. Format each as:
DATE: [date in YYYY-MM-DD format] | EVENT: [event description]

IMPORTANT for dates:
- Convert relative dates like "tomorrow", "next week", "next Monday" to actual dates using today's date ({today_date})
- Examples:
  * If today is 2025-11-15 and chat says "meeting tomorrow", write: DATE: 2025-11-16 | EVENT: Meeting
  * If today is 2025-11-15 and chat says "November 20", write: DATE: 2025-11-20 | EVENT: [event description]
- If date is unclear, write: DATE: TBD | EVENT: [event description]

If no dates found, write: "No dates found."

Now analyze the chat:""",
        )
        
        extraction_chain = (
            unified_prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("Calling LLM for unified extraction (todos + dates)...")
        extraction_response = extraction_chain.invoke({
            "chat_content": chat_content,
            "today_date": today.strftime("%Y-%m-%d")
        })
        logger.info(f"LLM response (first 500 chars): {extraction_response[:500]}...")
        
        # Parse the unified response
        todos = []
        found_dates = {}
        
        # Split response into sections
        sections = extraction_response.split("===")
        todo_section = ""
        dates_section = ""
        
        for i, section in enumerate(sections):
            if "TODOS" in section.upper():
                # Get content after this section marker
                if i + 1 < len(sections):
                    todo_section = sections[i + 1].split("===")[0] if "===" in sections[i + 1] else sections[i + 1]
                else:
                    # Content is in the same section after the marker
                    todo_section = section.split("TODOS", 1)[-1] if "TODOS" in section else ""
            elif "DATES" in section.upper():
                if i + 1 < len(sections):
                    dates_section = sections[i + 1]
                else:
                    dates_section = section.split("DATES", 1)[-1] if "DATES" in section else ""
        
        # Parse todos from section
        logger.info("Parsing todos from unified response...")
        for line in todo_section.strip().split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or (line and line[0].isdigit())):
                # Remove leading dash or number
                task_text = line.lstrip("-").lstrip("0123456789.").strip()
                if task_text and "no action items" not in task_text.lower():
                    # Determine priority from keywords
                    priority = "medium"
                    if any(keyword in task_text.lower() for keyword in ["urgent", "asap", "immediately", "critical", "high priority", "important"]):
                        priority = "high"
                    elif any(keyword in task_text.lower() for keyword in ["low priority", "later", "whenever", "optional"]):
                        priority = "low"
                    
                    todos.append({
                        "task": task_text,
                        "priority": priority
                    })
        
        logger.info(f"Extracted {len(todos)} todos from unified response")
        
        logger.info(f"Extracted {len(todos)} todos from unified response")
        
        # Parse dates from section
        logger.info("Parsing dates from unified response...")
        ai_extracted_count = 0
        
        for line in dates_section.strip().split("\n"):
            line = line.strip()
            if "DATE:" in line and "EVENT:" in line:
                try:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        date_str = parts[0].replace("DATE:", "").strip()
                        event_str = parts[1].replace("EVENT:", "").strip()
                        
                        logger.info(f"Processing extracted date: {date_str} | event: {event_str}")
                        
                        # Skip "no dates found" messages
                        if "no dates found" in date_str.lower() or "no dates found" in event_str.lower():
                            continue
                        
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
                                        ai_extracted_count += 1
                                    else:
                                        found_dates[date_str]["description"] = event_str
                                        if event_str not in found_dates[date_str]["events"]:
                                            found_dates[date_str]["events"].append(event_str)
                                else:
                                    logger.info(f"Skipping past date: {event_date}")
                            except ValueError as e:
                                logger.warning(f"Failed to parse date '{date_str}': {e}")
                                # If date parsing fails, try natural language parsing as fallback
                                try:
                                    from dateutil import parser as date_parser
                                    parsed_date = date_parser.parse(date_str, fuzzy=True).date()
                                    if parsed_date >= today:
                                        iso_date = parsed_date.strftime("%Y-%m-%d")
                                        found_dates[iso_date] = {
                                            "date": iso_date,
                                            "events": [event_str],
                                            "description": event_str
                                        }
                                        ai_extracted_count += 1
                                        logger.info(f"Parsed via dateutil: {date_str} → {iso_date}")
                                except:
                                    # Last resort: include with TBD
                                    if event_str:
                                        found_dates[f"TBD_{len(found_dates)}"] = {
                                            "date": "TBD",
                                            "events": [event_str],
                                            "description": event_str
                                        }
                                        logger.info(f"Stored as TBD: {event_str}")
                        else:
                            # Include TBD dates
                            if event_str:
                                found_dates[f"TBD_{len(found_dates)}"] = {
                                    "date": "TBD",
                                    "events": [event_str],
                                    "description": event_str
                                }
                except Exception as ex:
                    logger.error(f"Error parsing date line '{line}': {ex}")
                    continue
        
        logger.info(f"AI extracted {ai_extracted_count} valid dates from unified response")
        
        # Convert found_dates dictionary to list format for response
        important_dates = []
        for date_key, date_info in sorted(found_dates.items()):
            # Combine all events for this date
            event_desc = " | ".join(date_info.get("events", [date_info.get("description", "")]))
            important_dates.append({
                "date": date_info["date"],
                "title": event_desc[:150] if event_desc else date_info.get("description", "Important date"),
                "description": date_info.get("description", ""),
                "is_scheduled": date_info["date"] != "TBD"
            })
        
        logger.info(f"Extraction complete: {len(todos)} todos, {len(important_dates)} dates")
        return todos if todos else [], important_dates if important_dates else []



# Global agent instance
_agent = None


def get_agent() -> ChatAnalysisAgent:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = ChatAnalysisAgent()
    return _agent

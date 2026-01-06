import uuid
from datetime import datetime
from typing import Dict, Optional, List


class SessionManager:
    """
    Manages user chat sessions with in-memory storage

    Each session tracks:
    - Creation timestamp
    - Message history
    - Current active agent
    """

    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    def create_session(self) -> str:
        """
        Create a new chat session

        Returns:
            str: Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "current_agent": "personal"  # Always start with Personal Assistant
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session data by ID

        Args:
            session_id: Session identifier

        Returns:
            dict or None: Session data if exists, None otherwise
        """
        return self.sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session exists
        """
        return session_id in self.sessions

    def add_message(self, session_id: str, message: dict) -> bool:
        """
        Add a message to session history

        Args:
            session_id: Session identifier
            message: Message dict with keys: sender, text, agent, timestamp

        Returns:
            bool: True if successful, False if session doesn't exist
        """
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append(message)
            return True
        return False

    def get_conversation_history(self, session_id: str) -> List[dict]:
        """
        Get full conversation history for a session

        Args:
            session_id: Session identifier

        Returns:
            list: List of message dicts, or empty list if session doesn't exist
        """
        session = self.get_session(session_id)
        return session["messages"] if session else []

    def update_current_agent(self, session_id: str, agent: str) -> bool:
        """
        Update the currently active agent for a session

        Args:
            session_id: Session identifier
            agent: Agent name ("personal", "hr", "it")

        Returns:
            bool: True if successful, False if session doesn't exist
        """
        if session_id in self.sessions:
            self.sessions[session_id]["current_agent"] = agent
            return True
        return False

    def get_message_count(self, session_id: str) -> int:
        """
        Get number of messages in a session

        Args:
            session_id: Session identifier

        Returns:
            int: Message count, or 0 if session doesn't exist
        """
        session = self.get_session(session_id)
        return len(session["messages"]) if session else 0

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session was deleted, False if didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_all_sessions(self) -> Dict[str, dict]:
        """
        Get all sessions (for debugging/admin purposes)

        Returns:
            dict: All sessions
        """
        return self.sessions

    def get_session_count(self) -> int:
        """
        Get total number of sessions

        Returns:
            int: Number of active sessions
        """
        return len(self.sessions)

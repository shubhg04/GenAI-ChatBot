from datetime import datetime, timezone
from app_database import get_connection
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, session_id):
        self.session_id = session_id
    
    def default_history(self):
        return [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def load(self):
        default_history  = self.default_history()

        logger.info(f"memory_stage = load_start Session: {self.session_id}")       
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT role, content
                    FROM session_history
                    WHERE session_id = ?
                    ORDER BY id ASC
                """, (self.session_id,))
            
                rows = cursor.fetchall()

            if not rows:
                logger.info(
                    f"memory_stage = session_missing_using_default Session: {self.session_id} default_message_count: {len(default_history)}"
                )
                return default_history

            chat_history = []
            for row in rows:
                chat_history.append({
                    "role": row["role"],
                    "content": row["content"]
                })

            logger.info(
                f"memory_stage = load_done Session: {self.session_id} message_count: {len(chat_history)}"
            )
            return chat_history

        except Exception as error:
            logger.warning(
                f"memory_stage = load_failed Session: {self.session_id} error: {str(error)}"
            )
            logger.warning(
                f"memory_stage = load_fallback_default Session: {self.session_id} default_message_count: {len(default_history)}"
            )
            return default_history

    def save(self, chat_history):
        logger.info(
            f"memory_stage = save_start Session: {self.session_id} message_count: {len(chat_history)}"
        )

        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM session_history
                WHERE session_id = ?
            """, (self.session_id,))

            timestamp = datetime.now(timezone.utc).isoformat()

            for message in chat_history:
                cursor.execute("""
                    INSERT INTO session_history (session_id, role, content, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.session_id,
                    message["role"],
                    message["content"],
                    timestamp
                ))

            connection.commit()

        logger.info(
            f"memory_stage = save_done Session: {self.session_id} message_count: {len(chat_history)}"
        )

    def clear(self):
        default_history = self.default_history()

        logger.info(
            f"memory_stage = clear_start Session: {self.session_id}"
        )

        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM session_history
                WHERE session_id = ?
            """, (self.session_id,))

            timestamp = datetime.now(timezone.utc).isoformat()

            for message in default_history:
                cursor.execute("""
                    INSERT INTO session_history (session_id, role, content, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.session_id,
                    message["role"],
                    message["content"],
                    timestamp
                ))

            connection.commit()

        logger.info(
            f"memory_stage = clear_done Session: {self.session_id} message_count: {len(default_history)}"
        )

        return default_history
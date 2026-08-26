import psycopg

from server.config import DATABASE_URL


class ChatService:
    """
    Handles chat and message persistence
    using PostgreSQL.
    """

    def __init__(self):
        self.database_url = DATABASE_URL

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _get_connection(self):
        return psycopg.connect(self.database_url)

    # =========================================================
    # CREATE CHAT
    # =========================================================

    def create_chat(self, user_id=None, title="New Chat"):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO chats (
                        user_id,
                        title
                    )
                    VALUES (%s, %s)
                    RETURNING id, user_id, title, created_at, updated_at;
                    """,
                    (
                        user_id,
                        title
                    )
                )

                chat = cursor.fetchone()

            connection.commit()

        return {
            "id": str(chat[0]),
            "user_id": (
                str(chat[1])
                if chat[1] is not None
                else None
            ),
            "title": chat[2],
            "created_at": chat[3],
            "updated_at": chat[4]
        }

    # =========================================================
    # UPDATE CHAT TITLE
    # =========================================================

    def update_chat_title(self, chat_id, title):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE chats
                    SET
                        title = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING
                        id,
                        user_id,
                        title,
                        created_at,
                        updated_at;
                    """,
                    (
                        title,
                        chat_id
                    )
                )

                chat = cursor.fetchone()

            connection.commit()

        if chat is None:
            return None

        return {
            "id": str(chat[0]),
            "user_id": (
                str(chat[1])
                if chat[1] is not None
                else None
            ),
            "title": chat[2],
            "created_at": chat[3],
            "updated_at": chat[4]
        }

    # =========================================================
    # SAVE MESSAGE
    # =========================================================

    def save_message(self, chat_id, role, content):

        if role not in ["user", "assistant"]:

            raise ValueError(
                "Role must be 'user' or 'assistant'."
            )

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO messages (
                        chat_id,
                        role,
                        content
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        chat_id,
                        role,
                        content,
                        created_at;
                    """,
                    (
                        chat_id,
                        role,
                        content
                    )
                )

                message = cursor.fetchone()

                # Update chat activity
                cursor.execute(
                    """
                    UPDATE chats
                    SET updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (chat_id,)
                )

            connection.commit()

        return {
            "id": str(message[0]),
            "chat_id": str(message[1]),
            "role": message[2],
            "content": message[3],
            "created_at": message[4]
        }

    # =========================================================
    # GET CHAT MESSAGES
    # =========================================================

    def get_messages(self, chat_id):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        chat_id,
                        role,
                        content,
                        created_at
                    FROM messages
                    WHERE chat_id = %s
                    ORDER BY created_at ASC;
                    """,
                    (chat_id,)
                )

                rows = cursor.fetchall()

        messages = []

        for row in rows:

            messages.append(
                {
                    "id": str(row[0]),
                    "chat_id": str(row[1]),
                    "role": row[2],
                    "content": row[3],
                    "created_at": row[4]
                }
            )

        return messages

    # =========================================================
    # GET USER CHATS
    # =========================================================

    def get_chats(self, user_id=None):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                if user_id is None:

                    cursor.execute(
                        """
                        SELECT
                            id,
                            user_id,
                            title,
                            created_at,
                            updated_at
                        FROM chats
                        ORDER BY updated_at DESC;
                        """
                    )

                else:

                    cursor.execute(
                        """
                        SELECT
                            id,
                            user_id,
                            title,
                            created_at,
                            updated_at
                        FROM chats
                        WHERE user_id = %s
                        ORDER BY updated_at DESC;
                        """,
                        (user_id,)
                    )

                rows = cursor.fetchall()

        chats = []

        for row in rows:

            chats.append(
                {
                    "id": str(row[0]),
                    "user_id": (
                        str(row[1])
                        if row[1] is not None
                        else None
                    ),
                    "title": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                }
            )

        return chats

    # =========================================================
    # GET SINGLE CHAT
    # =========================================================

    def get_chat(self, chat_id):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        title,
                        created_at,
                        updated_at
                    FROM chats
                    WHERE id = %s;
                    """,
                    (chat_id,)
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": str(row[0]),
            "user_id": (
                str(row[1])
                if row[1] is not None
                else None
            ),
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4]
        }
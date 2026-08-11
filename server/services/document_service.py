import os
import psycopg

from server.config import DATABASE_URL


class DocumentService:
    """
    Handles document persistence and document management.
    Documents belong to individual users.
    """

    def __init__(self):
        self.database_url = DATABASE_URL

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _get_connection(self):
        return psycopg.connect(self.database_url)

    # =========================================================
    # GET USER DOCUMENTS
    # =========================================================

    def get_user_documents(self, user_id):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        d.id,
                        d.user_id,
                        d.filename,
                        d.file_path,
                        d.file_size,
                        d.mime_type,
                        d.created_at,
                        d.updated_at,
                        COUNT(dc.id) AS chunk_count
                    FROM documents d

                    LEFT JOIN document_chunks dc
                        ON dc.document_id = d.id

                    WHERE d.user_id = %s

                    GROUP BY
                        d.id,
                        d.user_id,
                        d.filename,
                        d.file_path,
                        d.file_size,
                        d.mime_type,
                        d.created_at,
                        d.updated_at

                    ORDER BY d.created_at DESC;
                    """,
                    (user_id,)
                )

                rows = cursor.fetchall()

        documents = []

        for row in rows:

            documents.append(
                {
                    "id": str(row[0]),
                    "user_id": str(row[1]),
                    "filename": row[2],
                    "file_path": row[3],
                    "file_size": row[4],
                    "mime_type": row[5],
                    "created_at": row[6],
                    "updated_at": row[7],
                    "chunk_count": row[8]
                }
            )

        return documents

    # =========================================================
    # GET SINGLE DOCUMENT
    # =========================================================

    def get_document(self, document_id, user_id):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        filename,
                        file_path,
                        file_size,
                        mime_type,
                        created_at,
                        updated_at
                    FROM documents
                    WHERE id = %s
                    AND user_id = %s;
                    """,
                    (
                        document_id,
                        user_id
                    )
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": str(row[0]),
            "user_id": str(row[1]),
            "filename": row[2],
            "file_path": row[3],
            "file_size": row[4],
            "mime_type": row[5],
            "created_at": row[6],
            "updated_at": row[7]
        }

    # =========================================================
    # DELETE DOCUMENT
    # =========================================================

    def delete_document(self, document_id, user_id):

        document = self.get_document(
            document_id=document_id,
            user_id=user_id
        )

        if document is None:
            return None

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM documents
                    WHERE id = %s
                    AND user_id = %s;
                    """,
                    (
                        document_id,
                        user_id
                    )
                )

            connection.commit()

        # -----------------------------------------------------
        # Delete physical PDF file
        # -----------------------------------------------------

        file_path = document["file_path"]

        if file_path and os.path.exists(file_path):

            try:
                os.remove(file_path)

            except OSError as error:

                print(
                    f"Warning: could not delete file "
                    f"{file_path}: {error}"
                )

        return document
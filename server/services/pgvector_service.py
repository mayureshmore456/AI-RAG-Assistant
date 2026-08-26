import os
import psycopg

from pgvector import Vector
from pgvector.psycopg import register_vector

from server.config import DATABASE_URL
from server.models.document import Document


class PGVectorService:
    """
    Handles document storage and vector similarity search
    using PostgreSQL + pgvector.
    """

    def __init__(self):
        self.database_url = DATABASE_URL

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _get_connection(self):
        connection = psycopg.connect(
            self.database_url
        )

        register_vector(connection)

        return connection

    # =========================================================
    # ADD DOCUMENTS
    # =========================================================

    def add_documents(self, documents, source, user_id):
        """
        Store a document and its chunks for a specific user.
        """

        if not documents:
            return None

        filename = os.path.basename(source)

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                # ---------------------------------------------
                # Create document record
                # ---------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO documents (
                        user_id,
                        filename,
                        file_path
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        user_id,
                        filename,
                        source
                    )
                )

                document_id = cursor.fetchone()[0]

                # ---------------------------------------------
                # Store document chunks + embeddings
                # ---------------------------------------------

                for index, document in enumerate(documents):

                    cursor.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id,
                            chunk_text,
                            chunk_index,
                            embedding
                        )
                        VALUES (%s, %s, %s, %s);
                        """,
                        (
                            document_id,
                            document.text,
                            index,
                            Vector(document.embedding)
                        )
                    )

            connection.commit()

        return str(document_id)

    # =========================================================
    # COUNT USER DOCUMENTS
    # =========================================================

    def count(self, user_id):
        """
        Count chunks belonging to documents owned by the user.
        """

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM document_chunks dc

                    JOIN documents d
                        ON dc.document_id = d.id

                    WHERE d.user_id = %s;
                    """,
                    (user_id,)
                )

                result = cursor.fetchone()

                return result[0]

    # =========================================================
    # VECTOR SIMILARITY SEARCH
    # =========================================================

    def search(self, query_embedding, top_k, user_id):
        """
        Search only documents belonging to the specified user.
        """

        query_vector = Vector(
            query_embedding
        )

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        dc.id,
                        dc.document_id,
                        dc.chunk_text,
                        dc.chunk_index,
                        dc.embedding <=> %s AS distance,
                        d.filename,
                        d.file_path

                    FROM document_chunks dc

                    JOIN documents d
                        ON dc.document_id = d.id

                    WHERE d.user_id = %s

                    ORDER BY dc.embedding <=> %s

                    LIMIT %s;
                    """,
                    (
                        query_vector,
                        user_id,
                        query_vector,
                        top_k
                    )
                )

                rows = cursor.fetchall()

        results = []

        for row in rows:

            document = Document(
                text=row[2],
                metadata={
                    "document_id": str(row[1]),
                    "source": row[6],
                    "filename": row[5],
                    "chunk_id": row[0],
                    "chunk_index": row[3]
                }
            )

            results.append(
                {
                    "document": document,
                    "score": 1 - row[4]
                }
            )

        return results
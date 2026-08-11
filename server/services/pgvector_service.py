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

    def add_documents(
        self,
        documents,
        source,
        user_id,
        filename=None,
        file_size=None,
        mime_type="application/pdf"
    ):

        if not documents:
            return None

        # -----------------------------------------------------
        # Use original filename if provided
        # -----------------------------------------------------

        if filename is None:

            filename = source.split("/")[-1]

        # -----------------------------------------------------
        # Connect to database
        # -----------------------------------------------------

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                # -------------------------------------------------
                # Create parent document
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO documents (
                        user_id,
                        filename,
                        file_path,
                        file_size,
                        mime_type
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        user_id,
                        filename,
                        source,
                        file_size,
                        mime_type
                    )
                )

                document_id = (
                    cursor.fetchone()[0]
                )

                # -------------------------------------------------
                # Store chunks and embeddings
                # -------------------------------------------------

                for index, document in enumerate(
                    documents
                ):

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
                            Vector(
                                document.embedding
                            )
                        )
                    )

            connection.commit()

        return str(document_id)

    # =========================================================
    # COUNT USER CHUNKS
    # =========================================================

    def count(
        self,
        user_id
    ):

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
                    (
                        user_id,
                    )
                )

                result = cursor.fetchone()

                return result[0]

    # =========================================================
    # VECTOR SIMILARITY SEARCH
    # =========================================================

    def search(
        self,
        query_embedding,
        top_k=3,
        user_id=None
    ):

        query_vector = Vector(
            query_embedding
        )

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                # -------------------------------------------------
                # Search ONLY current user's documents
                # -------------------------------------------------

                cursor.execute(
                    """
                    SELECT
                        dc.id,
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

        # -----------------------------------------------------
        # Convert database rows into Documents
        # -----------------------------------------------------

        results = []

        for row in rows:

            document = Document(
                text=row[1],
                metadata={
                    "source": row[5],
                    "filename": row[4],
                    "chunk_id": row[2]
                }
            )

            results.append(
                {
                    "document": document,
                    "score": 1 - row[3]
                }
            )

        return results
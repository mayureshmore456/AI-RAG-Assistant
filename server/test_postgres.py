from server.services.postgres_service import PostgresService


db = PostgresService()

print("✅ PostgreSQL connection successful!")

version = db.test_connection()

print("🐘 PostgreSQL version:")
print(version)

db.close()
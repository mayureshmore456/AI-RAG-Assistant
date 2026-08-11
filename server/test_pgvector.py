from server.services.pgvector_service import PGVectorService


db = PGVectorService()

print("✅ PGVectorService created successfully!")

print("📊 Current stored chunks:")
print(db.count())
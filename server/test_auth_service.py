from server.services.auth_service import AuthService


auth_service = AuthService()

print("🧪 Testing AuthService...")


# --------------------------------
# Create Token
# --------------------------------

user_id = "6d457d12-e5fb-4fa2-90ee-daf4c7e6ce1b"

token = auth_service.create_access_token(
    user_id
)

print("\n✅ JWT created:")
print(token)


# --------------------------------
# Verify Token
# --------------------------------

payload = auth_service.verify_token(
    token
)

print("\n✅ JWT verified:")
print(payload)


# --------------------------------
# Invalid Token Test
# --------------------------------

invalid_payload = auth_service.verify_token(
    "this-is-not-a-valid-token"
)

print("\n❌ Invalid token result:")
print(invalid_payload)


print("\n🎉 AuthService test complete!")
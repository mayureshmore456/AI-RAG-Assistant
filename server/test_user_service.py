from server.services.user_service import UserService


user_service = UserService()

print("🧪 Testing UserService...")


# --------------------------------
# Create User
# --------------------------------

user = user_service.create_user(
    name="Mayuresh",
    email="mayuresh@test.com",
    password="test123"
)

print("\n✅ User created:")
print(user)


# --------------------------------
# Find User
# --------------------------------

found_user = user_service.get_user_by_email(
    "mayuresh@test.com"
)

print("\n✅ User found:")
print(found_user)


# --------------------------------
# Authenticate
# --------------------------------

authenticated_user = user_service.authenticate_user(
    email="mayuresh@test.com",
    password="test123"
)

print("\n✅ Authentication result:")
print(authenticated_user)


# --------------------------------
# Wrong Password Test
# --------------------------------

wrong_password = user_service.authenticate_user(
    email="mayuresh@test.com",
    password="wrongpassword"
)

print("\n❌ Wrong password result:")
print(wrong_password)


print("\n🎉 UserService test complete!")
from server.services.chat_service import ChatService


chat_service = ChatService()

print("🧪 Testing ChatService...")

# Create a chat
chat = chat_service.create_chat(
    title="Test Chat"
)

print("✅ Chat created:")
print(chat)

chat_id = chat["id"]

# Save user message
user_message = chat_service.save_message(
    chat_id=chat_id,
    role="user",
    content="What is TCP?"
)

print("\n✅ User message saved:")
print(user_message)

# Save assistant message
assistant_message = chat_service.save_message(
    chat_id=chat_id,
    role="assistant",
    content="TCP is a connection-oriented transport layer protocol."
)

print("\n✅ Assistant message saved:")
print(assistant_message)

# Get messages
messages = chat_service.get_messages(
    chat_id=chat_id
)

print("\n📨 Chat history:")

for message in messages:
    print(
        f"{message['role']}: "
        f"{message['content']}"
    )

# Get chats
chats = chat_service.get_chats()

print("\n💬 All chats:")

for item in chats:
    print(
        f"{item['id']} → "
        f"{item['title']}"
    )

print("\n🎉 ChatService test complete!")
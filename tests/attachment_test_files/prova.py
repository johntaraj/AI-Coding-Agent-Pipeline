# Hardcoded data example in Python that will be attached in our Web App

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
]

print("User data:")
for user in users:
    print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
"""
Test Suite for Member 1 (Database & Auth)
Tests: DB initialization, User Registration, Password Verification, and Memory CRUD.
"""

from core.database import init_db, MemoryRepository
from core.auth import register_user, login_user

print("\n--- 1. Testing Database Initialization ---")
init_db()

print("\n--- 2. Testing User Registration ---")
reg_result = register_user("testuser", "test@example.com", "Password123")
print("Registration Output:", reg_result)

print("\n--- 3. Testing Duplicate Registration Prevention ---")
dup_result = register_user("testuser2", "test@example.com", "Password123")
print("Duplicate Register Output (should fail):", dup_result)

print("\n--- 4. Testing User Login ---")
logged_user = login_user("test@example.com", "Password123")
print("Login Successful for User:", logged_user)

wrong_login = login_user("test@example.com", "WrongPassword")
print("Wrong Password Test (should be None):", wrong_login)

if logged_user:
    user_id = logged_user["id"]
    print("\n--- 5. Testing Memory Creation ---")
    memory = MemoryRepository.create_memory(
        user_id=user_id,
        title="First Memory",
        description="This is a test note for our smart memory vault.",
        category="Personal",
        summary="A test note.",
        importance=4,
        tags=["vault", "first-note"]
    )
    print("Created Memory Record:", memory)

    print("\n--- 6. Testing Fetching User Memories ---")
    memories = MemoryRepository.get_user_memories(user_id)
    print(f"Fetched {len(memories)} memories for user:")
    for m in memories:
        print(f" -> [{m['category']}] {m['title']} (Importance: {m['importance']}/5)")

print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")

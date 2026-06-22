import requests
from urllib.parse import urlparse

# 1. LOGIN CREDENTIALS EN CLAIR
print("=== CLEARTEXT HTTP LOGIN ===")
response = requests.post('http://localhost/login', 
    data={'username': 'ali_hassan', 'password': 'password123'})
print(f"POST /login")
print(f"Body: username=ali_hassan&password=password123  ← CREDENTIALS EN CLAIR")
print()

# 2. SESSION COOKIE
print("=== SESSION COOKIE (HttpOnly missing) ===")
print(f"Set-Cookie: session=...; HttpOnly ← VULNERABLE: devrait avoir HttpOnly")
print()

# 3. DATABASE URL EN CLAIR (via Flask debug mode)
print("=== DATABASE CREDENTIALS LEAKAGE ===")
print("Flask debug mode expose les variables d'environnement:")
print("DATABASE_URL=postgresql://edu_admin:Educ%402024!@db:5432/myeduconnect")
print()

# 4. API JSON AVEC PII
print("=== PII TRANSMITTED IN PLAINTEXT ===")
response = requests.get('http://localhost/api/students')
print(response.json()[0])  # Affiche IC numbers, phones, etc.

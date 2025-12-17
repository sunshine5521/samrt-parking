import hashlib
password = 'password'
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f'Password: {password}')
print(f'SHA256 Hash: {hashed}')
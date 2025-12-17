import hashlib
password = 'password'
hashed = hashlib.md5(password.encode()).hexdigest()
print(f'Password: {password}')
print(f'MD5 Hash: {hashed}')
import hashlib

# 已知的admin密码哈希
hashed_password = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'

# 测试可能的密码
possible_passwords = ['admin', 'admin123', 'password', '123456', 'password123']

print('测试admin用户的密码：')
print('-' * 40)

for password in possible_passwords:
    # 计算SHA256哈希
    test_hash = hashlib.sha256(password.encode()).hexdigest()
    # 比较哈希值
    if test_hash == hashed_password:
        print(f'✓ 密码正确：{password}')
        break
    else:
        print(f'✗ 密码错误：{password}')
        print(f'   计算的哈希：{test_hash}')
        print(f'   正确的哈希：{hashed_password}')
        print()

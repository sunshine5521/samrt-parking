import sqlite3
import hashlib

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 新密码
new_password = 'admin123'
# 计算SHA256哈希
hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

# 更新admin用户的密码
cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, 'admin'))
conn.commit()

print('admin用户密码已重置：')
print(f'新密码：{new_password}')
print(f'哈希值：{hashed_password}')

# 验证更新结果
cursor.execute('SELECT username, password FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()
print(f'\n数据库中的admin用户信息：')
print(f'用户名：{user[0]}')
print(f'密码哈希：{user[1]}')

# 关闭连接
conn.close()
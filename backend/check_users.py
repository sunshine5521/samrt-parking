import sqlite3

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 执行查询
cursor.execute('SELECT username, password FROM users')

# 打印结果
print('用户名\t密码哈希')
print('-' * 20)
for row in cursor.fetchall():
    print(f'{row[0]}\t{row[1]}')

# 关闭连接
conn.close()
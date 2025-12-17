import sqlite3

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取完整的表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reservations';")
schema = cursor.fetchone()

print("Reservations table schema:")
print(schema[0] if schema else "Table not found")

# 关闭连接
conn.close()

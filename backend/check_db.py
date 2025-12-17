import sqlite3

# 检查数据库表结构的脚本
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取parking_records表的结构
cursor.execute("PRAGMA table_info(parking_records)")
columns = cursor.fetchall()

print("=== parking_records表结构 ===")
for column in columns:
    print(f"字段名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5] == 1}")

# 获取vehicles表的结构
cursor.execute("PRAGMA table_info(vehicles)")
columns = cursor.fetchall()

print("\n=== vehicles表结构 ===")
for column in columns:
    print(f"字段名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5] == 1}")

# 获取一些示例数据
print("\n=== parking_records表示例数据 ===")
cursor.execute("SELECT * FROM parking_records LIMIT 5")
records = cursor.fetchall()
for record in records:
    print(record)

# 关闭连接
conn.close()

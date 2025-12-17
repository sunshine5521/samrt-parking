import sqlite3

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取表结构
cursor.execute("PRAGMA table_info(reservations)")
columns = cursor.fetchall()

print("Reservations table columns:")
for column in columns:
    print(f"  {column[0]}: {column[1]} ({column[2]})")

# 关闭连接
conn.close()

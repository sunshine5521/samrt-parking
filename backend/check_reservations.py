import sqlite3

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取reservations表的结构
cursor.execute('PRAGMA table_info(reservations);')
columns = cursor.fetchall()

print('=== Table: reservations ===')
print('Structure:')
for column in columns:
    print(f'  {column[1]} ({column[2]})')

# 获取reservations表的行数
cursor.execute('SELECT COUNT(*) FROM reservations;')
row_count = cursor.fetchone()[0]
print(f'Rows: {row_count}')

# 如果有数据，显示前几行
if row_count > 0:
    cursor.execute('SELECT * FROM reservations;')
    rows = cursor.fetchall()
    print('First few rows:')
    for row in rows[:3]:
        print(f'  {row}')

# 关闭连接
conn.close()

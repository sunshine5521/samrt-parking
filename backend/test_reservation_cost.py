import sqlite3
import datetime

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 准备测试数据
user_id = 1
parking_lot_id = 1
parking_space_id = 1
vehicle_id = 1
start_time = '2023-10-01T10:00:00'
end_time = '2023-10-01T12:00:00'

# 从停车场获取时薪
cursor.execute('SELECT hourly_rate FROM parking_lots WHERE id = ?', (parking_lot_id,))
hourly_rate = cursor.fetchone()[0]

# 计算停车时长和总费用
start_datetime = datetime.fromisoformat(start_time)
end_datetime = datetime.fromisoformat(end_time)
duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
total_cost = duration_hours * hourly_rate

# 插入测试预订记录
cursor.execute('''INSERT INTO reservations (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, status, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, 'booked', total_cost))

# 提交事务
conn.commit()

# 查询插入的记录
cursor.execute('SELECT * FROM reservations WHERE id = ?', (cursor.lastrowid,))
reservation = cursor.fetchone()

# 打印结果
print(f'插入的预订记录：{reservation}')
print(f'计算的总费用：{total_cost}')
print(f'数据库中存储的总费用：{reservation[8]}')
print(f'总费用是否正确存储：{abs(reservation[8] - total_cost) < 0.001}')

# 清理测试数据
cursor.execute('DELETE FROM reservations WHERE id = ?', (reservation[0],))
conn.commit()

# 关闭连接
conn.close()
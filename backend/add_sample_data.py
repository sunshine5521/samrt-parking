import sqlite3

# 连接数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 为user1 (id=2) 添加更多车辆
cursor.execute('''
INSERT INTO vehicles (user_id, license_plate, brand, color)
VALUES (2, '京C24680', 'Ford', 'Red'),
       (2, '京D13579', 'Chevrolet', 'Blue')
''')

# 为user2 (id=3) 添加更多车辆
cursor.execute('''
INSERT INTO vehicles (user_id, license_plate, brand, color)
VALUES (3, '沪B45678', 'BMW', 'Black'),
       (3, '沪C98765', 'Audi', 'White')
''')

# 添加车位预约记录
cursor.execute('''
INSERT INTO reservations (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, status, total_cost)
VALUES (2, 1, 1, 1, '2023-10-10 09:00:00', '2023-10-10 17:00:00', 'completed', 40.0),
       (2, 2, 3, 2, '2023-10-11 10:00:00', '2023-10-11 15:00:00', 'pending', 40.0),
       (3, 3, 5, 3, '2023-10-12 08:00:00', '2023-10-12 20:00:00', 'confirmed', 120.0),
       (2, 1, 2, 4, '2023-10-13 14:00:00', '2023-10-13 18:00:00', 'completed', 20.0),
       (3, 2, 4, 5, '2023-10-14 09:00:00', '2023-10-14 13:00:00', 'pending', 32.0)
''')

# 添加停车记录
cursor.execute('''
INSERT INTO parking_records (user_id, vehicle_id, parking_lot_id, entry_time, exit_time, cost)
VALUES (2, 1, 1, '2023-10-07 08:30:00', '2023-10-07 12:30:00', 20.0),
       (2, 2, 2, '2023-10-08 10:00:00', '2023-10-08 16:00:00', 48.0),
       (3, 3, 3, '2023-10-09 07:30:00', '2023-10-09 19:30:00', 120.0),
       (2, 4, 1, '2023-10-10 09:15:00', '2023-10-10 17:00:00', 39.5),
       (3, 5, 2, '2023-10-11 08:45:00', '2023-10-11 12:00:00', 28.0)
''')

# 添加违规记录
cursor.execute('''
INSERT INTO violations (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount)
VALUES (2, 1, 1, '未按规定缴费', '2023-10-07 12:35:00', 'paid', 50.0),
       (2, 2, 2, '违规停车', '2023-10-08 16:05:00', 'unpaid', 200.0),
       (3, 3, 3, '超时停车', '2023-10-09 19:35:00', 'paid', 80.0),
       (2, 4, 1, '占用消防通道', '2023-10-10 17:05:00', 'unpaid', 500.0),
       (3, 5, 2, '未登记车辆进入', '2023-10-11 12:05:00', 'unpaid', 150.0)
''')

# 提交事务
conn.commit()

print('示例数据添加成功！')

# 验证添加的数据
print('\n=== 更新后的车辆表数据 ===')
cursor.execute('SELECT * FROM vehicles')
vehicles = cursor.fetchall()
for vehicle in vehicles:
    print(vehicle)

print('\n=== 更新后的预约表数据 ===')
cursor.execute('SELECT * FROM reservations')
reservations = cursor.fetchall()
for reservation in reservations:
    print(reservation)

print('\n=== 更新后的停车记录数据 ===')
cursor.execute('SELECT * FROM parking_records')
records = cursor.fetchall()
for record in records:
    print(record)

print('\n=== 更新后的违规记录数据 ===')
cursor.execute('SELECT * FROM violations')
violations = cursor.fetchall()
for violation in violations:
    print(violation)

# 关闭连接
conn.close()
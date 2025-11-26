import sqlite3

# 连接到数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 检查停车场数据
print('=== 停车场数据 ===')
cursor.execute('SELECT id, name, location, total_spaces, available_spaces FROM parking_lots')
parking_lots = cursor.fetchall()
print(f'共有 {len(parking_lots)} 个停车场')
for lot in parking_lots:
    print(f'ID: {lot[0]}, 名称: {lot[1]}, 位置: {lot[2]}, 总车位: {lot[3]}, 可用车位: {lot[4]}')

# 检查车位数据
print('\n=== 车位数据 ===')
cursor.execute('SELECT id, parking_lot_id, space_number, status FROM parking_spaces')
parking_spaces = cursor.fetchall()
print(f'共有 {len(parking_spaces)} 个车位')
for space in parking_spaces[:10]:  # 只显示前10个
    print(f'ID: {space[0]}, 停车场ID: {space[1]}, 车位号: {space[2]}, 状态: {space[3]}')
if len(parking_spaces) > 10:
    print(f'... 还有 {len(parking_spaces) - 10} 个车位未显示')

# 检查预订数据
print('\n=== 预订数据 ===')
cursor.execute('SELECT id, user_id, parking_lot_id, parking_space_id, status FROM reservations')
reservations = cursor.fetchall()
print(f'共有 {len(reservations)} 个预订')
for reservation in reservations:
    print(f'ID: {reservation[0]}, 用户ID: {reservation[1]}, 停车场ID: {reservation[2]}, 车位ID: {reservation[3]}, 状态: {reservation[4]}')

# 关闭连接
conn.close()
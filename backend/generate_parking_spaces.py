import sqlite3

# 连接数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取所有停车场
cursor.execute('SELECT id, total_spaces FROM parking_lots')
parking_lots = cursor.fetchall()

for lot_id, total_spaces in parking_lots:
    # 检查当前停车场已有多少车位
    cursor.execute('SELECT COUNT(*) FROM parking_spaces WHERE parking_lot_id = ?', (lot_id,))
    current_count = cursor.fetchone()[0]
    
    # 计算需要添加的车位数
    need_to_add = total_spaces - current_count
    
    if need_to_add > 0:
        print(f'为停车场 {lot_id} 添加 {need_to_add} 个车位...')
        
        # 批量添加车位
        spaces_to_add = []
        for i in range(current_count + 1, total_spaces + 1):
            space_number = f'A{i:03d}'  # 生成车位编号，如 A001, A002
            spaces_to_add.append((lot_id, space_number, 'free'))
        
        # 执行批量插入
        cursor.executemany('''
            INSERT INTO parking_spaces (parking_lot_id, space_number, status)
            VALUES (?, ?, ?)
        ''', spaces_to_add)
        
        print(f'停车场 {lot_id} 已添加 {need_to_add} 个车位')
    else:
        print(f'停车场 {lot_id} 已有 {current_count} 个车位，不需要添加')

# 提交事务
conn.commit()

# 验证结果
print('\n=== 各停车场车位统计 ===')
cursor.execute('SELECT parking_lot_id, COUNT(*) FROM parking_spaces GROUP BY parking_lot_id')
for lot_id, count in cursor.fetchall():
    cursor.execute('SELECT name FROM parking_lots WHERE id = ?', (lot_id,))
    lot_name = cursor.fetchone()[0]
    print(f'{lot_name} (ID: {lot_id}): {count} 个车位')

# 关闭连接
conn.close()
print('\n车位生成完成！')
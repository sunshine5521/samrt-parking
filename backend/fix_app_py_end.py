# 修复app.py文件末尾的问题

# 完整的缺失函数
missing_functions = '''

# 管理员删除停车场
@app.route('/api/admin/parking-lots/<int:lot_id>', methods=['DELETE'])
@require_auth(role='admin')
def delete_parking_lot(lot_id, **kwargs):
    conn = get_db_connection()
    # 删除停车场前，需要先删除相关的车位、预约、停车记录等
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 删除相关的违规记录
        conn.execute('DELETE FROM violations WHERE parking_lot_id = ?', (lot_id,))
        # 删除相关的停车记录
        conn.execute('DELETE FROM parking_records WHERE parking_lot_id = ?', (lot_id,))
        # 删除相关的预约
        conn.execute('DELETE FROM reservations WHERE parking_lot_id = ?', (lot_id,))
        # 删除相关的车位
        conn.execute('DELETE FROM parking_spaces WHERE parking_lot_id = ?', (lot_id,))
        # 删除停车场
        conn.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
        conn.commit()
        conn.close()
        return jsonify({'code': 200, 'message': '停车场删除成功'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 管理员添加车位
@app.route('/api/admin/parking-spaces', methods=['POST'])
@require_auth(role='admin')
def add_parking_space(**kwargs):
    data = request.get_json()
    parking_lot_id = data['parking_lot_id']
    space_number = data['space_number']
    space_type = data.get('type', 'normal')
    
    conn = get_db_connection()
    
    # 检查停车场是否存在
    parking_lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (parking_lot_id,)).fetchone()
    if not parking_lot:
        conn.close()
        return jsonify({'code': 404, 'message': '停车场不存在'}), 404
    
    # 检查该车位号是否已存在
    existing_space = conn.execute('SELECT * FROM parking_spaces WHERE parking_lot_id = ? AND space_number = ?', (parking_lot_id, space_number)).fetchone()
    if existing_space:
        conn.close()
        return jsonify({'code': 400, 'message': '该车位号已存在'}), 400
    
    # 创建车位
    conn.execute('INSERT INTO parking_spaces (parking_lot_id, space_number, type, status) VALUES (?, ?, ?, ?)', (parking_lot_id, space_number, space_type, 'free'))
    
    # 更新停车场的总车位数
    conn.execute('UPDATE parking_lots SET total_spaces = total_spaces + 1, available_spaces = available_spaces + 1 WHERE id = ?', (parking_lot_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'code': 200, 'message': '车位添加成功'})

# 管理员更新车位
@app.route('/api/admin/parking-spaces/<int:space_id>', methods=['PUT'])
@require_auth(role='admin')
def update_parking_space(space_id, **kwargs):
    data = request.get_json()
    space_number = data.get('space_number')
    space_type = data.get('type')
    status = data.get('status')
    
    conn = get_db_connection()
    
    # 构建更新字段
    update_fields = []
    params = []
    
    if space_number:
        update_fields.append('space_number = ?')
        params.append(space_number)
    if space_type:
        update_fields.append('type = ?')
        params.append(space_type)
    if status:
        update_fields.append('status = ?')
        params.append(status)
    
    params.append(space_id)
    
    if update_fields:
        query = f'UPDATE parking_spaces SET {", ".join(update_fields)} WHERE id = ?'
        conn.execute(query, params)
        conn.commit()
        conn.close()
        return jsonify({'code': 200, 'message': '车位更新成功'})
    else:
        conn.close()
        return jsonify({'code': 400, 'message': '没有需要更新的字段'})

# 管理员删除车位
@app.route('/api/admin/parking-spaces/<int:space_id>', methods=['DELETE'])
@require_auth(role='admin')
def delete_parking_space(space_id, **kwargs):
    conn = get_db_connection()
    
    # 获取车位所属的停车场
    space = conn.execute('SELECT parking_lot_id FROM parking_spaces WHERE id = ?', (space_id,)).fetchone()
    if not space:
        conn.close()
        return jsonify({'code': 404, 'message': '车位不存在'}), 404
    
    parking_lot_id = space['parking_lot_id']
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 删除相关的停车记录
        conn.execute('DELETE FROM parking_records WHERE parking_space_id = ?', (space_id,))
        # 删除相关的预约
        conn.execute('DELETE FROM reservations WHERE parking_space_id = ?', (space_id,))
        # 删除车位
        conn.execute('DELETE FROM parking_spaces WHERE id = ?', (space_id,))
        # 更新停车场的车位数
        conn.execute('UPDATE parking_lots SET total_spaces = total_spaces - 1, available_spaces = available_spaces - 1 WHERE id = ?', (parking_lot_id,))
        
        conn.commit()
        conn.close()
        return jsonify({'code': 200, 'message': '车位删除成功'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 预约超时释放任务
@app.route('/api/admin/tasks/release-expired-reservations', methods=['GET'])
@require_auth(role='admin')
def release_expired_reservations(**kwargs):
    conn = get_db_connection()
    
    # 获取当前时间
    now = datetime.datetime.now()
    grace_period = datetime.timedelta(minutes=15)  # 15分钟宽限期
    cutoff_time = now - grace_period
    cutoff_time_iso = cutoff_time.isoformat()
    
    try:
        # 查找超时未入场的预约
        expired_reservations = conn.execute('SELECT * FROM reservations WHERE status = ? AND start_time < ?', ('booked', cutoff_time_iso)).fetchall()
        
        if expired_reservations:
            conn.execute('BEGIN TRANSACTION')
            
            for res in expired_reservations:
                # 更新预约状态为已过期
                conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('expired', res['id']))
                
                # 创建通知
                conn.execute('INSERT INTO notifications (user_id, type, title, content, created_at) VALUES (?, ?, ?, ?, ?)', (res['user_id'], 'reservation', '预约已过期', f'您的预约（ID: {res["id"]}）已过期，车位已释放', datetime.datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return jsonify({'code': 200, 'message': f'成功释放 {len(expired_reservations)} 个过期预约'}), 200
        else:
            conn.close()
            return jsonify({'code': 200, 'message': '没有过期预约需要释放'}), 200
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
'''

# 读取原文件
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到需要替换的部分（从更新停车场函数的末尾开始，直到文件末尾）
start = content.find('    else:\n        conn.close()\n        return jsonify({\'code\': 400, \'message\': \'没有需要更新的字段\'})') + len('    else:\n        conn.close()\n        return jsonify({\'code\': 400, \'message\': \'没有需要更新的字段\'})')

# 构建新的内容
new_content = content[:start] + missing_functions

# 写入修复后的文件
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('app.py文件末尾已修复！')

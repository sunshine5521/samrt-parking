# 修复管理员更新停车场API函数
fixed_function = '''
# 管理员更新停车场
@app.route('/api/admin/parking-lots/<int:lot_id>', methods=['PUT'])
@require_auth(role='admin')
def update_parking_lot(lot_id, **kwargs):
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    gps_coordinates = data.get('gps_coordinates')
    hourly_rate = data.get('hourly_rate')
    status = data.get('status')

    conn = get_db_connection()

    # 构建更新字段
    update_fields = []
    params = []

    if name:
        update_fields.append('name = ?')
        params.append(name)
    if location:
        update_fields.append('location = ?')
        params.append(location)
    if gps_coordinates:
        update_fields.append('gps_coordinates = ?')
        params.append(gps_coordinates)
    if hourly_rate:
        update_fields.append('hourly_rate = ?')
        params.append(hourly_rate)
    if status:
        update_fields.append('status = ?')
        params.append(status)

    params.append(lot_id)

    if update_fields:
        query = f'UPDATE parking_lots SET {", ".join(update_fields)} WHERE id = ?'
        conn.execute(query, params)
        conn.commit()
        conn.close()
        return jsonify({'code': 200, 'message': '停车场更新成功'})
    else:
        conn.close()
        return jsonify({'code': 400, 'message': '没有需要更新的字段'})
'''

# 读取原文件
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到需要替换的部分
start = content.find('# 管理员更新停车场')
end = content.find('# 管理员删除停车场')

# 构建新的内容
new_content = content[:start] + fixed_function + content[end:]

# 写入修复后的文件
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('管理员更新停车场API函数已修复！')

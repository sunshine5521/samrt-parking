from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime
import os
import uuid

app = Flask(__name__)
CORS(app)

# 固定密钥，不再随机生成
app.config['SECRET_KEY'] = 'parking_system_secret_key_2023'

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('parking.db')
    conn.row_factory = sqlite3.Row
    return conn

# 统一鉴权装饰器
def require_auth(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'code': 401, 'message': '未提供token'}), 401
            
            try:
                # 移除Bearer前缀
                if token.startswith('Bearer '):
                    token = token.split(' ')[1]
                decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = decoded['user_id']
                user_role = decoded['role']
                
                # 检查角色权限
                if role and user_role != role:
                    return jsonify({'code': 403, 'message': '没有权限执行此操作'}), 403
                
                # 将用户信息传递给被装饰的函数
                kwargs['user_id'] = user_id
                kwargs['user_role'] = user_role
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({'code': 401, 'message': 'token已过期'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'code': 401, 'message': '无效的token'}), 401
            except Exception as e:
                return jsonify({'code': 500, 'message': str(e)}), 500
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# 停车费用计算函数
def calculate_parking_fee(entry_time_str, exit_time_str, hourly_rate):
    entry_time = datetime.datetime.fromisoformat(entry_time_str)
    exit_time = datetime.datetime.fromisoformat(exit_time_str)
    duration = (exit_time - entry_time).total_seconds() / 3600
    # 不足1小时按1小时计算
    duration = max(1.0, duration)
    return duration * hourly_rate


# 用户注册
@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data.get('email', '')

    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # 使用SHA256加密密码
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', 
                 (username, hashed_password, email, 'user'))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '注册成功'}), 200

# 用户登录
@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'code': 401, 'message': '用户名不存在'}), 401

    # 尝试SHA256验证
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password == user['password']:
        # SHA256验证成功
        pass
    else:
        # 尝试MD5验证
        hashed_password_md5 = hashlib.md5(password.encode()).hexdigest()
        if hashed_password_md5 != user['password']:
            return jsonify({'code': 401, 'message': '密码错误'}), 401

    token = jwt.encode({'user_id': user['id'], 'role': user['role'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'code': 200, 'data': {'token': f'Bearer {token}', 'user_id': user['id'], 'role': user['role']}})

# 获取用户个人信息
@app.route('/api/user/profile', methods=['GET'])
@require_auth()
def get_profile(user_id, **kwargs):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    return jsonify({'code': 200, 'data': dict(user)})

# 更新用户个人信息
@app.route('/api/user/profile', methods=['PUT'])
@require_auth()
def update_profile(user_id, **kwargs):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    conn = get_db_connection()
    
    # If password is provided, hash it and update
    if password:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn.execute('UPDATE users SET username = ?, password = ?, email = ? WHERE id = ?',
                   (username, hashed_password, email, user_id))
    else:
        conn.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                   (username, email, user_id))
    
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '个人信息更新成功'})

# 获取用户车辆列表
@app.route('/api/user/vehicles', methods=['GET'])
@require_auth()
def get_vehicles(user_id, **kwargs):
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return jsonify({'code': 200, 'data': [dict(vehicle) for vehicle in vehicles]})

# 添加车辆
@app.route('/api/user/vehicles', methods=['POST'])
@require_auth()
def add_vehicle(user_id, **kwargs):
    data = request.get_json()
    license_plate = data['license_plate']
    brand = data['brand']
    color = data['color']

    conn = get_db_connection()
    conn.execute('INSERT INTO vehicles (user_id, license_plate, brand, color) VALUES (?, ?, ?, ?)',
               (user_id, license_plate, brand, color))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '车辆添加成功'})

# 删除车辆
@app.route('/api/user/vehicles/<int:vehicle_id>', methods=['DELETE'])
@require_auth()
def delete_vehicle(vehicle_id, user_id, **kwargs):
    conn = get_db_connection()
    conn.execute('DELETE FROM vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '车辆删除成功'})

# 获取停车场列表
@app.route('/api/parking/lots', methods=['GET'])
@require_auth()
def get_parking_lots(**kwargs):
    conn = get_db_connection()
    parking_lots = conn.execute('SELECT * FROM parking_lots').fetchall()
    conn.close()

    return jsonify({'code': 200, 'data': [dict(lot) for lot in parking_lots]})

# 获取停车场车位列表
@app.route('/api/parking/spaces', methods=['GET'])
@require_auth()
def get_parking_spaces(**kwargs):
    lot_id = request.args.get('lot_id')
    if not lot_id:
        return jsonify({'code': 400, 'message': '缺少lot_id参数'}), 400
    
    conn = get_db_connection()
    parking_spaces = conn.execute('SELECT * FROM parking_spaces WHERE parking_lot_id = ?', (lot_id,)).fetchall()
    conn.close()

    return jsonify({'code': 200, 'data': [dict(space) for space in parking_spaces]})

# 获取可预约车位
@app.route('/api/parking/spaces/available', methods=['GET'])
@require_auth()
def get_available_spaces(**kwargs):
    lot_id = request.args.get('lot_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not lot_id or not start_time or not end_time:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    conn = get_db_connection()
    
    # 查询指定停车场内所有车位
    all_spaces = conn.execute('SELECT * FROM parking_spaces WHERE parking_lot_id = ?', (lot_id,)).fetchall()
    
    # 查询该时间段内已被预约或占用的车位
    conflicting_reservations = conn.execute('''
        SELECT parking_space_id FROM reservations 
        WHERE parking_lot_id = ? 
        AND status IN ('booked', 'checked_in') 
        AND (? < end_time AND ? > start_time)
    ''', (lot_id, start_time, end_time)).fetchall()
    
    # 查询该时间段内正在使用的车位（停车记录）
    conflicting_records = conn.execute('''
        SELECT parking_space_id FROM parking_records 
        WHERE parking_lot_id = ? 
        AND status = 'in_progress' 
        AND (? < exit_time OR exit_time IS NULL)
    ''', (lot_id, start_time)).fetchall()
    
    conn.close()
    
    # 提取冲突的车位ID
    conflicting_space_ids = set()
    for res in conflicting_reservations:
        conflicting_space_ids.add(res['parking_space_id'])
    for rec in conflicting_records:
        if rec['parking_space_id']:
            conflicting_space_ids.add(rec['parking_space_id'])
    
    # 筛选出可用车位
    available_spaces = [space for space in all_spaces if space['id'] not in conflicting_space_ids]
    
    return jsonify({'code': 200, 'data': [dict(space) for space in available_spaces]})

# 获取用户预约列表
@app.route('/api/user/reservations', methods=['GET'])
@require_auth()
def get_user_reservations(user_id, **kwargs):
    conn = get_db_connection()
    reservations = conn.execute('''
        SELECT r.*, v.license_plate, pl.name as parking_lot_name
        FROM reservations r
        JOIN vehicles v ON r.vehicle_id = v.id
        JOIN parking_lots pl ON r.parking_lot_id = pl.id
        WHERE r.user_id = ?
        ORDER BY r.start_time DESC
    ''', (user_id,)).fetchall()
    conn.close()

    return jsonify({'code': 200, 'data': [dict(res) for res in reservations]})

# 创建预约
@app.route('/api/reservations', methods=['POST'])
@require_auth()
def create_reservation(user_id, **kwargs):
    data = request.get_json()
    vehicle_id = data['vehicle_id']
    parking_lot_id = data['parking_lot_id']
    parking_space_id = data['parking_space_id']
    start_time = data['start_time']
    end_time = data['end_time']
    pay_now = data.get('pay_now', False)
    pay_method = data.get('pay_method', 'wallet')
    
    # 验证参数
    if start_time >= end_time:
        return jsonify({'code': 400, 'message': '开始时间必须早于结束时间'}), 400
    
    conn = get_db_connection()
    
    # 检查车辆是否属于用户
    vehicle = conn.execute('SELECT * FROM vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id)).fetchone()
    if not vehicle:
        conn.close()
        return jsonify({'code': 404, 'message': '车辆不存在或不属于该用户'}), 404
    
    # 检查停车场和车位是否存在
    parking_lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (parking_lot_id,)).fetchone()
    if not parking_lot:
        conn.close()
        return jsonify({'code': 404, 'message': '停车场不存在'}), 404
    
    parking_space = conn.execute('SELECT * FROM parking_spaces WHERE id = ? AND parking_lot_id = ?', (parking_space_id, parking_lot_id)).fetchone()
    if not parking_space:
        conn.close()
        return jsonify({'code': 404, 'message': '车位不存在或不属于该停车场'}), 404
    
    # 检查是否有重叠预约
    overlapping_reservation = conn.execute('''
        SELECT * FROM reservations 
        WHERE parking_space_id = ? 
        AND status IN ('booked', 'checked_in') 
        AND (? < end_time AND ? > start_time)
    ''', (parking_space_id, start_time, end_time)).fetchone()
    
    if overlapping_reservation:
        conn.close()
        return jsonify({'code': 400, 'message': '该车位在选定时间段已被预约'}), 400
    
    # 计算预约费用
    try:
        start_dt = datetime.datetime.fromisoformat(start_time)
        end_dt = datetime.datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds() / 3600
        duration = max(1.0, duration)  # 不足1小时按1小时计算
        total_cost = duration * parking_lot['hourly_rate']
    except Exception as e:
        conn.close()
        return jsonify({'code': 400, 'message': '时间格式错误'}), 400
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 创建预约
        conn.execute('''
            INSERT INTO reservations (user_id, vehicle_id, parking_lot_id, parking_space_id, start_time, end_time, status, total_cost, payment_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, vehicle_id, parking_lot_id, parking_space_id, start_time, end_time, 'booked', total_cost, 'unpaid', datetime.datetime.now().isoformat()))
        
        reservation_id = conn.lastrowid
        
        # 如果选择预约即付
        payment_info = None
        if pay_now:
            # 生成支付单
            trade_no = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO payments (user_id, reservation_id, amount, pay_method, status, trade_no, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, reservation_id, total_cost, pay_method, 'success', trade_no, datetime.datetime.now().isoformat()))
            
            # 更新预约支付状态
            conn.execute('UPDATE reservations SET payment_status = ? WHERE id = ?', ('paid', reservation_id))
            
            payment_info = {
                'payment_id': conn.lastrowid,
                'trade_no': trade_no,
                'amount': total_cost,
                'status': 'success'
            }
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '预约成功',
            'reservation_id': reservation_id,
            'payment': payment_info
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 取消预约
@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
@require_auth()
def cancel_reservation(reservation_id, user_id, **kwargs):
    conn = get_db_connection()
    
    # 获取预约信息
    reservation = conn.execute('SELECT * FROM reservations WHERE id = ? AND user_id = ?', (reservation_id, user_id)).fetchone()
    if not reservation:
        conn.close()
        return jsonify({'code': 404, 'message': '预约不存在'}), 404
    
    # 检查是否可以取消（只有booked状态可以取消）
    if reservation['status'] != 'booked':
        conn.close()
        return jsonify({'code': 400, 'message': '该预约已无法取消'}), 400
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 更新预约状态
        conn.execute('UPDATE reservations SET status = ?, canceled_at = ? WHERE id = ?', 
                   ('canceled', datetime.datetime.now().isoformat(), reservation_id))
        
        # 如果已支付，生成退款记录
        if reservation['payment_status'] == 'paid':
            trade_no = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO payments (user_id, reservation_id, amount, pay_method, status, trade_no, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, reservation_id, -reservation['total_cost'], 'refund', 'success', trade_no, datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'code': 200, 'message': '预约已取消'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 车辆入场
@app.route('/api/parking/entry', methods=['POST'])
@require_auth()
def vehicle_entry(user_id, **kwargs):
    data = request.get_json()
    vehicle_id = data['vehicle_id']
    lot_id = data['lot_id']
    space_id = data.get('space_id')
    reservation_id = data.get('reservation_id')
    
    conn = get_db_connection()
    
    # 检查车辆是否属于用户
    vehicle = conn.execute('SELECT * FROM vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id)).fetchone()
    if not vehicle:
        conn.close()
        return jsonify({'code': 404, 'message': '车辆不存在或不属于该用户'}), 404
    
    # 检查停车场是否存在
    parking_lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
    if not parking_lot:
        conn.close()
        return jsonify({'code': 404, 'message': '停车场不存在'}), 404
    
    # 如果提供了预约ID，检查预约是否有效
    if reservation_id:
        reservation = conn.execute('''
            SELECT * FROM reservations 
            WHERE id = ? AND user_id = ? AND vehicle_id = ? AND parking_lot_id = ? AND status = ?
        ''', (reservation_id, user_id, vehicle_id, lot_id, 'booked')).fetchone()
        
        if not reservation:
            conn.close()
            return jsonify({'code': 400, 'message': '无效的预约信息'}), 400
        
        # 使用预约的车位
        space_id = reservation['parking_space_id']
        
        # 更新预约状态为已入场
        conn.execute('UPDATE reservations SET status = ?, checkin_time = ? WHERE id = ?', 
                   ('checked_in', datetime.datetime.now().isoformat(), reservation_id))
    
    # 如果没有提供车位ID，自动分配一个空闲车位
    if not space_id:
        # 查询空闲车位
        available_space = conn.execute('''
            SELECT * FROM parking_spaces 
            WHERE parking_lot_id = ? AND status = ?
            ORDER BY id LIMIT 1
        ''', (lot_id, 'free')).fetchone()
        
        if not available_space:
            conn.close()
            return jsonify({'code': 400, 'message': '停车场已满'}), 400
        
        space_id = available_space['id']
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 创建停车记录
        conn.execute('''
            INSERT INTO parking_records (user_id, vehicle_id, parking_lot_id, parking_space_id, reservation_id, entry_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, vehicle_id, lot_id, space_id, reservation_id, datetime.datetime.now().isoformat(), 'in_progress'))
        
        record_id = conn.lastrowid
        
        # 更新车位状态为占用
        conn.execute('UPDATE parking_spaces SET status = ?, last_updated_at = ? WHERE id = ?', 
                   ('occupied', datetime.datetime.now().isoformat(), space_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '车辆入场成功',
            'record_id': record_id,
            'parking_space_id': space_id
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 车辆出场
@app.route('/api/parking/exit/<int:record_id>', methods=['PUT'])
@require_auth()
def vehicle_exit(record_id, user_id, **kwargs):
    conn = get_db_connection()
    
    # 获取停车记录
    record = conn.execute('SELECT * FROM parking_records WHERE id = ? AND user_id = ? AND status = ?', 
                         (record_id, user_id, 'in_progress')).fetchone()
    
    if not record:
        conn.close()
        return jsonify({'code': 404, 'message': '停车记录不存在或已结束'}), 404
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 获取停车场小时费率
        parking_lot = conn.execute('SELECT hourly_rate FROM parking_lots WHERE id = ?', (record['parking_lot_id'],)).fetchone()
        hourly_rate = parking_lot['hourly_rate'] if parking_lot else 10
        
        # 计算停车费用
        exit_time = datetime.datetime.now()
        entry_time = datetime.datetime.fromisoformat(record['entry_time'])
        duration = (exit_time - entry_time).total_seconds() / 3600
        duration = max(1.0, duration)  # 不足1小时按1小时计算
        cost = duration * hourly_rate
        
        # 更新停车记录
        conn.execute('''
            UPDATE parking_records
            SET exit_time = ?, duration = ?, cost = ?, status = ?
            WHERE id = ?
        ''', (exit_time.isoformat(), duration, cost, 'completed', record_id))
        
        # 更新车位状态为空闲
        conn.execute('UPDATE parking_spaces SET status = ?, last_updated_at = ? WHERE id = ?', 
                   ('free', datetime.datetime.now().isoformat(), record['parking_space_id']))
        
        # 如果有预约，更新预约状态为已完成
        if record['reservation_id']:
            conn.execute('UPDATE reservations SET status = ? WHERE id = ?', 
                       ('completed', record['reservation_id']))
        
        # 生成支付单
        trade_no = str(uuid.uuid4())
        conn.execute('''
            INSERT INTO payments (user_id, parking_record_id, amount, pay_method, status, trade_no, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, record_id, cost, 'wallet', 'success', trade_no, datetime.datetime.now().isoformat()))
        
        payment_id = conn.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '车辆出场成功',
            'data': {
                'exit_time': exit_time.isoformat(),
                'duration': duration,
                'cost': cost,
                'status': 'completed',
                'payment_id': payment_id
            }
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 处理支付
@app.route('/api/payments', methods=['POST'])
@require_auth()
def process_payment(user_id, **kwargs):
    data = request.get_json()
    
    # 支持多种支付场景：直接支付支付单ID，或通过关联ID支付
    payment_id = data.get('payment_id')
    record_id = data.get('record_id')
    violation_id = data.get('violation_id')
    reservation_id = data.get('reservation_id')
    pay_method = data.get('pay_method', 'wallet')
    
    conn = get_db_connection()
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        amount = 0
        payment_obj = None
        
        # 根据不同场景处理支付
        if payment_id:
            # 直接支付已有支付单
            payment_obj = conn.execute('SELECT * FROM payments WHERE id = ? AND user_id = ? AND status = ?', 
                                     (payment_id, user_id, 'pending')).fetchone()
            
            if not payment_obj:
                raise Exception('无效的支付单')
            
            amount = payment_obj['amount']
        elif record_id:
            # 支付停车记录费用
            record = conn.execute('SELECT * FROM parking_records WHERE id = ? AND user_id = ? AND status = ?', 
                                (record_id, user_id, 'completed')).fetchone()
            
            if not record:
                raise Exception('无效的停车记录')
            
            amount = record['cost']
        elif violation_id:
            # 支付违规罚款
            violation = conn.execute('SELECT * FROM violations WHERE id = ? AND user_id = ? AND status = ?', 
                                   (violation_id, user_id, 'unpaid')).fetchone()
            
            if not violation:
                raise Exception('无效的违规记录')
            
            amount = violation['fine_amount']
        elif reservation_id:
            # 支付预约费用
            reservation = conn.execute('SELECT * FROM reservations WHERE id = ? AND user_id = ? AND payment_status = ?', 
                                     (reservation_id, user_id, 'unpaid')).fetchone()
            
            if not reservation:
                raise Exception('无效的预约')
            
            amount = reservation['total_cost']
        else:
            raise Exception('缺少支付对象')
        
        # 生成支付单（如果没有）
        if not payment_obj:
            trade_no = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO payments (user_id, parking_record_id, reservation_id, violation_id, amount, pay_method, status, trade_no, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, record_id, reservation_id, violation_id, amount, pay_method, 'success', trade_no, datetime.datetime.now().isoformat()))
            
            payment_id = conn.lastrowid
        else:
            # 更新现有支付单状态
            payment_id = payment_obj['id']
            conn.execute('UPDATE payments SET status = ?, pay_method = ? WHERE id = ?', 
                       ('success', pay_method, payment_id))
        
        # 更新关联对象的支付状态
        if record_id:
            # 停车记录已在出场时处理
            pass
        elif violation_id:
            conn.execute('UPDATE violations SET status = ? WHERE id = ?', ('paid', violation_id))
        elif reservation_id:
            conn.execute('UPDATE reservations SET payment_status = ? WHERE id = ?', ('paid', reservation_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '支付成功',
            'data': {
                'payment_id': payment_id,
                'amount': amount,
                'status': 'success'
            }
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 400, 'message': str(e)}), 400

# 获取用户支付记录
@app.route('/api/payments', methods=['GET'])
@require_auth()
def get_payments(user_id, **kwargs):
    conn = get_db_connection()
    
    # 获取查询参数
    status = request.args.get('status')
    time_range = request.args.get('time_range')
    
    # 构建查询
    query = '''
        SELECT p.*, 
               CASE 
                   WHEN p.parking_record_id IS NOT NULL THEN 'parking' 
                   WHEN p.reservation_id IS NOT NULL THEN 'reservation' 
                   WHEN p.violation_id IS NOT NULL THEN 'violation' 
                   ELSE 'other' 
               END as payment_type
        FROM payments p
        WHERE p.user_id = ?
    '''
    
    params = [user_id]
    
    if status:
        query += ' AND p.status = ?'
        params.append(status)
    
    if time_range:
        # 简单处理时间范围，如：today, week, month
        now = datetime.datetime.now()
        if time_range == 'today':
            start_date = now.strftime('%Y-%m-%d')
            query += ' AND DATE(p.created_at) = ?'
            params.append(start_date)
        elif time_range == 'week':
            start_date = (now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            query += ' AND DATE(p.created_at) >= ?'
            params.append(start_date)
        elif time_range == 'month':
            start_date = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            query += ' AND DATE(p.created_at) >= ?'
            params.append(start_date)
    
    query += ' ORDER BY p.created_at DESC'
    
    payments = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify({'code': 200, 'data': [dict(pay) for pay in payments]})

# 生成违规记录
@app.route('/api/violations', methods=['POST'])
@require_auth(role='admin')
def create_violation(**kwargs):
    data = request.get_json()
    user_id = data['user_id']
    vehicle_id = data['vehicle_id']
    parking_lot_id = data['parking_lot_id']
    violation_type = data['violation_type']
    fine_amount = data['fine_amount']
    violation_time = data.get('violation_time', datetime.datetime.now().isoformat())
    
    conn = get_db_connection()
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 创建违规记录
        conn.execute('''
            INSERT INTO violations (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, 'unpaid', fine_amount))
        
        violation_id = conn.lastrowid
        
        # 创建通知
        conn.execute('''
            INSERT INTO notifications (user_id, type, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'violation', '违规通知', f'您的车辆违反了{violation_type}，罚款{fine_amount}元', datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '违规记录生成成功',
            'violation_id': violation_id
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 违规缴费
@app.route('/api/violations/<int:violation_id>/pay', methods=['POST'])
@require_auth()
def pay_violation(violation_id, user_id, **kwargs):
    data = request.get_json()
    pay_method = data.get('pay_method', 'wallet')
    
    conn = get_db_connection()
    
    # 获取违规记录
    violation = conn.execute('SELECT * FROM violations WHERE id = ? AND user_id = ? AND status = ?', 
                           (violation_id, user_id, 'unpaid')).fetchone()
    
    if not violation:
        conn.close()
        return jsonify({'code': 404, 'message': '无效的违规记录'}), 404
    
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 生成支付单
        trade_no = str(uuid.uuid4())
        conn.execute('''
            INSERT INTO payments (user_id, violation_id, amount, pay_method, status, trade_no, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, violation_id, violation['fine_amount'], pay_method, 'success', trade_no, datetime.datetime.now().isoformat()))
        
        # 更新违规状态
        conn.execute('UPDATE violations SET status = ? WHERE id = ?', ('paid', violation_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200, 
            'message': '违规缴费成功',
            'data': {
                'violation_id': violation_id,
                'amount': violation['fine_amount'],
                'status': 'paid'
            }
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 获取用户停车记录
@app.route('/api/parking/records', methods=['GET'])
@require_auth()
def get_parking_records(user_id, **kwargs):
    # 获取分页参数
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    conn = get_db_connection()
    
    # 获取总记录数
    total = conn.execute('''
        SELECT COUNT(*) FROM parking_records 
        WHERE user_id = ?
    ''', (user_id,)).fetchone()[0]
    
    # 获取分页数据
    records = conn.execute('''
        SELECT pr.*, v.license_plate, v.brand, v.color, pl.name as parking_lot_name
        FROM parking_records pr
        JOIN vehicles v ON pr.vehicle_id = v.id
        JOIN parking_lots pl ON pr.parking_lot_id = pl.id
        WHERE pr.user_id = ?
        ORDER BY pr.entry_time DESC
        LIMIT ? OFFSET ?
    ''', (user_id, page_size, offset)).fetchall()
    conn.close()

    return jsonify({
        'code': 200, 
        'data': [dict(record) for record in records],
        'total': total,
        'page': page,
        'page_size': page_size
    })

# 获取用户违规记录
@app.route('/api/violations', methods=['GET'])
@require_auth()
def get_violations(user_id, **kwargs):
    # 获取分页参数
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    conn = get_db_connection()
    
    # 获取总记录数
    total = conn.execute('''
        SELECT COUNT(*) FROM violations 
        WHERE user_id = ?
    ''', (user_id,)).fetchone()[0]
    
    # 获取分页数据
    violations = conn.execute('''
        SELECT v.*, vh.license_plate, pl.name as parking_lot_name
        FROM violations v
        JOIN vehicles vh ON v.vehicle_id = vh.id
        JOIN parking_lots pl ON v.parking_lot_id = pl.id
        WHERE v.user_id = ?
        ORDER BY v.violation_time DESC
        LIMIT ? OFFSET ?
    ''', (user_id, page_size, offset)).fetchall()
    conn.close()

    return jsonify({
        'code': 200, 
        'data': [dict(violation) for violation in violations],
        'total': total,
        'page': page,
        'page_size': page_size
    })

# 管理员获取所有车辆信息
@app.route('/api/admin/vehicles', methods=['GET'])
@require_auth(role='admin')
def get_all_vehicles(**kwargs):
    conn = get_db_connection()
    vehicles = conn.execute('''
        SELECT v.*, u.username 
        FROM vehicles v 
        JOIN users u ON v.user_id = u.id
    ''').fetchall()
    conn.close()

    return jsonify({'code': 200, 'data': [dict(vehicle) for vehicle in vehicles]})

# 管理员更新车辆信息
@app.route('/api/admin/vehicles/<int:vehicle_id>', methods=['PUT'])
@require_auth(role='admin')
def update_vehicle_admin(vehicle_id, **kwargs):
    data = request.get_json()
    license_plate = data['license_plate']
    brand = data['brand']
    color = data['color']

    conn = get_db_connection()
    conn.execute('''
        UPDATE vehicles
        SET license_plate = ?, brand = ?, color = ?
        WHERE id = ?
    ''', (license_plate, brand, color, vehicle_id))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '车辆信息已更新'})

# 管理员删除车辆
@app.route('/api/admin/vehicles/<int:vehicle_id>', methods=['DELETE'])
@require_auth(role='admin')
def delete_vehicle_admin(vehicle_id, **kwargs):
    conn = get_db_connection()
    conn.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '车辆已删除'})

# 管理员获取所有违规记录
@app.route('/api/admin/violations', methods=['GET'])
@require_auth(role='admin')
def get_all_violations(**kwargs):
    # Handle pagination
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size

    conn = get_db_connection()
    
    # Get total count
    total = conn.execute('SELECT COUNT(*) FROM violations').fetchone()[0]
    
    # Get violations with user and vehicle info
    violations = conn.execute('''
        SELECT v.*, u.username, ve.license_plate, ve.brand, ve.color, pl.name as parking_lot_name
        FROM violations v
        JOIN users u ON v.user_id = u.id
        JOIN vehicles ve ON v.vehicle_id = ve.id
        JOIN parking_lots pl ON v.parking_lot_id = pl.id
        ORDER BY v.violation_time DESC
        LIMIT ? OFFSET ?
    ''', (page_size, offset)).fetchall()
    conn.close()

    return jsonify({
        'code': 200,
        'data': [dict(violation) for violation in violations],
        'total': total,
        'page': page,
        'page_size': page_size
    })

# 管理员获取所有预约记录
@app.route('/api/admin/reservations', methods=['GET'])
@require_auth(role='admin')
def get_all_reservations(**kwargs):
    # Handle pagination
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size

    conn = get_db_connection()
    
    # Get total count
    total = conn.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]
    
    # Get reservations with user and vehicle info
    reservations = conn.execute('''
        SELECT r.*, u.username, v.license_plate, v.brand, v.color, pl.name as parking_lot_name
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN vehicles v ON r.vehicle_id = v.id
        JOIN parking_lots pl ON r.parking_lot_id = pl.id
        ORDER BY r.start_time DESC
        LIMIT ? OFFSET ?
    ''', (page_size, offset)).fetchall()
    conn.close()

    return jsonify({
        'code': 200,
        'data': [dict(reservation) for reservation in reservations],
        'total': total,
        'page': page,
        'page_size': page_size
    })

# 管理员获取统计数据
@app.route('/api/admin/statistics', methods=['GET'])
@require_auth(role='admin')
def get_admin_statistics(**kwargs):
    conn = get_db_connection()
    
    # Get total parking lots
    total_parking_lots = conn.execute('SELECT COUNT(*) FROM parking_lots').fetchone()[0]
    
    # Get total spaces
    total_spaces = conn.execute('SELECT COUNT(*) FROM parking_spaces').fetchone()[0]
    
    # Get occupied spaces
    occupied_spaces = conn.execute('SELECT COUNT(*) FROM parking_spaces WHERE status != ?', ('free',)).fetchone()[0]
    
    # Calculate occupancy rate
    occupancy_rate = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
    
    # Get today's revenue
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_revenue = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(created_at) = ? AND status = ?
    ''', (today, 'success')).fetchone()[0]
    
    # Get total users
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    # Get total vehicles
    total_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    
    # Get total violations
    total_violations = conn.execute('SELECT COUNT(*) FROM violations').fetchone()[0]
    
    conn.close()

    return jsonify({
        'code': 200,
        'statistics': {
            'total_parking_lots': total_parking_lots,
            'total_spaces': total_spaces,
            'occupied_spaces': occupied_spaces,
            'occupancy_rate': round(occupancy_rate, 2),
            'today_revenue': today_revenue,
            'total_users': total_users,
            'total_vehicles': total_vehicles,
            'total_violations': total_violations
        }
    })

# 管理员获取收入统计
@app.route('/api/admin/revenue-statistics', methods=['GET'])
@require_auth(role='admin')
def get_revenue_statistics(**kwargs):
    conn = get_db_connection()
    
    # Get today's revenue
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_revenue = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(created_at) = ? AND status = ?
    ''', (today, 'success')).fetchone()[0]
    
    # Get this month's revenue
    this_month = datetime.datetime.now().strftime('%Y-%m')
    month_revenue = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE STRFTIME('%Y-%m', created_at) = ? AND status = ?
    ''', (this_month, 'success')).fetchone()[0]
    
    # Get this year's revenue
    this_year = datetime.datetime.now().strftime('%Y')
    year_revenue = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE STRFTIME('%Y', created_at) = ? AND status = ?
    ''', (this_year, 'success')).fetchone()[0]
    
    # Get total revenue
    total_revenue = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE status = ?
    ''', ('success',)).fetchone()[0]
    
    # Get revenue details with pagination
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    # Get total records
    total = conn.execute('SELECT COUNT(*) FROM payments WHERE status = ?', ('success',)).fetchone()[0]
    
    # Get revenue details
    revenue_details = conn.execute('''
        SELECT p.*, 
               CASE 
                   WHEN p.parking_record_id IS NOT NULL THEN 'parking' 
                   WHEN p.reservation_id IS NOT NULL THEN 'reservation' 
                   WHEN p.violation_id IS NOT NULL THEN 'violation' 
                   ELSE 'other' 
               END as payment_type,
               u.username
        FROM payments p
        JOIN users u ON p.user_id = u.id
        WHERE p.status = ?
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
    ''', ('success', page_size, offset)).fetchall()
    
    # Get parking lot revenue ranking
    parking_lot_revenue = conn.execute('''
        SELECT pl.name as parking_lot_name, COALESCE(SUM(p.amount), 0) as revenue
        FROM parking_lots pl
        LEFT JOIN parking_records pr ON pl.id = pr.parking_lot_id
        LEFT JOIN payments p ON pr.id = p.parking_record_id
        WHERE p.status = ?
        GROUP BY pl.id
        ORDER BY revenue DESC
        LIMIT 5
    ''', ('success',)).fetchall()
    
    conn.close()

    # Prepare chart data
    chart_data = {
        'trend_dates': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        'trend_data': [800, 950, 1200, 1100, 1350, 1500, 1400],
        'parking_lot_names': [row['parking_lot_name'] for row in parking_lot_revenue],
        'parking_lot_revenues': [row['revenue'] for row in parking_lot_revenue]
    }

    return jsonify({
        'code': 200,
        'revenue_summary': {
            'todayRevenue': today_revenue,
            'monthRevenue': month_revenue,
            'yearRevenue': year_revenue,
            'totalRevenue': total_revenue,
            'todayChange': 12.5,  # Mock data for demonstration
            'monthChange': 8.2,   # Mock data for demonstration
            'yearChange': 15.8    # Mock data for demonstration
        },
        'revenue_details': [dict(record) for record in revenue_details],
        'total': total,
        'chart_data': chart_data
    })

# 管理员获取所有停车记录
@app.route('/api/admin/parking-records', methods=['GET'])
@require_auth(role='admin')
def get_all_parking_records(**kwargs):
    # Handle pagination parameters
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    # Handle filters
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    
    # Base query
    base_query = '''
        SELECT pr.*, v.license_plate, v.brand, v.color, pl.name as parking_lot_name, u.username
        FROM parking_records pr
        JOIN vehicles v ON pr.vehicle_id = v.id
        JOIN parking_lots pl ON pr.parking_lot_id = pl.id
        JOIN users u ON pr.user_id = u.id
        WHERE 1=1
    '''
    
    # Base count query
    count_query = '''
        SELECT COUNT(*)
        FROM parking_records pr
        JOIN vehicles v ON pr.vehicle_id = v.id
        JOIN parking_lots pl ON pr.parking_lot_id = pl.id
        JOIN users u ON pr.user_id = u.id
        WHERE 1=1
    '''
    
    # Parameters list
    params = []
    count_params = []
    
    # Add status filter if provided
    if status:
        base_query += ' AND pr.status = ?'
        count_query += ' AND pr.status = ?'
        params.append(status)
        count_params.append(status)
    
    # Add keyword filter if provided
    if keyword:
        base_query += ' AND (v.license_plate LIKE ? OR u.username LIKE ? OR pl.name LIKE ?)'
        count_query += ' AND (v.license_plate LIKE ? OR u.username LIKE ? OR pl.name LIKE ?)'
        keyword_param = f'%{keyword}%'
        params.extend([keyword_param, keyword_param, keyword_param])
        count_params.extend([keyword_param, keyword_param, keyword_param])
    
    # Add date range filter if provided
    if start_date:
        base_query += ' AND pr.entry_time >= ?'
        count_query += ' AND pr.entry_time >= ?'
        params.append(start_date)
        count_params.append(start_date)
    
    if end_date:
        base_query += ' AND pr.exit_time <= ?'
        count_query += ' AND pr.exit_time <= ?'
        params.append(end_date)
        count_params.append(end_date)
    
    # Add pagination
    base_query += ' LIMIT ? OFFSET ?'
    params.extend([page_size, offset])
    
    # Get paginated parking records with vehicle details
    parking_records = conn.execute(base_query, params).fetchall()
    # Get total number of records
    total = conn.execute(count_query, count_params).fetchone()[0]
    conn.close()
    
    # Convert records to list of dictionaries
    records_list = [dict(record) for record in parking_records]
    
    return jsonify({
        'code': 200,
        'data': records_list,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })

# 管理员结束停车记录
@app.route('/api/admin/parking-records/<int:record_id>/complete', methods=['PUT'])
@require_auth(role='admin')
def complete_parking_record(record_id, **kwargs):
    conn = get_db_connection()
    
    # Get the parking record
    record = conn.execute('SELECT * FROM parking_records WHERE id = ?', (record_id,)).fetchone()
    if not record:
        conn.close()
        return jsonify({'code': 404, 'message': '停车记录不存在'}), 404
    
    # Calculate duration and cost
    entry_time = datetime.datetime.fromisoformat(record['entry_time'])
    exit_time = datetime.datetime.now()
    duration = (exit_time - entry_time).total_seconds() / 3600
    
    # Get hourly rate from parking lot
    parking_lot = conn.execute('SELECT hourly_rate FROM parking_lots WHERE id = ?', (record['parking_lot_id'],)).fetchone()
    hourly_rate = parking_lot['hourly_rate'] if parking_lot else 10
    
    cost = duration * hourly_rate
    
    # Update the parking record
    conn.execute('''
        UPDATE parking_records
        SET exit_time = ?, duration = ?, cost = ?, status = 'completed'
        WHERE id = ?
    ''', (exit_time.isoformat(), duration, cost, record_id))
    conn.commit()
    conn.close()
    
    return jsonify({'code': 200, 'message': '停车记录已完成', 'data': {
        'end_time': exit_time.isoformat(),
        'duration': duration,
        'cost': cost,
        'status': 'completed'
    }})

# 管理员获取用户列表
@app.route('/api/admin/users', methods=['GET'])
@require_auth(role='admin')
def get_users(**kwargs):
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    return jsonify({'code': 200, 'data': [dict(user) for user in users]})

# 管理员添加停车场
@app.route('/api/admin/parking-lots', methods=['POST'])
@require_auth(role='admin')
def add_parking_lot(**kwargs):
    data = request.get_json()
    name = data['name']
    location = data['location']
    gps_coordinates = data['gps_coordinates']
    total_spaces = data['total_spaces']
    hourly_rate = data['hourly_rate']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO parking_lots (name, location, gps_coordinates, total_spaces, available_spaces, hourly_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, location, gps_coordinates, total_spaces, total_spaces, hourly_rate))
    
    parking_lot_id = conn.lastrowid
    
    # 创建初始车位
    for i in range(1, total_spaces + 1):
        conn.execute('''
            INSERT INTO parking_spaces (parking_lot_id, space_number, type, status)
            VALUES (?, ?, ?, ?)
        ''', (parking_lot_id, str(i), 'normal', 'free'))

    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '停车场添加成功', 'parking_lot_id': parking_lot_id})


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

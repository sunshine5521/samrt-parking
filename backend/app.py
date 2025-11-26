from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'supersecretkey'

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('parking.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    # Create users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                )''')
    # Create parking lots table
    conn.execute('''CREATE TABLE IF NOT EXISTS parking_lots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    gps_coordinates TEXT NOT NULL,
                    total_spaces INTEGER NOT NULL,
                    available_spaces INTEGER NOT NULL,
                    hourly_rate REAL NOT NULL
                )''')
    # Create vehicles table
    conn.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    license_plate TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    color TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    # Create parking spaces table
    conn.execute('''CREATE TABLE IF NOT EXISTS parking_spaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parking_lot_id INTEGER NOT NULL,
                    space_number TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'free',
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id)
                )''')
    # Create reservations table
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    parking_lot_id INTEGER NOT NULL,
                    parking_space_id INTEGER NOT NULL,
                    vehicle_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    total_cost REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id),
                    FOREIGN KEY (parking_space_id) REFERENCES parking_spaces (id),
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                )''')
    # Add total_cost column if not exists
    try:
        conn.execute('ALTER TABLE reservations ADD COLUMN total_cost REAL;')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Create parking records table
    conn.execute('''CREATE TABLE IF NOT EXISTS parking_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vehicle_id INTEGER NOT NULL,
                    parking_lot_id INTEGER NOT NULL,
                    entry_time TEXT NOT NULL,
                    exit_time TEXT,
                    cost REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id)
                )''')
    # Create violations table
    conn.execute('''CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vehicle_id INTEGER NOT NULL,
                    parking_lot_id INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    violation_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'unpaid',
                    fine_amount REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id)
                )''')
    # Insert sample parking lots only if table is empty
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM parking_lots')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO parking_lots (name, location, gps_coordinates, total_spaces, available_spaces, hourly_rate)
                        VALUES ('中央停车场', '市中心', '116.4074,39.9042', 100, 50, 5.0),
                               ('商业中心停车场', '商业区', '116.4074,39.9042', 200, 100, 8.0),
                               ('机场停车场', '机场', '116.4074,39.9042', 500, 200, 10.0)''')
    
    # Insert sample users only if table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO users (username, password, role)
                        VALUES ('admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin'),
                               ('user1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user'),
                               ('user2', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user')''')
    
    # Insert sample parking spaces only if table is empty
    cursor.execute('SELECT COUNT(*) FROM parking_spaces')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO parking_spaces (parking_lot_id, space_number, status)
                        VALUES (1, 'A001', 'free'),
                               (1, 'A002', 'reserved'),
                               (2, 'B001', 'free'),
                               (2, 'B002', 'occupied'),
                               (3, 'C001', 'free')''')
    
    # Insert sample vehicles only if table is empty
    cursor.execute('SELECT COUNT(*) FROM vehicles')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO vehicles (user_id, license_plate, brand, color)
                        VALUES (2, '京A12345', 'Toyota', 'White'),
                               (2, '京B67890', 'Honda', 'Black'),
                               (3, '沪A11223', 'Volkswagen', 'Silver')''')
    
    # Insert sample parking records only if table is empty
    cursor.execute('SELECT COUNT(*) FROM parking_records')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO parking_records (user_id, vehicle_id, parking_lot_id, entry_time, exit_time, cost)
                        VALUES (2, 1, 1, '2023-10-01 10:00:00', '2023-10-01 12:30:00', 15.0),
                               (2, 2, 2, '2023-10-02 08:00:00', '2023-10-02 17:30:00', 45.0),
                               (3, 3, 3, '2023-10-03 14:00:00', '2023-10-03 18:00:00', 20.0)''')
    
    # Insert sample violations only if table is empty
    cursor.execute('SELECT COUNT(*) FROM violations')
    if cursor.fetchone()[0] == 0:
        conn.execute('''INSERT INTO violations (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount)
                        VALUES (2, 1, 1, '乱停车', '2023-10-04 09:00:00', 'unpaid', 200.0),
                               (2, 2, 2, '超时停车', '2023-10-05 12:00:00', 'paid', 100.0),
                               (3, 3, 3, '违规占用残疾人车位', '2023-10-06 15:30:00', 'unpaid', 300.0)''')
    
    conn.commit()
    conn.close()

# User registration
@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username'].strip()
    password = data['password'].strip()
    confirm_password = data.get('confirmPassword', '')

    if not confirm_password:
        return jsonify({'code': 400, 'message': '请提供确认密码'}), 400

    confirm_password = confirm_password.strip()

    if password != confirm_password:
        return jsonify({'code': 400, 'message': '两次密码输入不一致'}), 400

    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, 'user'))
    conn.commit()
    conn.close()

    return jsonify({'code': 200, 'message': '注册成功'})

# User login
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

    return jsonify({'code': 200, 'data': {'token': token, 'user_id': user['id'], 'role': user['role']}})

# Get user profile
@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        return jsonify({'code': 200, 'data': dict(user)})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# Update user profile
@app.route('/api/user/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')

        conn = get_db_connection()
        if new_username:
            conn.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '个人信息更新成功'})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get user vehicles
@app.route('/api/user/vehicles', methods=['GET'])
def get_vehicles():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        vehicles = conn.execute('SELECT * FROM vehicles WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()

        return jsonify({'code': 200, 'data': [dict(vehicle) for vehicle in vehicles]})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Add user vehicle
@app.route('/api/user/vehicles', methods=['POST'])
def add_vehicle():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
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
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Delete user vehicle
@app.route('/api/user/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        conn.execute('DELETE FROM vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id))
        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '车辆删除成功'})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking lots
@app.route('/api/parking/lots', methods=['GET'])
def get_parking_lots():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])

        conn = get_db_connection()
        parking_lots = conn.execute('SELECT * FROM parking_lots').fetchall()
        conn.close()

        return jsonify({'code': 200, 'data': [dict(lot) for lot in parking_lots]})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking spaces
@app.route('/api/parking/spaces', methods=['GET'])
def get_parking_spaces():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])

        lot_id = request.args.get('lot_id')
        conn = get_db_connection()
        if lot_id:
            parking_spaces = conn.execute('SELECT * FROM parking_spaces WHERE parking_lot_id = ?', (lot_id,)).fetchall()
        else:
            parking_spaces = conn.execute('SELECT * FROM parking_spaces').fetchall()
        conn.close()

        return jsonify({'code': 200, 'data': [dict(space) for space in parking_spaces]})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking records
@app.route('/api/user/records', methods=['GET'])
def get_parking_records():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        parking_records = conn.execute('''
            SELECT pr.*, v.license_plate, v.brand, v.color, pl.name as parking_lot_name 
            FROM parking_records pr 
            JOIN vehicles v ON pr.vehicle_id = v.id 
            JOIN parking_lots pl ON pr.parking_lot_id = pl.id
            WHERE pr.user_id = ?
        ''', (user_id,)).fetchall()
        conn.close()

        return jsonify({'code': 200, 'records': [dict(record) for record in parking_records]})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking records with pagination
@app.route('/api/parking/records', methods=['GET'])
def get_parking_records_paginated():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        
        # Handle pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size
        # Handle search parameter
        license_plate = request.args.get('license_plate')

        conn = get_db_connection()
        
        # Base query
        base_query = '''
            SELECT pr.*, v.license_plate, v.brand, v.color, pl.name as parking_lot_name
            FROM parking_records pr
            JOIN vehicles v ON pr.vehicle_id = v.id
            JOIN parking_lots pl ON pr.parking_lot_id = pl.id
            WHERE pr.user_id = ?
        '''
        
        # Base count query
        count_query = 'SELECT COUNT(*) FROM parking_records pr JOIN vehicles v ON pr.vehicle_id = v.id WHERE pr.user_id = ?'
        
        # Parameters list
        params = [user_id]
        count_params = [user_id]
        
        # Add search condition if license_plate is provided
        if license_plate:
            base_query += ' AND v.license_plate LIKE ?'
            count_query += ' AND v.license_plate LIKE ?'
            params.append(f'%{license_plate}%')
            count_params.append(f'%{license_plate}%')
        
        # Add pagination
        base_query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        # Get paginated parking records with vehicle details
        parking_records = conn.execute(base_query, params).fetchall()
        # Get total number of records
        total = conn.execute(count_query, count_params).fetchone()[0]
        conn.close()

        return jsonify({'code': 200, 'records': [dict(record) for record in parking_records], 'total': total})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get user violations
@app.route('/api/user/violations', methods=['GET'])
def get_user_violations():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        violations = conn.execute('''
            SELECT v.*, veh.license_plate, veh.brand, veh.color, pl.name as parking_lot_name 
            FROM violations v 
            JOIN vehicles veh ON v.vehicle_id = veh.id 
            JOIN parking_lots pl ON v.parking_lot_id = pl.id
            WHERE v.user_id = ?
        ''', (user_id,)).fetchall()
        conn.close()

        return jsonify({'code': 200, 'violations': [dict(violation) for violation in violations]})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get violations with pagination
@app.route('/api/violations', methods=['GET'])
def get_violations_paginated():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        role = decoded['role']  # Get user role from token
        
        # Handle pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size

        conn = get_db_connection()
        
        if role == 'admin':
            # Admin sees all violations
            violations = conn.execute('''
                SELECT v.*, ve.license_plate, ve.brand, ve.color, pl.name as parking_lot_name
                FROM violations v
                JOIN vehicles ve ON v.vehicle_id = ve.id
                JOIN parking_lots pl ON v.parking_lot_id = pl.id
                LIMIT ? OFFSET ?
            ''', (page_size, offset)).fetchall()
            total = conn.execute('SELECT COUNT(*) FROM violations').fetchone()[0]
        else:
            # Regular user sees only their own violations
            violations = conn.execute('''
                SELECT v.*, ve.license_plate, ve.brand, ve.color, pl.name as parking_lot_name
                FROM violations v
                JOIN vehicles ve ON v.vehicle_id = ve.id
                JOIN parking_lots pl ON v.parking_lot_id = pl.id
                WHERE v.user_id = ?
                LIMIT ? OFFSET ?
            ''', (user_id, page_size, offset)).fetchall()
            total = conn.execute('SELECT COUNT(*) FROM violations WHERE user_id = ?', (user_id,)).fetchone()[0]
        
        conn.close()

        return jsonify({'code': 200, 'violations': [dict(violation) for violation in violations], 'total': total})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking spaces by lot ID


# Create parking reservation
@app.route('/api/reservation', methods=['POST'])
def create_reservation():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        data = request.get_json()
        vehicle_id = data['vehicle_id']
        parking_lot_id = data['parking_lot_id']
        parking_space_id = data['parking_space_id']
        start_time = data['start_time']
        end_time = data['end_time']

        conn = get_db_connection()
        try:
            # 获取停车场的时薪
            cursor = conn.execute('SELECT hourly_rate FROM parking_lots WHERE id = ?', (parking_lot_id,))
            hourly_rate = cursor.fetchone()[0]

            # 计算停车时长和总费用
            # 使用datetime.strptime解析ISO格式日期（兼容旧版Python）
            # 包含日期字符串末尾的'Z'字符在格式中
            start_datetime = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            end_datetime = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            total_cost = duration_hours * hourly_rate

            # 插入预订记录，状态为'booked'并包含总费用
            conn.execute('''INSERT INTO reservations (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, status, total_cost)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, 'booked', total_cost))
            
            # 减少停车场的可用车位数量
            conn.execute('UPDATE parking_lots SET available_spaces = available_spaces - 1 WHERE id = ?', (parking_lot_id,))
            
            conn.commit()
            conn.close()

            return jsonify({'code': 200, 'message': '预定成功'})
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'code': 500, 'message': str(e)}), 500
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# Add violation (admin only)
@app.route('/api/violations', methods=['POST'])
def add_violation():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        role = decoded['role']

        if role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限执行此操作'}), 403

        data = request.get_json()
        vehicle_license_plate = data.get('vehicle_license_plate')
        parking_lot_id = data.get('parking_lot_id')
        violation_type = data.get('violation_type')
        violation_time = data.get('violation_time')
        fine_amount = data.get('fine_amount')
        description = data.get('description', '')
        status = data.get('status', 'unpaid')

        if not vehicle_license_plate or not parking_lot_id or not violation_type or not violation_time or fine_amount is None:
            return jsonify({'code': 400, 'message': '缺少必要的参数'}), 400

        conn = get_db_connection()

        # Find vehicle by license plate
        vehicle = conn.execute('SELECT id, user_id FROM vehicles WHERE license_plate = ?', (vehicle_license_plate,)).fetchone()
        if not vehicle:
            conn.close()
            return jsonify({'code': 404, 'message': '车辆不存在'}), 404

        vehicle_id = vehicle['id']
        user_id = vehicle['user_id']

        # Insert new violation
        conn.execute('''INSERT INTO violations (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount))

        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '违规记录添加成功'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# Edit violation (admin only)
@app.route('/api/violations/<int:id>', methods=['PUT'])
def edit_violation(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        role = decoded['role']

        if role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限执行此操作'}), 403

        data = request.get_json()
        parking_lot_id = data.get('parking_lot_id')
        violation_type = data.get('violation_type')
        violation_time = data.get('violation_time')
        fine_amount = data.get('fine_amount')
        status = data.get('status')

        if not parking_lot_id or not violation_type or not violation_time or fine_amount is None or not status:
            return jsonify({'code': 400, 'message': '缺少必要的参数'}), 400

        conn = get_db_connection()

        # Update violation
        conn.execute('''UPDATE violations SET parking_lot_id = ?, violation_type = ?, violation_time = ?, fine_amount = ?, status = ?
                        WHERE id = ?''',
                    (parking_lot_id, violation_type, violation_time, fine_amount, status, id))

        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '违规记录更新成功'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# Delete violation (admin only)
@app.route('/api/violations/<int:id>', methods=['DELETE'])
def delete_violation(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        role = decoded['role']

        if role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限执行此操作'}), 403

        conn = get_db_connection()

        # Delete violation
        conn.execute('DELETE FROM violations WHERE id = ?', (id,))

        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '违规记录删除成功'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# Pay violation
@app.route('/api/violations/<int:id>/pay', methods=['POST'])
def pay_violation(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']

        conn = get_db_connection()
        # Check if the violation belongs to the user
        violation = conn.execute('SELECT * FROM violations WHERE id = ? AND user_id = ?', (id, user_id)).fetchone()
        if not violation:
            conn.close()
            return jsonify({'code': 404, 'message': '违规记录不存在'}), 404

        # Update the violation status to 'paid'
        conn.execute('UPDATE violations SET status = ? WHERE id = ? AND user_id = ?', ('paid', id, user_id))
        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'message': '支付成功'})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get admin statistics
@app.route('/api/admin/statistics', methods=['GET'])
def get_statistics():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        decoded = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        role = decoded['role']
        
        if role != 'admin':
            return jsonify({'code': 403, 'message': '无权限访问此资源'}), 403

        time_range = request.args.get('time_range', 'today')
        conn = get_db_connection()

        # Calculate total parking lots
        total_parking_lots = conn.execute('SELECT COUNT(*) FROM parking_lots').fetchone()[0]

        # Calculate total spaces
        total_spaces = conn.execute('SELECT SUM(total_spaces) FROM parking_lots').fetchone()[0] or 0

        # Calculate current occupancy rate
        current_occupancy = conn.execute('''
            SELECT SUM(total_spaces - available_spaces) * 100.0 / SUM(total_spaces) 
            FROM parking_lots 
            WHERE total_spaces > 0
        ''').fetchone()[0] or 0.0

        # Calculate revenue based on time range
        if time_range == 'today':
            revenue = conn.execute('''
                SELECT SUM(cost) 
                FROM parking_records 
                WHERE date(entry_time) = date('now')
            ''').fetchone()[0] or 0.0
        elif time_range == 'week':
            revenue = conn.execute('''
                SELECT SUM(cost) 
                FROM parking_records 
                WHERE entry_time BETWEEN datetime('now', '-7 days') AND datetime('now')
            ''').fetchone()[0] or 0.0
        elif time_range == 'month':
            revenue = conn.execute('''
                SELECT SUM(cost) 
                FROM parking_records 
                WHERE strftime('%Y-%m', entry_time) = strftime('%Y-%m', 'now')
            ''').fetchone()[0] or 0.0
        elif time_range == 'year':
            revenue = conn.execute('''
                SELECT SUM(cost) 
                FROM parking_records 
                WHERE strftime('%Y', entry_time) = strftime('%Y', 'now')
            ''').fetchone()[0] or 0.0
        else:
            revenue = 0.0

        # Get parking lot revenues
        parking_lot_revenues = conn.execute('''
            SELECT 
                pl.id, 
                pl.name, 
                SUM(pr.cost) as revenue,
                CASE 
                    WHEN pl.total_spaces > 0 THEN (pl.total_spaces - pl.available_spaces) * 100.0 / pl.total_spaces
                    ELSE 0
                END as occupancy_rate
            FROM parking_lots pl
            LEFT JOIN parking_records pr ON pl.id = pr.parking_lot_id
            GROUP BY pl.id
            ORDER BY revenue DESC
        ''').fetchall()
        
        parking_lot_revenues = [dict(item) for item in parking_lot_revenues]
        for item in parking_lot_revenues:
            item['revenue'] = round(item['revenue'] or 0.0, 2)
            item['occupancy_rate'] = round(item['occupancy_rate'] or 0.0, 2)

        # Get recent parking records
        parking_records = conn.execute('''
            SELECT 
                pr.id, 
                pl.name as parking_lot_name, 
                pr.entry_time as start_time, 
                pr.exit_time as end_time, 
                pr.cost
            FROM parking_records pr
            JOIN parking_lots pl ON pr.parking_lot_id = pl.id
            ORDER BY pr.entry_time DESC
            LIMIT 10
        ''').fetchall()
        
        parking_records = [dict(item) for item in parking_records]
        for item in parking_records:
            item['cost'] = round(item['cost'] or 0.0, 2)

        conn.close()

        return jsonify({
            'code': 200,
            'statistics': {
                'total_parking_lots': total_parking_lots,
                'total_spaces': total_spaces,
                'occupancy_rate': round(current_occupancy, 2),
                'today_revenue': round(revenue, 2)
            },
            'parking_lot_revenues': parking_lot_revenues,
            'parking_records': parking_records
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, use_reloader=False)
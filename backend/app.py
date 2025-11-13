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
                    available_spaces INTEGER NOT NULL
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
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots (id),
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                )''')
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
    # Insert sample parking lots
    conn.execute('''INSERT OR IGNORE INTO parking_lots (name, location, gps_coordinates, total_spaces, available_spaces)
                    VALUES ('中央停车场', '市中心', '116.4074,39.9042', 100, 50),
                           ('商业中心停车场', '商业区', '116.4074,39.9042', 200, 100),
                           ('机场停车场', '机场', '116.4074,39.9042', 500, 200)''')
    
    # Insert sample users with SHA256 hashes
    conn.execute('''INSERT OR IGNORE INTO users (username, password, role)
                    VALUES ('admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin'),
                           ('user1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user'),
                           ('user2', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user')''')
    
    # Insert sample vehicles
    conn.execute('''INSERT OR IGNORE INTO vehicles (user_id, license_plate, brand, color)
                    VALUES (2, '京A12345', 'Toyota', 'White'),
                           (2, '京B67890', 'Honda', 'Black'),
                           (3, '沪A11223', 'Volkswagen', 'Silver')''')
    
    # Insert sample parking records
    conn.execute('''INSERT OR IGNORE INTO parking_records (user_id, vehicle_id, parking_lot_id, entry_time, exit_time, cost)
                    VALUES (2, 1, 1, '2023-10-01 10:00:00', '2023-10-01 12:30:00', 15.0),
                           (2, 2, 2, '2023-10-02 08:00:00', '2023-10-02 17:30:00', 45.0),
                           (3, 3, 3, '2023-10-03 14:00:00', '2023-10-03 18:00:00', 20.0)''')
    
    # Insert sample violations
    conn.execute('''INSERT OR IGNORE INTO violations (user_id, vehicle_id, parking_lot_id, violation_type, violation_time, status, fine_amount)
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

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password != user['password']:
        return jsonify({'code': 401, 'message': '密码错误'}), 401

    token = jwt.encode({'user_id': user['id'], 'role': user['role'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                      app.config['SECRET_KEY'], algorithm='HS256')

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

        conn = get_db_connection()
        # Get paginated parking records with vehicle details
        parking_records = conn.execute('''
            SELECT pr.*, v.license_plate, v.brand, v.color, pl.name as parking_lot_name
            FROM parking_records pr
            JOIN vehicles v ON pr.vehicle_id = v.id
            JOIN parking_lots pl ON pr.parking_lot_id = pl.id
            WHERE pr.user_id = ?
            LIMIT ? OFFSET ?
        ''', (user_id, page_size, offset)).fetchall()
        # Get total number of records
        total = conn.execute('SELECT COUNT(*) FROM parking_records WHERE user_id = ?', (user_id,)).fetchone()[0]
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
        
        # Handle pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size

        conn = get_db_connection()
        # Get paginated violations with vehicle details
        violations = conn.execute('''
            SELECT v.*, ve.license_plate, ve.brand, ve.color
            FROM violations v
            JOIN vehicles ve ON v.vehicle_id = ve.id
            WHERE v.user_id = ?
            LIMIT ? OFFSET ?
        ''', (user_id, page_size, offset)).fetchall()
        # Get total number of records
        total = conn.execute('SELECT COUNT(*) FROM violations WHERE user_id = ?', (user_id,)).fetchone()[0]
        conn.close()

        return jsonify({'code': 200, 'violations': [dict(violation) for violation in violations], 'total': total})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

# Get parking spaces by lot ID
@app.route('/api/parking/space', methods=['GET'])
def get_parking_spaces():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 401, 'message': '未提供token'}), 401

    try:
        jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
        lot_id = request.args.get('lot_id')

        if not lot_id:
            return jsonify({'code': 400, 'message': '未提供停车场ID'}), 400

        # Generate mock parking spaces since there's no parking_spaces table in the database
        conn = get_db_connection()
        parking_lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        
        if not parking_lot:
            conn.close()
            return jsonify({'code': 404, 'message': '停车场不存在'}), 404

        parking_lot = dict(parking_lot)
        total_spaces = parking_lot['total_spaces']
        available_spaces = parking_lot['available_spaces']

        # Get all reservations for this parking lot
        reservations = conn.execute('''
            SELECT parking_space_id, status
            FROM reservations 
            WHERE parking_lot_id = ?
        ''', (lot_id,)).fetchall()
        conn.close()

        # Generate mock parking spaces
        parking_spaces = []
        for i in range(1, total_spaces + 1):
            # Check if this space is reserved
            reserved = any(reservation['parking_space_id'] == i and reservation['status'] == 'booked' for reservation in reservations)
            
            if reserved:
                status = 'booked'
            elif i <= available_spaces:
                status = 'free'
            else:
                status = 'occupied'
            
            parking_spaces.append({
                'id': i,
                'number': str(i).zfill(3),
                'status': status,
                'parking_lot_id': lot_id
            })

        return jsonify({'code': 200, 'data': parking_spaces})
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 401, 'message': 'token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'code': 401, 'message': '无效的token'}), 401

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
            # 插入预订记录，状态为'booked'
            conn.execute('''INSERT INTO reservations (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (user_id, parking_lot_id, parking_space_id, vehicle_id, start_time, end_time, 'booked'))
            
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
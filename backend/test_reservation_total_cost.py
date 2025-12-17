import requests
import sqlite3
import json

# 登录获取token
login_url = 'http://127.0.0.1:5000/api/user/login'
# 准备登录数据
login_data = {'username': 'user2', 'password': 'password'}
login_response = requests.post(login_url, json=login_data)

if login_response.status_code != 200:
    print('登录失败:', login_response.json())
    exit(1)

token = login_response.json()['data']['token']
print('登录成功, token:', token)

# 准备预约数据
reservation_url = 'http://127.0.0.1:5000/api/reservation'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 使用现有的停车场ID 1
reservation_data = {
    'vehicle_id': 1,
    'parking_lot_id': 1,
    'parking_space_id': 1,
    'start_time': '2024-05-20T10:00:00.000Z',
    'end_time': '2024-05-20T12:00:00.000Z'
}

# 发送预约请求
response = requests.post(reservation_url, headers=headers, json=reservation_data)
print('预约请求状态码:', response.status_code)
print('预约响应:', response.json())

if response.status_code != 200:
    print('预约失败')
    exit(1)

# 查询数据库验证总费用
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 获取最新的预约记录
cursor.execute('SELECT * FROM reservations ORDER BY id DESC LIMIT 1')
latest_reservation = cursor.fetchone()

if latest_reservation:
    print('最新预约记录:', latest_reservation)
    print('总费用:', latest_reservation[8])  # total_cost在第9列
else:
    print('没有找到预约记录')

conn.close()
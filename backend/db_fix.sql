-- 修复payments表，删除重复的status列
DROP TABLE IF EXISTS payments;
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    parking_record_id INTEGER,
    reservation_id INTEGER,
    violation_id INTEGER,
    amount REAL NOT NULL,
    pay_method TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    trade_no TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (parking_record_id) REFERENCES parking_records (id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (id),
    FOREIGN KEY (violation_id) REFERENCES violations (id)
);

-- 更新现有记录的默认值
-- 更新parking_spaces表的last_updated_at字段
UPDATE parking_spaces SET last_updated_at = CURRENT_TIMESTAMP WHERE last_updated_at IS NULL;

-- 更新reservations表的created_at字段
UPDATE reservations SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

-- 更新parking_records表的status字段，对于已完成的记录设置为completed
UPDATE parking_records SET status = 'completed' WHERE exit_time IS NOT NULL;

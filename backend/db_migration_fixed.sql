-- 创建新表
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

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unread',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER,
    detail_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users (id)
);

-- 修改现有表
-- parking_lots 表 - 所有默认值都是常量，没有问题
ALTER TABLE parking_lots ADD COLUMN status TEXT NOT NULL DEFAULT 'open';
ALTER TABLE parking_lots ADD COLUMN open_time TEXT DEFAULT '00:00';
ALTER TABLE parking_lots ADD COLUMN close_time TEXT DEFAULT '24:00';
ALTER TABLE parking_lots ADD COLUMN contact_phone TEXT;

-- parking_spaces 表 - 需要先添加列，再更新默认值
ALTER TABLE parking_spaces ADD COLUMN type TEXT DEFAULT 'normal';
ALTER TABLE parking_spaces ADD COLUMN last_updated_at TEXT;
-- 更新现有记录的默认值
UPDATE parking_spaces SET type = 'normal' WHERE type IS NULL;
UPDATE parking_spaces SET last_updated_at = CURRENT_TIMESTAMP WHERE last_updated_at IS NULL;
-- 修改列约束为NOT NULL
UPDATE parking_spaces SET type = 'normal' WHERE type IS NULL;
UPDATE parking_spaces SET last_updated_at = CURRENT_TIMESTAMP WHERE last_updated_at IS NULL;

-- reservations 表 - 需要先添加列，再更新默认值
ALTER TABLE reservations ADD COLUMN payment_status TEXT DEFAULT 'unpaid';
ALTER TABLE reservations ADD COLUMN created_at TEXT;
ALTER TABLE reservations ADD COLUMN canceled_at TEXT;
ALTER TABLE reservations ADD COLUMN checkin_time TEXT;
-- 更新现有记录的默认值
UPDATE reservations SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

-- parking_records 表 - 需要先添加列，再更新默认值
ALTER TABLE parking_records ADD COLUMN parking_space_id INTEGER;
ALTER TABLE parking_records ADD COLUMN reservation_id INTEGER;
ALTER TABLE parking_records ADD COLUMN status TEXT DEFAULT 'in_progress';
-- 更新现有记录的默认值
UPDATE parking_records SET status = 'in_progress' WHERE status IS NULL;
-- 对于已经完成的记录，更新状态为completed
UPDATE parking_records SET status = 'completed' WHERE exit_time IS NOT NULL;

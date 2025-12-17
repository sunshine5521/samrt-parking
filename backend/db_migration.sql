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
-- parking_lots 表
ALTER TABLE parking_lots ADD COLUMN status TEXT NOT NULL DEFAULT 'open';
ALTER TABLE parking_lots ADD COLUMN open_time TEXT DEFAULT '00:00';
ALTER TABLE parking_lots ADD COLUMN close_time TEXT DEFAULT '24:00';
ALTER TABLE parking_lots ADD COLUMN contact_phone TEXT;

-- parking_spaces 表
ALTER TABLE parking_spaces ADD COLUMN type TEXT NOT NULL DEFAULT 'normal';
ALTER TABLE parking_spaces ADD COLUMN last_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- reservations 表
ALTER TABLE reservations ADD COLUMN payment_status TEXT DEFAULT 'unpaid';
ALTER TABLE reservations ADD COLUMN created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE reservations ADD COLUMN canceled_at TEXT;
ALTER TABLE reservations ADD COLUMN checkin_time TEXT;

-- parking_records 表
ALTER TABLE parking_records ADD COLUMN parking_space_id INTEGER;
ALTER TABLE parking_records ADD COLUMN reservation_id INTEGER;
ALTER TABLE parking_records ADD COLUMN status TEXT NOT NULL DEFAULT 'in_progress';
ALTER TABLE parking_records ADD FOREIGN KEY (parking_space_id) REFERENCES parking_spaces (id);
ALTER TABLE parking_records ADD FOREIGN KEY (reservation_id) REFERENCES reservations (id);

# database.py - BẢN ĐÃ FIX LỖI SYNTAX VÀ LỖI DỮ LIỆU
import sqlite3
import pandas as pd
import hashlib

DB_FILE = 'logistics.db'

def get_connection():
    """Tạo kết nối tới SQLite"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def init_system():
    """Khởi tạo bảng nếu chưa có (Đảm bảo schema English)"""
    conn = get_connection(); c = conn.cursor()
    
    # 1. Bảng User
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, role TEXT, full_name TEXT
        )
    ''')
    
    # 2. Bảng Kho hàng (Inventory)
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, category TEXT, cost_price REAL, selling_price REAL,
            stock_quantity INTEGER, weight REAL, created_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Bảng Giao dịch (Transactions - Đã có đủ cột địa chỉ)
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT, action TEXT, product_name TEXT, quantity INTEGER, note TEXT,
            order_type TEXT, destination_address TEXT, origin_depot TEXT
        )
    ''')
    
    # Tạo Admin mặc định
    try:
        pw = hashlib.sha256(str.encode("123")).hexdigest()
        c.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", 
                  ('admin', pw, 'Admin', 'System Administrator'))
        c.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", 
                  ('staff', pw, 'Staff', 'Warehouse Staff'))
    except: pass
    
    conn.commit()
    conn.close()


# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---

def load_data():
    """Tải dữ liệu tồn kho từ SQL"""
    conn = get_connection()
    try:
        df = pd.read_sql('SELECT * FROM inventory', conn)
    except Exception as e:
        df = pd.DataFrame()
    conn.close()
    return df

def log_action(user, action, product, qty, note="", order_type="N/A", destination="N/A", origin="N/A"):
    """Ghi nhật ký giao dịch"""
    conn = get_connection(); c = conn.cursor()
    c.execute('INSERT INTO transactions (user, action, product_name, quantity, note, order_type, destination_address, origin_depot) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
              (user, action, product, qty, note, order_type, destination, origin))
    conn.commit(); conn.close()

def get_product_names():
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT product_name FROM inventory")
    data = [row[0] for row in c.fetchall()]
    conn.close()
    return data

def get_product_info(name):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT * FROM inventory WHERE product_name=?", (name,))
    data = c.fetchone()
    conn.close()
    return data

def add_item_sql(name, cat, cost, sell, stock, weight, user):
    conn = get_connection(); c = conn.cursor()
    c.execute('''
        INSERT INTO inventory (product_name, category, cost_price, selling_price, stock_quantity, weight, created_by) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, cat, cost, sell, stock, weight, user))
    conn.commit(); conn.close()

def process_sale_sql(name, qty, seller, revenue_vnd, order_type, destination, origin):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT stock_quantity FROM inventory WHERE product_name=?", (name,))
    current_stock = c.fetchone()[0]
    
    if current_stock < qty:
        conn.close(); return False, f"❌ Insufficient stock! Current: {current_stock}"
    
    new_stock = current_stock - qty
    c.execute("UPDATE inventory SET stock_quantity=? WHERE product_name=?", (new_stock, name))
    
    # Ghi log với đầy đủ thông tin địa chỉ
    c.execute('''
        INSERT INTO transactions (user, action, product_name, quantity, note, order_type, destination_address, origin_depot) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (seller, "OUTBOUND", name, qty, f"Revenue: {revenue_vnd}", order_type, destination, origin))
    
    conn.commit(); conn.close()
    return True, "✅ Sales processed successfully!"

def get_transactions_sql():
    """Lấy dữ liệu giao dịch cho báo cáo"""
    conn = get_connection()
    try:
        df = pd.read_sql('SELECT * FROM transactions', conn)
    except Exception as e:
        df = pd.DataFrame()
    conn.close()
    return df
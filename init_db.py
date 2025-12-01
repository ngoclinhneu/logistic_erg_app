import sqlite3
import hashlib 
import random
import datetime

# --- CONFIGURATION ---
DB_NAME = "logistics.db"

def hash_password(password):
    """Encrypt password using SHA-256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. TABLE: USERS (Authentication)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- 'Admin' or 'Staff'
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. TABLE: INVENTORY (English Columns)
    # Lưu ý: Tên cột đã được đổi sang Tiếng Anh để khớp với App mới
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            cost_price REAL,
            selling_price REAL,
            stock_quantity INTEGER,
            weight REAL,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. TABLE: TRANSACTIONS (History/Audit Log)
    # Bảng này cần thiết cho tính năng Lịch sử và AI Dự báo
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            action TEXT,
            product_name TEXT,
            quantity INTEGER,
            note TEXT
        )
    ''')
    
    # --- DATA SEEDING ---
    
    # A. Create Users (Default Password: 123)
    hashed_pass = hash_password("123")
    
    users_data = [
        ('admin', hashed_pass, 'Admin', 'System Administrator'),
        ('staff', hashed_pass, 'Staff', 'Warehouse Staff'),
        ('sales', hashed_pass, 'Staff', 'Sales Representative')
    ]
    
    try:
        c.executemany('INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)', users_data)
        print("✅ Created Users successfully (Pass: 123)")
    except sqlite3.IntegrityError:
        print("ℹ️ Users already exist.")

    # B. Generate 50 Mock Products
    products = ["iPhone 15", "Samsung Galaxy", "MacBook Air", "Sony Headphone", "Dell XPS", "Logitech Mouse", "Mechanical Keyboard", "LG Monitor", "iPad Pro", "AirPods"]
    categories = ["Electronics", "Computers", "Accessories", "Gadgets"]
    
    inventory_data = []
    for _ in range(50):
        name = f"{random.choice(products)} {random.randint(100, 999)}" # Ex: iPhone 15 101
        cat = random.choice(categories)
        cost = random.randint(50, 2000) * 10000 # 500k to 20m
        price = cost * random.uniform(1.2, 1.5) # Profit margin 20-50%
        stock = random.randint(0, 100)
        weight = round(random.uniform(0.1, 3.0), 1)
        
        inventory_data.append((name, cat, cost, price, stock, weight, 'Admin'))
        
    c.executemany('''
        INSERT INTO inventory (product_name, category, cost_price, selling_price, stock_quantity, weight, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', inventory_data)
    
    print(f"✅ Generated {len(inventory_data)} mock inventory items.")

    conn.commit()
    conn.close()
    print(f"🚀 Database '{DB_NAME}' is ready! You can run the App now.")

if __name__ == "__main__":
    create_database()
import datetime
from datetime import timedelta
import random
from fpdf import FPDF
import unicodedata
import math
import pytz
from database import get_connection

CURRENCY_RATES = {
    "VND": {"rate": 1, "symbol": "₫", "locale": "{:,.0f}"},
    "USD": {"rate": 25400, "symbol": "$", "locale": "{:,.2f}"},
    "CNY": {"rate": 3500, "symbol": "¥", "locale": "{:,.2f}"},
    "EUR": {"rate": 27000, "symbol": "€", "locale": "{:,.2f}"}
}

def create_invoice_pdf(customer, order_type, address, product, qty, price, total, seller, curr_symbol):
    def remove_accents(input_str):
        if not isinstance(input_str, str): return str(input_str)
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    symbol_to_code = {"$": "USD", "₫": "VND", "¥": "CNY", "€": "EUR"}
    currency_code = symbol_to_code.get(curr_symbol, "VND")
    
    TIMEZONES = {
        "USD": "America/New_York",
        "VND": "Asia/Ho_Chi_Minh",
        "CNY": "Asia/Shanghai",
        "EUR": "Europe/Paris"
    }
    
    try:
        tz = pytz.timezone(TIMEZONES.get(currency_code, "Asia/Ho_Chi_Minh"))
        current_time_str = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    except:
        current_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    safe_curr = symbol_to_code.get(curr_symbol, "UNIT")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 10, txt="SALES INVOICE", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="NGOC LINH LOGISTICS GLOBAL", ln=1, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.cell(200, 8, txt=f"Date: {current_time_str}", ln=1)
    pdf.cell(200, 8, txt=remove_accents(f"Order Type: {order_type}"), ln=1) # <--- Đã nhận tham số mới
    pdf.cell(200, 8, txt=remove_accents(f"Customer: {customer}"), ln=1)
    
    if address:
        pdf.multi_cell(0, 8, txt=remove_accents(f"Ship To: {address}")) # <--- Đã nhận tham số mới
        
    pdf.cell(200, 8, txt=remove_accents(f"Seller: {seller}"), ln=1)
    pdf.cell(200, 8, txt=f"Currency: {safe_curr}", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Product", 1); pdf.cell(30, 10, "Qty", 1); pdf.cell(40, 10, "Price", 1); pdf.cell(40, 10, "Total", 1); pdf.ln()
    pdf.set_font("Arial", size=12)
    fmt_price = f"{price:,.2f}"
    fmt_total = f"{total:,.2f}"
    pdf.cell(80, 10, remove_accents(product), 1)
    pdf.cell(30, 10, str(qty), 1)
    pdf.cell(40, 10, fmt_price, 1)
    pdf.cell(40, 10, fmt_total, 1)
    pdf.ln(20)
    pdf.cell(200, 10, txt="Thank you for your business!", ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def generate_fake_sales():
    conn = get_connection(); c = conn.cursor()
    try: c.execute("SELECT product_name, selling_price FROM inventory"); products = c.fetchall()
    except: return False, "Database Error."
    if not products: return False, "Inventory is empty!"
    count = 0; end_date = datetime.date.today(); start_date = end_date - timedelta(days=30); users = ['Admin', 'Staff']
    for _ in range(200):
        days_offset = random.randint(0, 30); fake_date = start_date + timedelta(days=days_offset); timestamp = datetime.datetime.combine(fake_date, datetime.datetime.min.time()); prod = random.choice(products); qty = random.randint(1, 5); revenue = prod[1] * qty; c.execute('''INSERT INTO transactions (timestamp, user, action, product_name, quantity, note) VALUES (?, ?, ?, ?, ?, ?)''', (timestamp, random.choice(users), "OUTBOUND", prod[0], qty, f"Revenue: {revenue}")); count += 1
    conn.commit(); conn.close(); return True, f"Generated {count} transactions!"

def solve_vrp(locations, truck_capacity):
    import math
    
    if not locations: return [], 0, []
    depot = locations[0] 
    customers = locations[1:] 
    routes = [] 
    current_route = [depot]
    current_load = 0
    current_loc = depot
    total_distance = 0
    ROAD_FACTOR = 1.3 
    
    while customers:
        nearest_dist = float('inf')
        nearest_node = None
        for node in customers:
            item_weight = node.get('weight', 100) 
            if current_load + item_weight <= truck_capacity:
                dist = math.sqrt((current_loc['lat'] - node['lat'])**2 + (current_loc['lon'] - node['lon'])**2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_node = node
        
        if nearest_node:
            current_route.append(nearest_node)
            total_distance += nearest_dist
            current_load += nearest_node.get('weight', 100)
            current_loc = nearest_node
            customers.remove(nearest_node)
        else:
            dist_back = math.sqrt((current_loc['lat'] - depot['lat'])**2 + (current_loc['lon'] - depot['lon'])**2)
            total_distance += dist_back
            current_route.append(depot) 
            routes.append(current_route) 
            current_route = [depot]
            current_load = 0
            current_loc = depot
    if len(current_route) > 1:
        dist_back = math.sqrt((current_loc['lat'] - depot['lat'])**2 + (current_loc['lon'] - depot['lon'])**2)
        total_distance += dist_back
        current_route.append(depot)
        routes.append(current_route)
    return routes, total_distance * 111 * ROAD_FACTOR
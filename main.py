import streamlit as st
import pandas as pd
import time
import math
from datetime import timedelta, datetime
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
import numpy as np
from streamlit_option_menu import option_menu
import plotly.express as px
import pytz
import random
import database as db
import auth
import utils


# --- 1. CẤU HÌNH & TỶ GIÁ ---
st.set_page_config(page_title="NL ERP System", page_icon="🚛", layout="wide")
db.init_system() 
CURRENCY_TIMEZONES = {
    "VND": "Asia/Ho_Chi_Minh",
    "USD": "America/New_York",
    "CNY": "Asia/Shanghai",
    "EUR": "Europe/Paris"
}

def get_current_time_by_currency(currency_code):
    tz_name = CURRENCY_TIMEZONES.get(currency_code, "UTC")
    tz = pytz.timezone(tz_name)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# --- 2. HÀM FORMAT TIỀN TỆ  ---
def format_money(amount, currency):
    """Format tiền tệ dựa trên selection của người dùng."""
    converted = amount / utils.CURRENCY_RATES[currency]['rate']
    fmt = utils.CURRENCY_RATES[currency]['locale']
    return f"{utils.CURRENCY_RATES[currency]['symbol']} {fmt.format(converted)}"

# --- QUẢN LÝ SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = ''
if 'full_name' not in st.session_state: st.session_state['full_name'] = ''
if 'username' not in st.session_state: st.session_state['username'] = ''

# --- GIAO DIỆN LOGIN  ---
def login_page():
    st.markdown("""
    <style>
        .stApp { background-color: #f8f9fa; }
        [data-testid="stSidebar"] { display: none; } header { visibility: hidden; }
        .stButton button { width: 100%; background-color: #d63031 !important; color: white !important; font-weight: bold; padding: 10px; border: none; }
        .big-title { text-align: center; font-size: 48px; font-weight: 900; color: #d63031; margin-bottom: 0px; font-family: 'Arial', sans-serif; }
        .small-text { text-align: center; color: gray; margin-bottom: 30px; }
    </style> """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="big-title">NL ERP</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-text">Hệ thống quản lý kho vận</div>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Tài khoản", placeholder="admin")
            p = st.text_input("Mật khẩu", type="password", placeholder="123")
            st.write("")
            if st.form_submit_button("ĐĂNG NHẬP"):
                user = auth.check_login(u, p)
                if user:
                    st.session_state['logged_in'] = True; st.session_state['user_role'] = user[0]; st.session_state['full_name'] = user[1]; st.session_state['username'] = u; st.success("OK!"); time.sleep(0.5); st.rerun()
                else: st.error("Sai tài khoản/mật khẩu")

# --- GIAO DIỆN CHÍNH (SAU KHI LOGIN) ---
def main_app():
    # Header & Sidebar CSS
    st.markdown("""
    <style>
        .header {position: fixed; top:0; left:0; width:100%; height:60px; background:white; z-index:99; padding:0 20px; border-bottom:3px solid #003366; display:flex; align-items:center;}
        .block-container {padding-top:80px;}
        [data-testid="stSidebar"] {background-color:#212529;}
    </style>
    <div class="header">
        <h3 style="margin-left:15px; color:#003366; font-weight: bold; font-family: sans-serif;">NGOC LINH LOGISTICS (GLOBAL)</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white;'>🌐 Currency</h3>", unsafe_allow_html=True)
        currency = st.selectbox("Display Currency", list(utils.CURRENCY_RATES.keys()), key='currency')
        current_time_str = get_current_time_by_currency(currency)
        st.markdown(f"<p style='color: #00ff00; font-weight: bold;'>🕒 {current_time_str}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ddd; font-size: 12px;'>Rate: 1 {currency} = {utils.CURRENCY_RATES[currency]['rate']} VND</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"<div style='color:white; font-size:14px; margin-bottom:10px;'>User: <b>{st.session_state['full_name']}</b></div>", unsafe_allow_html=True)
        
        # MENU FULL OPTION + TRANSPORT
        menu_ops = ["DASHBOARD", "INVENTORY", "SALES (POS)", "INBOUND", "TRANSPORT", "TRANSACTIONS", "REPORTS (AI)", "ADMIN & SETTINGS"]
        icons_ops = ['speedometer2', 'box-seam', 'cart-check', 'box-arrow-in-down', 'truck', 'clock', 'graph-up-arrow', 'gear']
        
        selected = option_menu(None, menu_ops, icons=icons_ops, default_index=0,
                             styles={"nav-link-selected": {"background-color": "#003366"}})
        if st.button("Logout", use_container_width=True): st.session_state['logged_in'] = False; st.rerun()

    df_stock = db.load_data()

    # 1. DASHBOARD
    if selected == "DASHBOARD":
        st.title("📊 Executive Dashboard")
        st.caption(f"Last Updated: {get_current_time_by_currency(currency)} ({currency} Timezone)")
        if not df_stock.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total SKU", len(df_stock))
            total_val = df_stock['cost_price'].sum(); profit = (df_stock['selling_price'] - df_stock['cost_price']).sum()
            
            c2.metric(f"Inventory Value ({currency})", format_money(total_val, currency))
            c3.metric(f"Proj. Profit ({currency})", format_money(profit, currency))
        else: st.info("Database empty.")

    # 2. INVENTORY
    elif selected == "INVENTORY":
        st.title("📦 Live Inventory")
        if not df_stock.empty:
            df_display = df_stock.copy()
            rate = utils.CURRENCY_RATES[currency]['rate']
            df_display['cost_price'] /= rate; df_display['selling_price'] /= rate
            fmt = f"%.2f {utils.CURRENCY_RATES[currency]['symbol']}"
            st.dataframe(df_display, use_container_width=True, hide_index=True, column_config={"stock_quantity": st.column_config.ProgressColumn("Stock", max_value=100), "cost_price": st.column_config.NumberColumn("Cost", format=fmt), "selling_price": st.column_config.NumberColumn("Selling", format=fmt)})

    # 3. SALES (POS)
    elif selected == "SALES (POS)":
        st.title("🛒 Sales & Outbound")
        c1, c2 = st.columns([1, 1])
        with c1:
            try:
                lst = db.get_product_names()
                if lst:
                    # INPUTS ĐỊA CHỈ VÀ LOẠI ĐƠN HÀNG
                    order_type = st.selectbox("Order Type", [
                        "Retail/Walk-in",     
                        "Online (E-commerce)", 
                        "Wholesale (B2B)"     
                    ])                    
                    origin = st.selectbox("Origin Depot", ["Warehouse A (HCM)", "Warehouse B (Hanoi)"])
                    destination = st.text_area("Destination Address", placeholder="VD: 123 Đường ABC, Quận 1...")
                    st.divider()
                    
                    sp = st.selectbox("Select Product", lst); inf = db.get_product_info(sp); pr = inf[4]; stk = inf[5]
                    st.info(f"Price: {format_money(pr, currency)} | Stock: {stk}")
                    cus = st.text_input("Customer Name", "Walk-in"); q = st.number_input("Quantity", 1)
                    total_vnd = q * pr
                    st.metric(f"TOTAL ({currency})", format_money(total_vnd, currency))
                    
                    if st.button("PROCESS SALE", type="primary"):
                        if "Online" in order_type and not destination:
                            st.error("⚠️ Đơn hàng Online bắt buộc phải nhập Địa chỉ giao hàng!")
                        else:
                            suc, msg = db.process_sale_sql(sp, q, st.session_state['user_role'], total_vnd, order_type, destination, origin)
                            if suc:
                                st.success(msg); rt = utils.CURRENCY_RATES[currency]['rate']; sym = utils.CURRENCY_RATES[currency]['symbol']
                                
                                pdf = utils.create_invoice_pdf(cus, order_type, destination, sp, q, pr/rt, (q*pr)/rt, st.session_state['full_name'], sym)
                                st.download_button("🖨️ DOWNLOAD INVOICE", pdf, f"inv_{int(time.time())}.pdf", "application/pdf")
                            else: st.error(msg)
                else: st.warning("No products available.")
            except Exception as e: st.error(f"Error: {e}")

    # 4. INBOUND
    elif selected == "INBOUND":
        st.title("📥 Inbound Operations")
        st.caption("⚠️ Please enter prices in VND (Base Currency).")
        tab1, tab2 = st.tabs(["Manual Entry", "Bulk Import"])
        with tab1:
            with st.form("in"):
                c1,c2=st.columns(2); nm=c1.text_input("Name")
                CATEGORY_LIST = [
                    "Electronics", "Fashion", "Home & Living", 
                    "FMCG", "Health & Beauty", "Automotive", 
                    "Industrial", "Sports", "Books", "Others"
                ]
                ct=c2.selectbox("Category", CATEGORY_LIST); cs=c1.number_input("Cost (VND)",0.0); sl=c2.number_input("Sell (VND)",0.0); qt=c1.number_input("Qty",1); wt=c2.number_input("Weight",0.1)
                if st.form_submit_button("ADD"): db.add_item_sql(nm, ct, cs, sl, qt, wt, st.session_state['user_role']); db.log_action(st.session_state['full_name'], "INBOUND", nm, qt); st.success("Added!"); time.sleep(1); st.rerun()
        with tab2:
            st.write("Upload Excel/CSV file with columns: Name, Category, Cost, Price, Qty, Weight")
            upl = st.file_uploader("Upload File", type=['csv', 'xlsx'])
            if upl and st.button("CONFIRM IMPORT"):
                try:
                    df = pd.read_csv(upl) if upl.name.endswith('.csv') else pd.read_excel(upl)
                    conn = db.get_connection(); c = conn.cursor()
                    for i, r in df.iterrows(): c.execute("INSERT INTO inventory (product_name, category, cost_price, selling_price, stock_quantity, weight, created_by) VALUES (?,?,?,?,?,?,?)", (r['Name'], r['Category'], r['Cost'], r['Price'], r['Qty'], r['Weight'], st.session_state['user_role']))
                    conn.commit(); conn.close(); st.success(f"Imported {len(df)} items!"); time.sleep(1); st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    # 5. TRANSACTIONS (LỊCH SỬ NHẬP XUẤT) [KHÔI PHỤC]
    elif selected == "TRANSACTIONS":
        st.title("📜 System Audit Log")
        st.caption(f"All timestamps are displayed in System Time (Vietnam/UTC+7). Current View Mode: {currency}")
        conn = db.get_connection()
        df_log = pd.read_sql("SELECT * FROM transactions ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df_log.empty:
            st.dataframe(
                df_log, use_container_width=True, hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Thời gian", format="D/M/Y, h:m:s"),
                    "action": "Hành động",
                    "product_name": "Sản phẩm",
                    "quantity": st.column_config.NumberColumn("SL"),
                    "user": "Người thực hiện",
                    "note": "Ghi chú (Doanh thu)",
                }
            )
        else:
            st.info("Chưa có lịch sử giao dịch.")

    # 6. TRANSPORT (VẬN CHUYỂN - TỰ ĐỘNG HÓA)
    elif selected == "TRANSPORT":
        st.title("🚛 Route Optimization (Map)")
        st.caption("Tối ưu hóa lộ trình giao hàng từ dữ liệu đơn hàng thực tế.")
        
        # Khởi tạo Geocoder
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="nl_logistics_app_v2")

        col_map, col_list = st.columns([2, 1])
        
        # Khởi tạo state nếu chưa có
        if 'delivery_points' not in st.session_state:
            st.session_state['delivery_points'] = [{'name': 'KHO TỔNG (Depot)', 'lat': 10.7769, 'lon': 106.7009, 'type': 'depot'}]
            st.session_state['status_msg'] = "Sẵn sàng."

        with col_list:
            st.subheader("📍 Danh Sách Điểm Giao")
            st.info(st.session_state.get('status_msg', ''))
            
            st.divider()
            
            # NÚT TỰ ĐỘNG CẬP NHẬT TỪ ĐƠN HÀNG
            if st.button("🔄 Cập nhật từ Đơn Hàng Mới Nhất", type="primary", use_container_width=True):
                conn = db.get_connection()
                latest_orders = pd.read_sql("""
                    SELECT id, product_name, destination_address, quantity 
                    FROM transactions 
                    WHERE action='OUTBOUND' 
                    AND destination_address IS NOT NULL 
                    AND destination_address != '' 
                    ORDER BY timestamp DESC LIMIT 10
                """, conn)
                conn.close()

                if not latest_orders.empty:
                    new_points = [{'name': 'KHO TỔNG (Depot)', 'lat': 10.7769, 'lon': 106.7009, 'type': 'depot'}]
                    
                    success_count = 0
                    progress_text = "Đang định vị địa chỉ..."
                    my_bar = st.progress(0, text=progress_text)
                    
                    for index, row in latest_orders.iterrows():
                        addr = row['destination_address']
                        my_bar.progress((index + 1) / len(latest_orders), text=f"Đang tìm: {addr}")
                        
                        try:
                            location = geolocator.geocode(addr, timeout=5)
                            
                            if location:
                                new_points.append({
                                    'name': f"ĐH #{row['id']} - {addr[:20]}...", # Tên ngắn gọn
                                    'lat': location.latitude,
                                    'lon': location.longitude,
                                    'type': 'customer',
                                    'info': f"Sản phẩm: {row['product_name']} (x{row['quantity']})"
                                })
                                success_count += 1
                            else:
                                lat_rnd = 10.7769 + random.uniform(-0.05, 0.05)
                                lon_rnd = 106.7009 + random.uniform(-0.05, 0.05)
                                new_points.append({
                                    'name': f"ĐH #{row['id']} (Không tìm thấy tạ độ thực)", 
                                    'lat': lat_rnd,
                                    'lon': lon_rnd, 
                                    'type': 'customer',
                                    'info': f"Địa chỉ gốc: {addr}"
                                })
                                success_count += 1
                                
                        except Exception as e:
                            st.error(f"Lỗi định vị: {e}")
                    
                    my_bar.empty()
                    st.session_state['delivery_points'] = new_points
                    st.session_state['status_msg'] = f"Đã cập nhật {success_count} điểm giao hàng từ đơn hàng."
                    st.rerun()
                else:
                    st.warning("Không tìm thấy đơn hàng Online nào có địa chỉ.")

            # Nút Reset
            if st.button("🗑️ Xóa Lộ Trình", use_container_width=True):
                st.session_state['delivery_points'] = [{'name': 'KHO TỔNG (Depot)', 'lat': 10.7769, 'lon': 106.7009, 'type': 'depot'}]
                st.session_state['status_msg'] = "Đã xóa lộ trình."
                st.rerun()

            # Hiển thị danh sách text
            if len(st.session_state['delivery_points']) > 1:
                st.markdown("---")
                for p in st.session_state['delivery_points'][1:]:
                    st.text(f"📍 {p['name']}")

        with col_map:
            points = st.session_state['delivery_points']
            center_lat = points[0]['lat']
            center_lon = points[0]['lon']
            m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
            
            if len(points) > 1:
                routes, total_km = utils.solve_vrp(points, truck_capacity=1000)
                
                st.success(f"✅ Đã tối ưu: **{len(routes)} chuyến xe**. Tổng quãng đường: **{total_km:.2f} km**")
                
                colors = ['blue', 'green', 'purple', 'orange', 'darkred']
                
                for i, route in enumerate(routes):
                    color = colors[i % len(colors)]
                    
                    # Vẽ đường nối cho từng chuyến xe
                    route_coords = [[p['lat'], p['lon']] for p in route]
                    folium.PolyLine(
                        route_coords, 
                        color=color, 
                        weight=4, 
                        opacity=0.8, 
                        tooltip=f"Chuyến {i+1}"
                    ).add_to(m)
                    
                    # Vẽ các điểm trên tuyến này
                    for p in route:
                        icon_color = 'red' if p['type'] == 'depot' else color
                        icon_type = 'home' if p['type'] == 'depot' else 'gift'
                        
                        popup_content = f"<b>{p['name']}</b><br>{p.get('info', '')}"
                        
                        folium.Marker(
                            [p['lat'], p['lon']], 
                            popup=popup_content, 
                            tooltip=f"{p['name']} (Xe {i+1})",
                            icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
                        ).add_to(m)

                # Hiển thị danh sách chuyến xe dưới bản đồ
                with st.expander("📋 Chi tiết phân tuyến"):
                    for i, route in enumerate(routes):
                        st.markdown(f"**🚛 Chuyến {i+1}**: {' ➔ '.join([p['name'] for p in route])}")
                        
            else:
                # Vẽ kho mặc định nếu chưa có điểm
                folium.Marker([center_lat, center_lon], popup="KHO TỔNG", icon=folium.Icon(color='red', icon='home')).add_to(m)
            
            st_folium(m, width="100%", height=600)
    
    # 7. REPORTS (AI)
    elif selected == "REPORTS (AI)":
        st.title("📈 AI Analytics")
        with st.expander("Tools"): 
            if st.button("Gen Data"): utils.generate_fake_sales(); st.rerun()
        conn = db.get_connection()
        try:
            df_tr = pd.read_sql("SELECT * FROM transactions WHERE action='OUTBOUND'", conn)
            df_tr['Revenue_VND'] = df_tr['note'].str.extract(r'(\d+\.?\d*)').astype(float)
            df_tr['Date'] = pd.to_datetime(df_tr['timestamp'])
            rate = utils.CURRENCY_RATES[currency]['rate']; df_tr['Revenue'] = df_tr['Revenue_VND'] / rate
        except: df_tr = pd.DataFrame()
        conn.close()

        if not df_tr.empty:
            t1, t2, t3, t4 = st.tabs(["Trend", "ABC", "Category", "AI Forecast"])
            with t1:
                daily = df_tr.groupby(df_tr['Date'].dt.date)['Revenue'].sum().reset_index()
                st.plotly_chart(px.line(daily, x='Date', y='Revenue', labels={'Revenue': f'Rev ({currency})'}), use_container_width=True)
            with t2:
                prod_stats = df_tr.groupby('product_name')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
                prod_stats['Cum_Perc'] = 100 * (prod_stats['Revenue'].cumsum() / prod_stats['Revenue'].sum())
                prod_stats['Class'] = prod_stats['Cum_Perc'].apply(lambda x: 'A' if x<=80 else ('B' if x<=95 else 'C'))
                st.plotly_chart(px.scatter(prod_stats, x='product_name', y='Revenue', color='Class', size='Revenue'), use_container_width=True)
            with t3:
                df_inv = db.load_data()[['product_name', 'category']]
                mrg = pd.merge(df_tr, df_inv, on='product_name', how='left').fillna("Unknown")
                st.plotly_chart(px.sunburst(mrg.groupby(['category', 'product_name'])['Revenue'].sum().reset_index(), path=['category', 'product_name'], values='Revenue'), use_container_width=True)
            with t4:
                daily['Day'] = np.arange(len(daily))
                model = LinearRegression(); model.fit(daily[['Day']], daily['Revenue'])
                future = model.predict(np.arange(len(daily), len(daily)+7).reshape(-1, 1))
                dates = [pd.to_datetime(daily['Date'].max()) + timedelta(days=x) for x in range(1, 8)]
                df_f = pd.DataFrame({'Date': dates, 'Revenue': future, 'Type': 'Forecast'}); df_h = pd.DataFrame({'Date': pd.to_datetime(daily['Date']), 'Revenue': daily['Revenue'], 'Type': 'History'})
                st.plotly_chart(px.line(pd.concat([df_h, df_f]), x='Date', y='Revenue', color='Type'), use_container_width=True)
                st.markdown("---"); st.subheader("📦 Smart Replenishment")
                q_stats = df_tr.groupby('product_name')['quantity'].sum().reset_index()
                q_stats['Avg'] = q_stats['quantity'] / 30
                stock = db.load_data()[['product_name', 'stock_quantity']]
                rst = pd.merge(stock, q_stats, on='product_name', how='left').fillna(0)
                rst['Need'] = (rst['Avg'] * 7) - rst['stock_quantity']
                buy = rst[rst['Need'] > 0].copy(); buy['Need'] = buy['Need'].apply(lambda x: int(x)+1)
                if not buy.empty: st.error("Restock Needed"); st.dataframe(buy, use_container_width=True)
                else: st.success("Healthy")

    elif selected == "ADMIN & SETTINGS":
        st.title("⚙️ System Administration")
        tp, tu = st.tabs(["Change Password", "User Management"])
        with tp:
            st.subheader("Change Password")
            with st.form("chg_pass"):
                p1 = st.text_input("New Pass", type="password"); p2 = st.text_input("Confirm", type="password")
                if st.form_submit_button("Update"):
                    if p1==p2 and p1: auth.change_password_sql(st.session_state['username'], p1); st.success("Updated! Relogin."); time.sleep(2); st.session_state['logged_in']=False; st.rerun()
                    else: st.error("Error")
        with tu:
            if st.session_state['user_role'] == 'Admin':
                st.subheader("Create User")
                c1, c2 = st.columns(2); u = c1.text_input("Username"); f = c1.text_input("Fullname"); r = c2.selectbox("Role", ["Staff", "Admin"]); p = c2.text_input("Password", type="password")
                if st.button("Create"):
                    if u and p: s, m = auth.create_user_sql(u, p, r, f);
                    if s: st.success(m); time.sleep(1); st.rerun()
                    else: st.error(m)
                st.markdown("---"); conn = db.get_connection(); usrs = pd.read_sql("SELECT id, username, role, full_name FROM users", conn); conn.close(); st.dataframe(usrs, use_container_width=True)
            else: st.error("Access Denied")

if st.session_state['logged_in']: main_app()
else: login_page()
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="Yalı Balık ERP PRO", page_icon="🌊", layout="wide")

# 2. VERİTABANI BAĞLANTISI VE TABLO OLUŞTURMA
def init_db():
    conn = sqlite3.connect('yali_balik.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tables 
                 (name TEXT PRIMARY KEY, status TEXT, opened_at TEXT, kitchen_status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu 
                 (category TEXT, name TEXT PRIMARY KEY, price REAL, stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, price REAL, method TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations 
                 (table_name TEXT PRIMARY KEY, client_name TEXT, res_time TEXT)''')
    
    c.execute("SELECT count(*) FROM menu")
    if c.fetchone()[0] == 0:
        initial_menu = [
            ('Meze', 'Levrek Marin', 220, 50), ('Meze', 'Atom', 150, 40),
            ('Meze', 'Fava', 130, 40), ('Meze', 'Lakerda', 280, 20),
            ('Rakı', '70lik Rakı', 1450, 10), ('Rakı', 'Duble Rakı', 180, 100),
            ('Denizden', 'Levrek Izgara', 450, 30), ('Denizden', 'Kalamar Tava', 350, 40),
            ('Tatlı', 'Volkanik', 160, 25), ('Tatlı', 'Fırın Helva', 140, 30),
            ('İçecekler', 'Büyük Su', 40, 200), ('İçecekler', 'Şalgam', 50, 100),
            ('Salatalar', 'Roka Salatası', 160, 80)
        ]
        c.executemany("INSERT INTO menu VALUES (?,?,?,?)", initial_menu)
        
        initial_tables = [(f"Deniz {i}", "Boş", None, "Bekliyor") for i in range(1,5)] + \
                         [(f"Salon {i}", "Boş", None, "Bekliyor") for i in range(1,5)]
        c.executemany("INSERT INTO tables VALUES (?,?,?,?)", initial_tables)
        
    conn.commit()
    return conn

conn = init_db()

# CSS TASARIMI (BÜYÜK VE NET YAZILAR)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span { color: #000000 !important; font-weight: bold; }
    .main-title { font-size: 45px; color: #1e3a8a !important; font-weight: 900; text-align: center; }
    
    /* Kullanımı Kolay Büyük Masa ve Ürün Butonları */
    div.stButton > button { 
        border-radius: 12px; border: 2px solid #1e3a8a; 
        color: #000000 !important; background-color: #f1f5f9;
        height: 65px; font-size: 18px; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #1e3a8a; color: white !important; }
    
    /* Küçük Miktar Düzenleme Butonları İçin Özel CSS (+ ve - butonları) */
    .qty-btn button {
        height: 35px !important;
        font-size: 16px !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Kategori Sekme Tasarımları */
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        background-color: #e2e8f0 !important;
        border-radius: 8px 8px 0 0;
        padding: 12px 22px;
    }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: #ffffff !important; }
    </style>
    <div class="main-title">🌊 YALI BALIK PRO ERP</div>
    <p style='text-align:center; color: #64748b !important; font-weight: normal;'>Hızlı Servis ve Adisyon Sistemi v4.4</p>
""", unsafe_allow_html=True)

# GİRİŞ SİSTEMİ
if 'auth' not in st.session_state: st.session_state.auth = None
if st.session_state.auth is None:
    st.markdown("### 🔐 Sisteme Giriş Yapın")
    col_l, _ = st.columns(2)
    pin = col_l.text_input("Personel PIN Kodu", type="password")
    if col_l.button("Giriş Yap"):
        if pin == "1234": st.session_state.auth = "Garson"; st.rerun()
        elif pin == "5678": st.session_state.auth = "Aşçı"; st.rerun()
        elif pin == "0000": st.session_state.auth = "Patron"; st.rerun()
        else: st.error("Hatalı PIN!")
    st.stop()

st.sidebar.write(f"👤 Yetki: **{st.session_state.auth}**")
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state.auth = None
    st.rerun()

def get_tables(): return pd.read_sql("SELECT * FROM tables", conn)
def get_menu(): return pd.read_sql("SELECT * FROM menu", conn)
def get_elapsed(opened_at):
    if not opened_at or str(opened_at) == "None": return ""
    diff = datetime.now() - datetime.strptime(str(opened_at), "%Y-%m-%d %H:%M:%S")
    return f"\n({diff.seconds // 60} dk)"

# ANA SEKMELER
tabs = ["⚓ Salon Planı", "🍳 Mutfak", "📅 Rezervasyon", "📈 Raporlar & Admin"]
if st.session_state.auth == "Aşçı": active_tabs = ["🍳 Mutfak"]
elif st.session_state.auth == "Garson": active_tabs = ["⚓ Salon Planı", "🍳 Mutfak", "📅 Rezervasyon"]
else: active_tabs = tabs

sel_tab = st.sidebar.radio("Menü", active_tabs)

# --- SALON PLANI (KULLANIM ODAKLI) ---
if sel_tab == "⚓ Salon Planı":
    col_map, col_ops = st.columns([5, 4])
    tables_df = get_tables()
    
    with col_map:
        st.subheader("📍 Masa Durumları")
        grid = st.columns(3)
        for i, row in tables_df.iterrows():
            color = "🟢" if row['status'] == "Boş" else "🔴"
            if row['kitchen_status'] == "Hazır": color = "✅"
            res_check = pd.read_sql(f"SELECT * FROM reservations WHERE table_name='{row['name']}'", conn)
            if not res_check.empty and row['status'] == "Boş": color = "🔵"

            label = f"{color} {row['name']}{get_elapsed(row['opened_at'])}"
            if grid[i%3].button(label, key=f"btn_{row['name']}", use_container_width=True):
                st.session_state.active_table = row['name']

    with col_ops:
        if 'active_table' in st.session_state:
            t_name = st.session_state.active_table
            t_info = tables_df[tables_df['name'] == t_name].iloc[0]
            
            st.markdown(f"### 🍽 ... {t_name} ({t_info['status']})")
            
            if t_info['status'] == "Boş":
                if st.button("🔓 Masayı Aç ve Sipariş Al", type="primary", use_container_width=True):
                    conn.execute(f"UPDATE tables SET status='Dolu', opened_at='{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE name='{t_name}'")
                    conn.commit()
                    st.rerun()
            else:
                st.write("---")
                menu_df = get_menu()
                
                # 🔴 ÖZELLİK 3: AKILLI ARAMA ÇUBUĞU
                search_query = st.text_input("🔍 Hızlı Ürün Ara (Örn: Kalamar, Su...)", placeholder="Yazmaya başlayın...")
                
                if search_query.strip() != "":
                    # Arama yapılıyorsa sadece aranan ürünleri büyük butonlar halinde listele
                    st.markdown("🎯 Arama Sonuçları:")
                    filtered_menu = menu_df[menu_df['name'].str.lower().contains(search_query.lower(), na=False)]
                    if filtered_menu.empty:
                        st.info("Ürün bulunamadı.")
                    else:
                        search_cols = st.columns(2)
                        for idx, item_row in filtered_menu.reset_index().iterrows():
                            if search_cols[idx % 2].button(f"➕ {item_row['name']} ({item_row['price']} TL)", key=f"src_{item_row['name']}", use_container_width=True):
                                conn.execute("INSERT INTO sales (item_name, price, method, date) VALUES (?,?,?,?)", (item_row['name'], item_row['price'], "Bekliyor", t_name))
                                conn.execute(f"UPDATE menu SET stock = stock - 1 WHERE name='{item_row['name']}'")
                                conn.commit()
                                st.rerun()
                else:
                    # 🔴 ÖZELLİK 1: SEKMELİ KATEGORİLER VE "EN ÇOK SATANLAR"
                    categories = ["🔥 En Çok Satanlar"] + list(menu_df['category'].unique())
                    menu_tabs = st.tabs(categories)
                    
                    # EN ÇOK SATANLAR SEKMESİ (Sabit Hızlı Seçim Ürünleri)
                    with menu_tabs[0]:
                        fast_items = ["Büyük Su", "Roka Salatası", "Şalgam", "Levrek Marin"]
                        fast_df = menu_df[menu_df['name'].isin(fast_items)]
                        f_cols = st.columns(2)
                        for idx, item_row in fast_df.reset_index().iterrows():
                            if f_cols[idx % 2].button(f"⭐ {item_row['name']}\n{item_row['price']} TL", key=f"fast_{item_row['name']}", use_container_width=True):
                                conn.execute("INSERT INTO sales (item_name, price, method, date) VALUES (?,?,?,?)", (item_row['name'], item_row['price'], "Bekliyor", t_name))
                                conn.execute(f"UPDATE menu SET stock = stock - 1 WHERE name='{item_row['name']}'")
                                conn.commit()
                                st.rerun()
                    
                    # DİĞER STANDART KATEGORİLER
                    for index, cat_name in enumerate(categories[1:], start=1):
                        with menu_tabs[index]:
                            cat_items = menu_df[menu_df['category'] == cat_name]
                            btn_cols = st.columns(2)
                            for item_idx, item_row in cat_items.reset_index().iterrows():
                                btn_label = f"{item_row['name']}\n{item_row['price']} TL (Stok: {item_row['stock']})"
                                if btn_cols[item_idx % 2].button(btn_label, key=f"add_{t_name}_{item_row['name']}", use_container_width=True):
                                    if item_row['stock'] >= 1:
                                        conn.execute("INSERT INTO sales (item_name, price, method, date) VALUES (?,?,?,?)", (item_row['name'], item_row['price'], "Bekliyor", t_name))
                                        conn.execute(f"UPDATE menu SET stock = stock - 1 WHERE name='{item_row['name']}'")
                                        conn.execute(f"UPDATE tables SET kitchen_status='Mutfakta' WHERE name='{t_name}'")
                                        conn.commit()
                                        st.rerun()
                                    else: st.error("Stok bitti!")
                
                # --- GÜNCEL ADİSÝON VE MİKTAR AYARLAMA ---
                st.write("---")
                st.markdown("#### 🧾 Güncel Adisyon")
                active_sales = pd.read_sql(f"SELECT * FROM sales WHERE date='{t_name}' AND method='Bekliyor'", conn)
                
                if active_sales.empty:
                    st.info("Adisyon boş.")
                else:
                    # Ürünleri gruplayıp miktarlarını hesaplıyoruz
                    summary = active_sales.groupby('item_name').agg(
                        Adet=('id', 'count'),
                        Tek_Fiyat=('price', 'first')
                    ).reset_index()
                    
                    # 🔴 ÖZELLİK 2: ADİSYON İÇİNDE ANLIK + / - BUTONLARI
                    for _, s_row in summary.iterrows():
                        c_name, c_qty, c_price = s_row['item_name'], s_row['Adet'], s_row['Tek_Fiyat']
                        
                        col_item, col_minus, col_qty, col_plus = st.columns([5, 1, 1, 1])
                        col_item.write(f"🔹 **{c_name}** ({c_price * c_qty} TL)")
                        col_qty.markdown(f"<p style='text-align:center; font-size:18px;'>{c_qty}</p>", unsafe_allow_html=True)
                        
                        # Eksi Butonu (Miktarı azaltır, 1 ise tamamen siler)
                        st.markdown('<div class="qty-btn">', unsafe_allow_html=True)
                        if col_minus.button("➖", key=f"min_{t_name}_{c_name}"):
                            # En son eklenen 1 adet kaydı bul ve sil
                            last_id = active_sales[active_sales['item_name'] == c_name]['id'].max()
                            conn.execute(f"DELETE FROM sales WHERE id={last_id}")
                            conn.execute(f"UPDATE menu SET stock = stock + 1 WHERE name='{c_name}'")
                            conn.commit()
                            st.rerun()
                            
                        # Artı Butonu (Miktarı artırır)
                        if col_plus.button("➕", key=f"pls_{t_name}_{c_name}"):
                            conn.execute("INSERT INTO sales (item_name, price, method, date) VALUES (?,?,?,?)", (c_name, c_price, "Bekliyor", t_name))
                            conn.execute(f"UPDATE menu SET stock = stock - 1 WHERE name='{c_name}'")
                            conn.commit()
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    total_val = active_sales['price'].sum()
                    st.markdown(f"### 💰 Toplam Hesap: {total_val} TL")
                    
                    method = st.radio("Ödeme", ["Nakit", "Kredi Kartı"], horizontal=True)
                    if st.button("💵 Tahsil Et ve Masayı Kapat", type="primary", use_container_width=True):
                        conn.execute(f"UPDATE sales SET method='{method}', date='{datetime.now().strftime('%Y-%m-%d')}' WHERE date='{t_name}'")
                        conn.execute(f"UPDATE tables SET status='Boş', opened_at=NULL, kitchen_status='Bekliyor' WHERE name='{t_name}'")
                        conn.commit()
                        st.rerun()

# --- DİĞER MODÜLLER (MUTFAK, REZERVASYON, RAPOR) DEĞİŞMEDİ ---
elif sel_tab == "🍳 Mutfak":
    st.subheader("👨‍🍳 Pişirme Listesi")
    active_orders = pd.read_sql("SELECT * FROM sales WHERE method='Bekliyor'", conn)
    if active_orders.empty: st.success("Mutfak temiz!")
    else:
        for masa in active_orders['date'].unique():
            with st.expander(f"🔔 {masa} Siparişleri", expanded=True):
                st.table(active_orders[active_orders['date'] == masa][['item_name', 'price']])
                if st.button(f"Masa {masa} Hazır!", key=f"k_{masa}"):
                    conn.execute(f"UPDATE tables SET kitchen_status='Hazır' WHERE name='{masa}'")
                    conn.commit()
                    st.rerun()
elif sel_tab == "📅 Rezervasyon":
    st.subheader("📝 Rezervasyon")
    c1, c2, c3 = st.columns(3)
    if st.button("Rezervasyonu Kaydet"):
        conn.execute("INSERT OR REPLACE INTO reservations VALUES (?,?,?)", (c2.selectbox("Masa", get_tables()['name']), c1.text_input("Ad"), c3.text_input("Saat")))
        conn.commit()
elif sel_tab == "📈 Raporlar & Admin":
    sales_df = pd.read_sql("SELECT * FROM sales WHERE method != 'Bekliyor'", conn)
    if not sales_df.empty: st.metric("Toplam Hasılat", f"{sales_df['price'].sum()} TL"); st.plotly_chart(px.pie(sales_df, values='price', names='item_name', title='Satış Dağılımı'))
    st.dataframe(get_menu(), use_container_width=True)
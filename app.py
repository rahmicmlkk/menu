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
            ('Tatlı', 'Volkanik', 160, 25), ('Tatlı', 'Fırın Helva', 140, 30)
        ]
        c.executemany("INSERT INTO menu VALUES (?,?,?,?)", initial_menu)
        
        initial_tables = [(f"Deniz {i}", "Boş", None, "Bekliyor") for i in range(1,5)] + \
                         [(f"Salon {i}", "Boş", None, "Bekliyor") for i in range(1,5)]
        c.executemany("INSERT INTO tables VALUES (?,?,?,?)", initial_tables)
        
    conn.commit()
    return conn

conn = init_db()

# CSS TASARIMI
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span { color: #000000 !important; font-weight: 500; }
    .main-title { font-size: 45px; color: #1e3a8a !important; font-weight: 900; text-align: center; }
    
    /* Masa ve Fonksiyon Butonları */
    div.stButton > button { 
        border-radius: 12px; border: 2px solid #1e3a8a; 
        color: #000000 !important; background-color: #f1f5f9;
        height: 60px; font-size: 18px; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #1e3a8a; color: white !important; }
    
    /* Kategori Sekme Tasarımları (Koyu ve Net) */
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        background-color: #e2e8f0 !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        margin-right: 4px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    </style>
    <div class="main-title">🌊 YALI BALIK PRO ERP</div>
    <p style='text-align:center; color: #64748b !important;'>Kurumsal Restoran Yönetim Sistemi v4.3</p>
""", unsafe_allow_html=True)

# 3. GİRİŞ SİSTEMİ (AUTH)
if 'auth' not in st.session_state:
    st.session_state.auth = None

if st.session_state.auth is None:
    st.markdown("### 🔐 Sisteme Giriş Yapın")
    col_l, col_r = st.columns(2)
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

# 4. FONKSİYONLAR
def get_tables(): return pd.read_sql("SELECT * FROM tables", conn)
def get_menu(): return pd.read_sql("SELECT * FROM menu", conn)

def get_elapsed(opened_at):
    if not opened_at or opened_at is None or str(opened_at).strip() == "" or str(opened_at) == "None": 
        return ""
    try:
        diff = datetime.now() - datetime.strptime(str(opened_at), "%Y-%m-%d %H:%M:%S")
        return f"\n({diff.seconds // 60} dk)"
    except:
        return ""

if 'menu_message' not in st.session_state:
    st.session_state.menu_message = None

# 5. ANA SEKMELER
tabs = ["⚓ Salon Planı", "🍳 Mutfak", "📅 Rezervasyon", "📈 Raporlar & Admin"]
if st.session_state.auth == "Aşçı": active_tabs = ["🍳 Mutfak"]
elif st.session_state.auth == "Garson": active_tabs = ["⚓ Salon Planı", "🍳 Mutfak", "📅 Rezervasyon"]
else: active_tabs = tabs

sel_tab = st.sidebar.radio("Menü", active_tabs)

# ==========================================
# SEKMELERİN İÇERİĞİ
# ==========================================

# --- SALON PLANI ---
if sel_tab == "⚓ Salon Planı":
    # Ekranı ikiye bölüyoruz: Sol taraf masalar, sağ taraf adisyon işlemleri
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
            
            st.markdown(f"### 🍽️ Masa: {t_name} ({t_info['status']})")
            
            # 🔴 ÖZELLİK 2: Masa boşsa aç butonu göster, basıldığı an durumu kaydet ve direkt içine gir
            if t_info['status'] == "Boş":
                if st.button("🔓 Masayı Aç ve Sipariş Al", type="primary", use_container_width=True):
                    conn.execute(f"UPDATE tables SET status='Dolu', opened_at='{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE name='{t_name}'")
                    conn.commit()
                    st.rerun()
            else:
                # Masa doluysa veya yeni açıldıysa burası otomatik olarak listelenir
                st.write("---")
                
                # 🔴 ÖZELLİK 1: KATEGORİ SEKMELERİNİ GERİ GETİRME VE SİPARİŞ ALMA
                st.markdown("#### 🦀 Menü Kategorileri")
                menu_df = get_menu()
                categories = menu_df['category'].unique()
                menu_tabs = st.tabs(list(categories))
                
                for index, cat_name in enumerate(categories):
                    with menu_tabs[index]:
                        cat_items = menu_df[menu_df['category'] == cat_name]
                        # Ürünleri yan yana 2'li butonlar halinde listele
                        btn_cols = st.columns(2)
                        for item_idx, item_row in cat_items.reset_index().iterrows():
                            btn_label = f"{item_row['name']}\n({item_row['price']} TL) - Stok: {item_row['stock']}"
                            
                            if btn_cols[item_idx % 2].button(btn_label, key=f"add_{t_name}_{item_row['name']}", use_container_width=True):
                                if item_row['stock'] >= 1:
                                    # Satış kaydı ekle
                                    conn.execute("INSERT INTO sales (item_name, price, method, date) VALUES (?,?,?,?)",
                                                 (item_row['name'], item_row['price'], "Bekliyor", t_name))
                                    # Stok düş
                                    conn.execute(f"UPDATE menu SET stock = stock - 1 WHERE name='{item_row['name']}'")
                                    # Mutfak durumunu güncelle
                                    conn.execute(f"UPDATE tables SET kitchen_status='Mutfakta' WHERE name='{t_name}'")
                                    conn.commit()
                                    st.success(f"➕ {item_row['name']} adisyona eklendi!")
                                    st.rerun()
                                else:
                                    st.error("⚠️ Yetersiz Stok!")
                
                # Mevcut Adisyon Listesi ve Hesap Kapatma
                st.write("---")
                st.markdown("#### 🧾 Güncel Adisyon")
                active_sales = pd.read_sql(f"SELECT * FROM sales WHERE date='{t_name}' AND method='Bekliyor'", conn)
                
                if active_sales.empty:
                    st.info("Bu masaya ait henüz bir sipariş girilmemiş.")
                else:
                    # Adisyon özet tablosu
                    st.dataframe(active_sales[['item_name', 'price']], use_container_width=True, hide_index=True)
                    total_val = active_sales['price'].sum()
                    st.markdown(f"### 💰 Toplam: {total_val} TL")
                    
                    method = st.radio("Ödeme Tipi Seçin", ["Nakit", "Kredi Kartı"], horizontal=True)
                    if st.button("💵 Hesabı Tahsil Et ve Masayı Kapat", type="primary", use_container_width=True):
                        conn.execute(f"UPDATE sales SET method='{method}', date='{datetime.now().strftime('%Y-%m-%d')}' WHERE date='{t_name}'")
                        conn.execute(f"UPDATE tables SET status='Boş', opened_at=NULL, kitchen_status='Bekliyor' WHERE name='{t_name}'")
                        conn.commit()
                        st.success("Hesap başarıyla kapatıldı!")
                        st.rerun()
        else:
            st.info("İşlem yapmak için sol taraftaki restoran planından bir masaya tıklayın.")

# --- MUTFAK ---
elif sel_tab == "🍳 Mutfak":
    st.subheader("👨‍🍳 Pişirme Listesi")
    active_orders = pd.read_sql("SELECT * FROM sales WHERE method='Bekliyor'", conn)
    if active_orders.empty:
        st.success("Tüm siparişler hazır!")
    else:
        for masa in active_orders['date'].unique():
            with st.expander(f"🔔 {masa} Siparişleri", expanded=True):
                masa_items = active_orders[active_orders['date'] == masa]
                st.table(masa_items[['item_name', 'price']])
                if st.button(f"Masa {masa} Hazır!", key=f"k_{masa}"):
                    conn.execute(f"UPDATE tables SET kitchen_status='Hazır' WHERE name='{masa}'")
                    conn.commit()
                    st.rerun()

# --- REZERVASYON ---
elif sel_tab == "📅 Rezervasyon":
    st.subheader("📝 Yeni Rezervasyon Oluştur")
    c1, c2, c3 = st.columns(3)
    r_name = c1.text_input("Müşteri Adı")
    r_table = c2.selectbox("Masa Seç", get_tables()['name'])
    r_time = c3.text_input("Saat (Örn: 20:30)")
    if st.button("Rezervasyonu Kaydet"):
        conn.execute("INSERT OR REPLACE INTO reservations VALUES (?,?,?)", (r_table, r_name, r_time))
        conn.commit()
        st.success("Rezerve edildi!")

# --- RAPORLAR & ADMİN ---
elif sel_tab == "📈 Raporlar & Admin":
    st.subheader("📊 Patron Dashboard")
    sales_df = pd.read_sql("SELECT * FROM sales WHERE method != 'Bekliyor'", conn)
    
    if not sales_df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Toplam Hasılat", f"{sales_df['price'].sum()} TL")
        fig = px.pie(sales_df, values='price', names='item_name', title='Ürün Satış Dağılımı')
        st.plotly_chart(fig)
    
    st.divider()
    st.subheader("📦 Stok ve Menü Yönetimi")
    
    if st.session_state.menu_message:
        st.success(st.session_state.menu_message)
        st.session_state.menu_message = None
        
    st.dataframe(get_menu(), use_container_width=True)
    
    if st.checkbox("Ürün Ekle/Güncelle", value=True):
        with st.form("menu_form", clear_on_submit=True):
            st.markdown("##### ➕ Yeni Ürün Bilgileri")
            f_cat = st.selectbox("Kategori", ["Meze", "Rakı", "Denizden", "Tatlı"])
            f_name = st.text_input("Ürün Adı", placeholder="Örn: Kalamar Tava...")
            f_price = st.number_input("Fiyat (TL)", min_value=0.0, step=10.0, value=150.0)
            f_stock = st.number_input("Başlangıç Stok Miktarı", min_value=0, step=5, value=50)
            
            submit_btn = st.form_submit_button("Kaydet ve Listeye Ekle")
            
            if submit_btn:
                if f_name.strip() == "":
                    st.error("⚠️ Ürün adı boş bırakılamaz!")
                else:
                    conn.execute("INSERT OR REPLACE INTO menu VALUES (?,?,?,?)", (f_cat, f_name, f_price, f_stock))
                    conn.commit()
                    st.session_state.menu_message = f"✅ '{f_name}' ürünü başarıyla menüye eklendi ve stok güncellendi!"
                    st.rerun()
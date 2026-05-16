import streamlit as st
from datetime import datetime

# Sayfa ayarları
st.set_page_config(page_title="Yalı Balık POS Premium", page_icon="🌊", layout="wide")

# ==========================================
# GÜÇLÜ VE ZARİF CSS TASARIMI
# ==========================================
st.markdown("""
    <style>
    /* Genel Arkaplan Rengi (Soft Deniz Esintisi) */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Ana Başlıklar */
    .main-title { 
        font-size: 46px; 
        color: #0f172a; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .sub-title { 
        font-size: 18px; 
        color: #64748b; 
        text-align: center; 
        margin-bottom: 35px; 
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    /* Tüm Butonlar İçin Modern Kart Görünümü ve Animasyon */
    div.stButton > button {
        border-radius: 12px;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        background-color: #ffffff;
        color: #1e293b;
        font-weight: 600;
        padding: 10px 0;
    }
    
    /* Butonların Üzerine Gelince (Hover) Animasyonu */
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #3b82f6;
        color: #2563eb;
    }
    
    /* Birincil (Primary) Butonlar İçin Özel Tasarım (Ödeme vs.) */
    div.stButton > button[data-baseweb="button"]:has(div.st-emotion-cache-1n76uvr) {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
    }
    
    /* Sekme (Tab) Tasarımları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        background-color: #e2e8f0;
        border: none;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border-bottom: 3px solid #1e3a8a !important;
        font-weight: bold;
    }
    
    /* Metrik (Admin Rapor) Kartları */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border-left: 5px solid #1e3a8a;
    }
    
    /* Bölüm Çizgileri */
    hr {
        border-color: #e2e8f0;
    }
    </style>
    
    <div class="main-title">🌊 YALI BALIK RESTORANI</div>
    <div class="sub-title">PREMIUM ADİSYON & YÖNETİM SİSTEMİ</div>
""", unsafe_allow_html=True)

# 1. VERİTABANI TANIMLAMALARI (Session State)
if 'tables' not in st.session_state:
    masa_isimleri = ["Deniz 1", "Deniz 2", "Deniz 3", "Deniz 4", "Salon 1", "Salon 2", "Salon 3", "Salon 4", "Loca 1", "Loca 2", "VIP"]
    st.session_state.tables = {isim: {"status": "Boş", "orders": {}, "opened_at": None} for isim in masa_isimleri}

if 'selected_table' not in st.session_state: st.session_state.selected_table = None
if 'view_mode' not in st.session_state: st.session_state.view_mode = "masalar"

# 🦞 MENÜ VERİLERİ
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Soğuk Mezeler": {"Levrek Marin": 220, "Deniz Börülcesi": 140, "Fava": 130, "Lakerda": 280, "Atom": 150, "Kavun & Beyaz Peynir": 190},
        "Ara Sıcaklar": {"Kalamar Tava": 350, "Tereyağlı Karides": 380, "Ahtapot Izgara": 450, "Balık Pastırması": 290, "Sigara Böreği": 120},
        "Denizden (Ana Yemek)": {"Levrek Izgara": 450, "Çipura": 420, "Kalkan Tava": 850, "Somon Izgara": 520, "Lüfer": 750},
        "Salatalar": {"Roka Salatası": 160, "Gavurdağı": 180, "Yalı Özel Salata": 320},
        "Tatlılar": {"Fırında Tahin Helvası": 180, "Dondurmalı İrmik": 160, "Ayva Tatlısı": 150, "Meyve Tabağı": 200},
        "İçecekler & Alkol": {"70'lik Yeni Seri Rakı": 1450, "35'lik Rakı": 800, "Kadeh Şarap": 250, "Şalgam Suyu": 50, "Büyük Su": 40, "Türk Kahvesi": 60}
    }

if 'sales' not in st.session_state: st.session_state.sales = {"Nakit": 0, "Kredi Kartı": 0}

def get_elapsed_time(opened_at_str):
    if not opened_at_str: return ""
    opened_at = datetime.strptime(opened_at_str, "%Y-%m-%d %H:%M:%S")
    duration = datetime.now() - opened_at
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if days > 0: return f"⏱️ {days} gün {hours} sa {minutes} dk"
    elif hours > 0: return f"⏱️ {hours} sa {minutes} dk"
    else: return f"⏱️ {minutes} dk"

tab1, tab2 = st.tabs(["⚓ Salon ve Masalar", "⚙️ Yönetici Paneli"])

# ==========================================
# 1. SEKME: SALON VE MASA YÖNETİMİ
# ==========================================
with tab1:
    if st.session_state.view_mode == "masalar":
        col_left, col_right = st.columns([5, 3])
        
        with col_left:
            st.markdown("### 🗺️ Restoran Planı")
            grid_cols = st.columns(4)
            for i, (t_name, t_data) in enumerate(st.session_state.tables.items()):
                time_info = f"\n({get_elapsed_time(t_data['opened_at'])})" if t_data["opened_at"] else ""
                
                if t_data["status"] == "Boş": emoji, btn_label = "🟢", f"{emoji} {t_name}"
                elif t_data["status"] == "Açık" and len(t_data["orders"]) == 0: emoji, btn_label = "🟡", f"{emoji} {t_name} {time_info}"
                else: emoji, btn_label = "🔴", f"{emoji} {t_name} {time_info}"
                    
                if grid_cols[i % 4].button(btn_label, key=f"table_btn_{t_name}", use_container_width=True):
                    st.session_state.selected_table = t_name
            
        with col_right:
            st.markdown("### 🛠️ Masa İşlemleri")
            if st.session_state.selected_table:
                target_table = st.session_state.selected_table
                t_status = st.session_state.tables[target_table]["status"]
                t_opened = st.session_state.tables[target_table]["opened_at"]
                
                st.info(f"📍 **Seçili Bölüm:** {target_table}  \n📊 **Durum:** {t_status}")
                
                if t_opened:
                    st.write(f"📅 **Geliş Saati:** {t_opened.split()[1]}")
                    st.write(f"⏳ **Oturum Süresi:** {get_elapsed_time(t_opened)}")
                
                if t_status == "Boş":
                    if st.button("🔓 Masayı Aç (Müşteri Geldi)", type="primary", use_container_width=True):
                        st.session_state.tables[target_table]["status"] = "Açık"
                        st.session_state.tables[target_table]["opened_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.rerun()
                
                if t_status != "Boş":
                    if st.button("🍽️ Adisyona Git / Sipariş Al", use_container_width=True):
                        st.session_state.view_mode = "masa_detay"
                        st.rerun()
                        
                    st.divider()
                    st.markdown("#### 🔄 Masayı Taşı")
                    empty_tables = [name for name, data in st.session_state.tables.items() if data["status"] == "Boş"]
                    if empty_tables:
                        move_target = st.selectbox("Hedef Masayı Seçin", empty_tables, label_visibility="collapsed")
                        if st.button(f"{target_table} -> {move_target} Olarak Taşı", use_container_width=True):
                            st.session_state.tables[move_target]["orders"] = st.session_state.tables[target_table]["orders"]
                            st.session_state.tables[move_target]["opened_at"] = st.session_state.tables[target_table]["opened_at"]
                            st.session_state.tables[move_target]["status"] = st.session_state.tables[target_table]["status"]
                            st.session_state.tables[target_table]["orders"] = {}
                            st.session_state.tables[target_table]["opened_at"] = None
                            st.session_state.tables[target_table]["status"] = "Boş"
                            st.session_state.selected_table = move_target
                            st.success("Masa başarıyla taşındı!")
                            st.rerun()
            else:
                st.write("İşlem yapmak için sol taraftan bir masa seçiniz.")

    # GÖRÜNÜM 2: MASANIN İÇİ
    elif st.session_state.view_mode == "masa_detay":
        current_t = st.session_state.selected_table
        t_opened = st.session_state.tables[current_t]["opened_at"]
        
        if st.button("⬅️ Salon Planına Dön", type="secondary"):
            st.session_state.view_mode = "masalar"
            st.rerun()
            
        st.markdown(f"## 📋 {current_t} - Sipariş Ekranı")
        if t_opened: st.caption(f"⏱️ Müşteri {get_elapsed_time(t_opened)} önce giriş yaptı.")
        st.divider()
        
        detay_col1, detay_col2 = st.columns([5, 3])
        
        with detay_col1:
            st.markdown("### 🦀 Yalı Menüsü")
            categories = list(st.session_state.menu.keys())
            menu_tabs = st.tabs(categories)
            
            for index, cat_name in enumerate(categories):
                with menu_tabs[index]:
                    cat_items = st.session_state.menu[cat_name]
                    if not cat_items:
                        st.info("Bu kategoride henüz ürün yok.")
                    else:
                        cat_cols = st.columns(3)
                        for i, (item_name, item_price) in enumerate(cat_items.items()):
                            if cat_cols[i % 3].button(f"{item_name}\n{item_price} ₺", key=f"item_{cat_name}_{item_name}", use_container_width=True):
                                current_orders = st.session_state.tables[current_t]["orders"]
                                if item_name in current_orders: st.session_state.tables[current_t]["orders"][item_name]["quantity"] += 1
                                else: st.session_state.tables[current_t]["orders"][item_name] = {"price": item_price, "quantity": 1}
                                st.session_state.tables[current_t]["status"] = "Dolu"
                                st.rerun()
                            
        with detay_col2:
            st.markdown("### 🧾 Güncel Adisyon")
            order_dict = st.session_state.tables[current_t]["orders"]
            
            if len(order_dict) == 0:
                st.info("Bu masaya henüz sipariş girilmedi.")
            else:
                total = 0
                st.markdown("<div style='background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
                
                for item_name, details in order_dict.items():
                    item_total_price = details["price"] * details["quantity"]
                    total += item_total_price
                    st.markdown(f"**{details['quantity']}x {item_name}** <span style='float:right;'>{item_total_price} ₺</span>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 5px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)
                    
                st.markdown(f"<h3 style='text-align: right; color: #1e3a8a; margin-top: 15px;'>Toplam: {total} ₺</h3>", unsafe_allow_html=True)
                st.markdown("</div><br>", unsafe_allow_html=True)
                
                pay_col1, pay_col2 = st.columns(2)
                if pay_col1.button("💵 Nakit", use_container_width=True, type="primary"):
                    st.session_state.sales["Nakit"] += total
                    st.session_state.tables[current_t]["orders"] = {}
                    st.session_state.tables[current_t]["opened_at"] = None
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Nakit tahsil edildi!")
                    st.rerun()
                    
                if pay_col2.button("💳 Kredi Kartı", use_container_width=True, type="primary"):
                    st.session_state.sales["Kredi Kartı"] += total
                    st.session_state.tables[current_t]["orders"] = {}
                    st.session_state.tables[current_t]["opened_at"] = None
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Kart ile tahsil edildi!")
                    st.rerun()

# ==========================================
# 2. SEKME: ADMİN PANELİ 
# ==========================================
with tab2:
    st.markdown("## 👑 Yönetim & Raporlama Merkezi")
    
    admin_col1, admin_col2 = st.columns(2)
    with admin_col1:
        st.markdown("### 📊 Günlük Kasa Raporu")
        st.metric("💵 Nakit Hasılat", f"{st.session_state.sales['Nakit']} ₺")
        st.metric("💳 Kredi Kartı Hasılat", f"{st.session_state.sales['Kredi Kartı']} ₺")
        toplam = st.session_state.sales['Nakit'] + st.session_state.sales['Kredi Kartı']
        st.info(f"### 💎 Toplam Ciro: {toplam} ₺")
        
    with admin_col2:
        st.markdown("### ℹ️ Restoran Doluluk Durumu")
        dolu_masa = sum(1 for m in st.session_state.tables.values() if m['status'] != "Boş")
        toplam_masa = len(st.session_state.tables)
        st.metric("Aktif Doluluk", f"{dolu_masa} / {toplam_masa} Masa")
        st.progress(dolu_masa / toplam_masa if toplam_masa > 0 else 0)

    st.divider()

    st.markdown("### 🍔 Menü Yönetimi (Ürün Ekle / Sil)")
    menu_col1, menu_col2 = st.columns(2)
    
    with menu_col1:
        st.markdown("#### ✨ Yeni Ürün Ekle")
        kategoriler = list(st.session_state.menu.keys())
        secilen_kategori = st.selectbox("Eklenecek Kategori", kategoriler)
        yeni_urun_adi = st.text_input("Ürün Adı", placeholder="Örn: Karides Güveç")
        yeni_urun_fiyati = st.number_input("Satış Fiyatı (₺)", min_value=1, step=10, value=100)
        
        if st.button("➕ Menüye Ekle", type="primary"):
            if yeni_urun_adi.strip() == "": st.error("Lütfen geçerli bir ürün adı yazın!")
            elif yeni_urun_adi in st.session_state.menu[secilen_kategori]: st.warning(f"'{yeni_urun_adi}' zaten mevcut!")
            else:
                st.session_state.menu[secilen_kategori][yeni_urun_adi] = yeni_urun_fiyati
                st.success(f"✅ '{yeni_urun_adi}' başarıyla eklendi!")
                st.rerun()

    with menu_col2:
        st.markdown("#### 🗑️ Ürün Sil")
        silinecek_kategori = st.selectbox("Kategori Seçin", kategoriler, key="del_cat")
        mevcut_urunler = list(st.session_state.menu[silinecek_kategori].keys())
        
        if mevcut_urunler:
            silinecek_urun = st.selectbox("Silinecek Ürünü Seçin", mevcut_urunler)
            if st.button("❌ Ürünü Kalıcı Olarak Sil"):
                del st.session_state.menu[silinecek_kategori][silinecek_urun]
                st.success(f"'{silinecek_urun}' menüden kaldırıldı!")
                st.rerun()
        else:
            st.info("Bu kategoride silinecek ürün bulunmuyor.")
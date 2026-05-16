import streamlit as st
from datetime import datetime

# Sayfa ayarları (İkon ve Başlık Güncellendi)
st.set_page_config(page_title="Yalı Balık POS", page_icon="🌊", layout="wide")

# Özelleştirilmiş HTML/CSS ile modern başlık tasarımı
st.markdown("""
    <style>
    .main-title {
        font-size: 42px;
        color: #1E3A8A;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        color: #64748B;
        text-align: center;
        margin-bottom: 30px;
        font-style: italic;
    }
    </style>
    <div class="main-title">🌊 YALI BALIK RESTORANI</div>
    <div class="sub-title">Modern Adisyon ve Salon Yönetim Sistemi</div>
""", unsafe_allow_html=True)

# 1. VERİTABANI TANIMLAMALARI (Session State)
# Masaları konsepte uygun isimlendiriyoruz
if 'tables' not in st.session_state:
    masa_isimleri = [
        "Deniz 1", "Deniz 2", "Deniz 3", "Deniz 4", 
        "Salon 1", "Salon 2", "Salon 3", "Salon 4", 
        "Loca 1", "Loca 2", "VIP"
    ]
    st.session_state.tables = {
        isim: {"status": "Boş", "orders": [], "opened_at": None} for isim in masa_isimleri
    }

if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "masalar"

# 🦞 YALI BALIK ÖZEL MENÜSÜ
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Soğuk Mezeler": {"Levrek Marin": 220, "Deniz Börülcesi": 140, "Fava": 130, "Lakerda": 280, "Atom": 150, "Kavun & Beyaz Peynir": 190},
        "Ara Sıcaklar": {"Kalamar Tava": 350, "Tereyağlı Karides": 380, "Ahtapot Izgara": 450, "Balık Pastırması": 290, "Sigara Böreği": 120},
        "Denizden (Ana Yemek)": {"Levrek Izgara": 450, "Çipura": 420, "Kalkan Tava (Porsiyon)": 850, "Somon Izgara": 520, "Lüfer": 750},
        "Salatalar": {"Roka Salatası": 160, "Gavurdağı": 180, "Yalı Özel Deniz Mahsulleri Salata": 320},
        "Tatlılar": {"Fırında Tahin Helvası": 180, "Dondurmalı İrmik": 160, "Ayva Tatlısı": 150, "Meyve Tabağı": 200},
        "İçecekler & Alkol": {"70'lik Yeni Seri Rakı": 1450, "35'lik Rakı": 800, "Kadeh Şarap": 250, "Şalgam Suyu": 50, "Büyük Su": 40, "Türk Kahvesi": 60}
    }

if 'sales' not in st.session_state:
    st.session_state.sales = {"Nakit": 0, "Kredi Kartı": 0}

def get_elapsed_time(opened_at_str):
    if not opened_at_str:
        return ""
    opened_at = datetime.strptime(opened_at_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    duration = now - opened_at
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"⏱️ {days} gün {hours} sa {minutes} dk"
    elif hours > 0:
        return f"⏱️ {hours} sa {minutes} dk"
    else:
        return f"⏱️ {minutes} dk"

tab1, tab2 = st.tabs(["⚓ Salon ve Deniz Kenarı", "⚙️ Yönetici Paneli"])

# ==========================================
# 1. SEKME: SALON VE MASA YÖNETİMİ
# ==========================================
with tab1:
    if st.session_state.view_mode == "masalar":
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("🗺️ Restoran Planı")
            grid_cols = st.columns(4)
            for i, (t_name, t_data) in enumerate(st.session_state.tables.items()):
                time_info = ""
                if t_data["opened_at"]:
                    time_info = f"\n({get_elapsed_time(t_data['opened_at'])})"
                
                if t_data["status"] == "Boş":
                    emoji = "🟢"
                    btn_label = f"{emoji} {t_name}"
                elif t_data["status"] == "Açık" and len(t_data["orders"]) == 0:
                    emoji = "🟡"
                    btn_label = f"{emoji} {t_name} {time_info}"
                else:
                    emoji = "🔴"
                    btn_label = f"{emoji} {t_name} {time_info}"
                    
                if grid_cols[i % 4].button(btn_label, key=f"table_btn_{t_name}", use_container_width=True):
                    st.session_state.selected_table = t_name
            
        with col_right:
            st.subheader("🛠️ Masa İşlemleri")
            if st.session_state.selected_table:
                target_table = st.session_state.selected_table
                t_status = st.session_state.tables[target_table]["status"]
                t_opened = st.session_state.tables[target_table]["opened_at"]
                
                st.info(f"Seçili Bölüm: **{target_table}**\n\nDurum: {t_status}")
                
                if t_opened:
                    st.write(f"📅 **Müşteri Geliş Saati:** {t_opened.split()[1]}")
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
                    
                    st.write("🔄 Masayı Taşı")
                    empty_tables = [name for name, data in st.session_state.tables.items() if data["status"] == "Boş"]
                    if empty_tables:
                        move_target = st.selectbox("Taşınacak Hedef Masayı Seçin", empty_tables)
                        if st.button(f"{target_table} -> {move_target} Taşı", use_container_width=True):
                            st.session_state.tables[move_target]["orders"] = st.session_state.tables[target_table]["orders"]
                            st.session_state.tables[move_target]["opened_at"] = st.session_state.tables[target_table]["opened_at"]
                            st.session_state.tables[move_target]["status"] = st.session_state.tables[target_table]["status"]
                            
                            st.session_state.tables[target_table]["orders"] = []
                            st.session_state.tables[target_table]["opened_at"] = None
                            st.session_state.tables[target_table]["status"] = "Boş"
                            
                            st.session_state.selected_table = move_target
                            st.success("Masa taşıma işlemi başarılı!")
                            st.rerun()
                    else:
                        st.warning("Salonda boş masa bulunmuyor!")
            else:
                st.write("İşlem yapmak için sol taraftan bir masa seçiniz.")

    elif st.session_state.view_mode == "masa_detay":
        current_t = st.session_state.selected_table
        t_opened = st.session_state.tables[current_t]["opened_at"]
        
        if st.button("⬅️ Salon Planına Dön", type="secondary"):
            st.session_state.view_mode = "masalar"
            st.rerun()
            
        st.header(f"📋 {current_t} - Adisyon")
        if t_opened:
            st.caption(f"⏱️ Müşteri {get_elapsed_time(t_opened)} önce giriş yaptı.")
        st.divider()
        
        detay_col1, detay_col2 = st.columns([2, 1])
        
        with detay_col1:
            st.subheader("🦀 Yalı Menüsü")
            categories = list(st.session_state.menu.keys())
            menu_tabs = st.tabs(categories)
            
            for index, cat_name in enumerate(categories):
                with menu_tabs[index]:
                    cat_items = st.session_state.menu[cat_name]
                    cat_cols = st.columns(3)
                    
                    for i, (item_name, item_price) in enumerate(cat_items.items()):
                        if cat_cols[i % 3].button(f"{item_name}\n{item_price} ₺", key=f"item_{cat_name}_{item_name}", use_container_width=True):
                            st.session_state.tables[current_t]["orders"].append({"name": item_name, "price": item_price})
                            st.session_state.tables[current_t]["status"] = "Dolu"
                            st.rerun()
                            
        with detay_col2:
            st.subheader("🧾 Güncel Adisyon")
            order_list = st.session_state.tables[current_t]["orders"]
            total = sum(item['price'] for item in order_list)
            
            if len(order_list) == 0:
                st.info("Bu masaya henüz sipariş girilmedi.")
            else:
                for item in order_list:
                    st.write(f"- {item['name']} : **{item['price']} ₺**")
                    
                st.divider()
                st.markdown(f"### 💰 Toplam: {total} ₺")
                
                st.markdown("#### Ödeme Al")
                pay_col1, pay_col2 = st.columns(2)
                if pay_col1.button("💵 Nakit", use_container_width=True, type="primary"):
                    st.session_state.sales["Nakit"] += total
                    st.session_state.tables[current_t]["orders"] = []
                    st.session_state.tables[current_t]["opened_at"] = None
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Nakit tahsil edildi!")
                    st.rerun()
                    
                if pay_col2.button("💳 Kredi Kartı", use_container_width=True, type="primary"):
                    st.session_state.sales["Kredi Kartı"] += total
                    st.session_state.tables[current_t]["orders"] = []
                    st.session_state.tables[current_t]["opened_at"] = None
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Kart ile tahsil edildi!")
                    st.rerun()

# ==========================================
# 2. SEKME: ADMİN PANELİ (GÜNLÜK RAPOR)
# ==========================================
with tab2:
    st.header("👑 Yalı Balık Yönetim Paneli")
    admin_col1, admin_col2 = st.columns(2)
    
    with admin_col1:
        st.subheader("📊 Günlük Kasa Raporu")
        st.metric("Nakit Hasılat", f"{st.session_state.sales['Nakit']} ₺")
        st.metric("Kredi Kartı Hasılat", f"{st.session_state.sales['Kredi Kartı']} ₺")
        
        toplam = st.session_state.sales['Nakit'] + st.session_state.sales['Kredi Kartı']
        st.markdown(f"## 💎 Toplam Ciro: {toplam} ₺")
        
    with admin_col2:
        st.subheader("ℹ️ Restoran Durumu")
        dolu_masa = sum(1 for m in st.session_state.tables.values() if m['status'] != "Boş")
        toplam_masa = len(st.session_state.tables)
        st.metric("Aktif Doluluk", f"{dolu_masa} / {toplam_masa} Masa")
        st.progress(dolu_masa / toplam_masa if toplam_masa > 0 else 0)
        st.write("Tüm salon ve personel hareketleri anlık olarak kaydedilmektedir.")
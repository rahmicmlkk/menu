import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Modern POS Pro", layout="wide")

# 1. VERİTABANI TANIMLAMALARI (Session State)
# Masaları detaylı bir sözlük yapısında tutuyoruz
if 'tables' not in st.session_state:
    st.session_state.tables = {
        f"Masa {i}": {"status": "Boş", "orders": []} for i in range(1, 13)
    }

# Aktif üzerinde çalışılan masa ve ekran görünüm durumu
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "masalar"  # "masalar" veya "masa_detay"

# İstediğin Kategorilere Göre Güncellenmiş Menü
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Meze": {"Haydari": 70, "Şakşuka": 75, "Muhammara": 85, "Kavun & Peynir": 120},
        "Rakı": {"Duble Rakı": 190, "35'lik Rakı": 650, "70'lik Rakı": 1200},
        "Meşrubat": {"Kola": 45, "Fanta": 45, "Ayran": 30, "Şalgam Suyu": 35},
        "Sıcak İçecek": {"Çay": 20, "Türk Kahvesi": 45, "Nescafe": 40},
        "Ana Yemek": {"Izgara Köfte": 240, "Tavuk Şiş": 210, "Adana Kebap": 280, "Saç Tava": 320}
    }

# Günlük Kasa Raporu
if 'sales' not in st.session_state:
    st.session_state.sales = {"Nakit": 0, "Kredi Kartı": 0}

st.title("🥂 Gelişmiş Restoran POS Sistemi")

# Sekmeleri Oluşturma
tab1, tab2 = st.tabs(["🛒 Salon / Masalar", "⚙️ Admin Paneli"])

# ==========================================
# 1. SEKME: SALON VE MASA YÖNETİMİ
# ==========================================
with tab1:
    
    # GÖRÜNÜM 1: MASALARIN GENEL LİSTESİ
    if st.session_state.view_mode == "masalar":
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Salon Planı")
            # 4 sütunlu masa düzeni
            grid_cols = st.columns(4)
            for i, (t_name, t_data) in enumerate(st.session_state.tables.items()):
                # Duruma göre renk emojisi belirle
                if t_data["status"] == "Boş":
                    emoji = "🟢"  # Boş masa
                elif t_data["status"] == "Açık" and len(t_data["orders"]) == 0:
                    emoji = "🟡"  # Açılmış ama henüz sipariş girilmemiş
                else:
                    emoji = "🔴"  # Dolu / Siparişli masa
                    
                if grid_cols[i % 4].button(f"{emoji} {t_name}", key=f"table_btn_{t_name}", use_container_width=True):
                    st.session_state.selected_table = t_name
            
        with col_right:
            st.subheader("Masa İşlemleri")
            if st.session_state.selected_table:
                target_table = st.session_state.selected_table
                t_status = st.session_state.tables[target_table]["status"]
                t_orders = st.session_state.tables[target_table]["orders"]
                
                st.info(f"Seçili Masa: **{target_table}**\n\nDurum: {t_status}")
                
                # AKSİYON 1: MASAYI AÇ
                if t_status == "Boş":
                    if st.button("🔓 Masayı Aç", type="primary", use_container_width=True):
                        st.session_state.tables[target_table]["status"] = "Açık"
                        st.rerun()
                
                # MASA AÇIKSA VEYA DOLUYSA DİĞER ÖZELLİKLER GÖZÜKSÜN
                if t_status != "Boş":
                    # AKSİYON 2: MASANIN İÇİNE GİR
                    if st.button("📥 Masanın İçine Gir (Sipariş)", use_container_width=True):
                        st.session_state.view_mode = "masa_detay"
                        st.rerun()
                        
                    st.divider()
                    
                    # AKSİYON 3: MASAYI TAŞI
                    st.write("🔄 Masayı Taşı")
                    empty_tables = [name for name, data in st.session_state.tables.items() if data["status"] == "Boş"]
                    if empty_tables:
                        move_target = st.selectbox("Taşınacak Hedef Masayı Seçin", empty_tables)
                        if st.button(f"{target_table} -> {move_target} Taşı", use_container_width=True):
                            # Verileri hedef masaya aktar
                            st.session_state.tables[move_target]["orders"] = st.session_state.tables[target_table]["orders"]
                            st.session_state.tables[move_target]["status"] = "Dolu" if len(st.session_state.tables[target_table]["orders"]) > 0 else "Açık"
                            
                            # Eski masayı boşalt
                            st.session_state.tables[target_table]["orders"] = []
                            st.session_state.tables[target_table]["status"] = "Boş"
                            st.session_state.selected_table = move_target # odağı yeni masaya al
                            st.success("Masa başarıyla taşındı!")
                            st.rerun()
                    else:
                        st.warning("Taşınacak boş masa yok!")
            else:
                st.write("İşlem yapmak için sol taraftan bir masaya tıklayın.")

    # GÖRÜNÜM 2: MASANIN İÇİ (SİPARİŞ EKLEME VE KATEGORİLER)
    elif st.session_state.view_mode == "masa_detay":
        current_t = st.session_state.selected_table
        
        # Üst Bar / Geri Dönüş
        if st.button("⬅️ Masalara Geri Dön", type="secondary"):
            st.session_state.view_mode = "masalar"
            st.rerun()
            
        st.header(f"📋 {current_t} - Sipariş Ekranı")
        st.divider()
        
        detay_col1, detay_col2 = st.columns([2, 1])
        
        with detay_col1:
            st.subheader("Menü Kategorileri")
            
            # İstediğin kategorileri yan yana Sekme (Tab) olarak açıyoruz
            categories = list(st.session_state.menu.keys())
            menu_tabs = st.tabs(categories)
            
            # Her kategori sekmesinin içine ilgili ürünleri buton olarak diziyoruz
            for index, cat_name in enumerate(categories):
                with menu_tabs[index]:
                    cat_items = st.session_state.menu[cat_name]
                    cat_cols = st.columns(3)
                    
                    for i, (item_name, item_price) in enumerate(cat_items.items()):
                        if cat_cols[i % 3].button(f"{item_name}\n{item_price} TL", key=f"item_{cat_name}_{item_name}", use_container_width=True):
                            # Sipariş ekle
                            st.session_state.tables[current_t]["orders"].append({"name": item_name, "price": item_price})
                            # İlk sipariş girildiğinde durumu 'Dolu' yap
                            st.session_state.tables[current_t]["status"] = "Dolu"
                            st.rerun()
                            
        with detay_col2:
            st.subheader("🧾 Adisyon")
            order_list = st.session_state.tables[current_t]["orders"]
            total = sum(item['price'] for item in order_list)
            
            if len(order_list) == 0:
                st.info("Bu masada henüz sipariş yok. Soldaki menüden ekleme yapın.")
            else:
                # Siparişleri listele
                for item in order_list:
                    st.write(f"- {item['name']} : **{item['price']} TL**")
                    
                st.divider()
                st.markdown(f"### Toplam: {total} TL")
                
                # Hesap Kapatma Butonları
                pay_col1, pay_col2 = st.columns(2)
                if pay_col1.button("💵 Nakit Kapat", use_container_width=True, type="primary"):
                    st.session_state.sales["Nakit"] += total
                    st.session_state.tables[current_t]["orders"] = []
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Nakit olarak kapatıldı!")
                    st.rerun()
                    
                if pay_col2.button("💳 Kart Kapat", use_container_width=True, type="primary"):
                    st.session_state.sales["Kredi Kartı"] += total
                    st.session_state.tables[current_t]["orders"] = []
                    st.session_state.tables[current_t]["status"] = "Boş"
                    st.session_state.view_mode = "masalar"
                    st.success("Hesap Kart ile kapatıldı!")
                    st.rerun()

# ==========================================
# 2. SEKME: ADMİN PANELİ (GÜNLÜK RAPOR)
# ==========================================
with tab2:
    st.header("👑 Yönetici Paneli")
    
    admin_col1, admin_col2 = st.columns(2)
    
    with admin_col1:
        st.subheader("💰 Günlük Tarihli Ciro Başarısı")
        st.metric("Nakit Hasılat", f"{st.session_state.sales['Nakit']} TL")
        st.metric("Kredi Kartı Hasılat", f"{st.session_state.sales['Kredi Kartı']} TL")
        
        toplam = st.session_state.sales['Nakit'] + st.session_state.sales['Kredi Kartı']
        st.markdown(f"## Toplam Ciro: {toplam} TL")
        
    with admin_col2:
        st.subheader("ℹ️ Sistem Notları")
        st.write("Bu panelden ileride tarihe göre filtreleme özellikleri ve dinamik ürün ekleme modülleri yönetilecektir.")
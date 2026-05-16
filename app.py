import streamlit as st
from datetime import datetime

# Sayfa ayarları
st.set_page_config(page_title="Yalı Balık POS Ultimate", page_icon="🌊", layout="wide")

# ==========================================
# GÜÇLÜ VE ZARİF CSS TASARIMI (SİYAH KATEGORİLER)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .main-title { font-size: 42px; color: #0f172a; font-weight: 800; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #64748b; text-align: center; margin-bottom: 30px; font-weight: 400; }
    
    /* Buton Tasarımları */
    div.stButton > button { border-radius: 10px; transition: 0.3s; font-weight: bold; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    /* KATEGORİ (SEKME) İSİMLERİNİ SİYAH YAPMA */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        color: #000000 !important; /* Yazılar Siyah */
        font-weight: 600;
        background-color: #e2e8f0;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #000000 !important; /* Aktif Kategori Yazısı Siyah */
        border-bottom: 3px solid #000000 !important; /* Alt Çizgi Siyah */
        font-weight: 800 !important;
    }

    /* Adisyon Fişi Tasarımı */
    .receipt { background: #fff; padding: 20px; border: 1px dashed #333; width: 300px; font-family: monospace; color: #000; margin: auto; }
    .receipt-header { text-align: center; font-weight: bold; font-size: 18px; border-bottom: 1px dashed #333; padding-bottom: 10px; margin-bottom: 10px; }
    </style>
    <div class="main-title">🌊 YALI BALIK RESTORANI</div>
    <div class="sub-title">Premium POS & Mutfak Yönetimi</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. VERİTABANI VE DURUM YÖNETİMİ
# ==========================================
if 'tables' not in st.session_state:
    masa_isimleri = ["Deniz 1", "Deniz 2", "Deniz 3", "Deniz 4", "Salon 1", "Salon 2", "Salon 3", "Loca 1", "VIP"]
    st.session_state.tables = {
        isim: {"status": "Boş", "orders": {}, "opened_at": None, "kitchen_status": "Bekliyor"} 
        for isim in masa_isimleri
    }

if 'selected_table' not in st.session_state: st.session_state.selected_table = None
if 'view_mode' not in st.session_state: st.session_state.view_mode = "masalar"
if 'print_receipt' not in st.session_state: st.session_state.print_receipt = None

if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Soğuk Mezeler": {"Levrek Marin": 220, "Fava": 130, "Lakerda": 280, "Atom": 150},
        "Ara Sıcaklar": {"Kalamar Tava": 350, "Karides": 380, "Ahtapot Izgara": 450},
        "Ana Yemek": {"Levrek Izgara": 450, "Kalkan Tava": 850, "Somon": 520},
        "İçecekler": {"70'lik Rakı": 1450, "Şalgam": 50, "Su": 40}
    }

if 'sales' not in st.session_state: st.session_state.sales = {"Nakit": 0, "Kredi Kartı": 0, "İkram": 0}

def get_elapsed_time(opened_at_str):
    if not opened_at_str: return ""
    opened_at = datetime.strptime(opened_at_str, "%Y-%m-%d %H:%M:%S")
    mins = (datetime.now() - opened_at).seconds // 60
    return f"⏱️ {mins} dk"

# 3 Sekmeli Yapı
tab1, tab_mutfak, tab2 = st.tabs(["⚓ Salon (Garson)", "🍳 Mutfak (Aşçı)", "⚙️ Yönetim (Admin)"])

# ==========================================
# SEKME 1: SALON (GARSON & KASA)
# ==========================================
with tab1:
    if st.session_state.view_mode == "masalar":
        col_left, col_right = st.columns([5, 3])
        
        with col_left:
            st.markdown("### 🗺️ Restoran Planı")
            grid_cols = st.columns(3)
            for i, (t_name, t_data) in enumerate(st.session_state.tables.items()):
                time_info = f"\n({get_elapsed_time(t_data['opened_at'])})" if t_data["opened_at"] else ""
                
                k_status = ""
                if t_data["kitchen_status"] == "Mutfakta": k_status = " ⏳"
                elif t_data["kitchen_status"] == "Hazır": k_status = " ✅"
                
                # HATA ÇÖZÜMÜ: Atamalar ayrıldı
                if t_data["status"] == "Boş": 
                    emoji = "🟢"
                    btn_label = f"{emoji} {t_name}"
                elif t_data["status"] == "Açık" and len(t_data["orders"]) == 0: 
                    emoji = "🟡"
                    btn_label = f"{emoji} {t_name} {time_info}"
                else: 
                    emoji = "🔴"
                    btn_label = f"{emoji} {t_name} {k_status} {time_info}"
                    
                if grid_cols[i % 3].button(btn_label, key=f"tbl_{t_name}", use_container_width=True):
                    st.session_state.selected_table = t_name
                    st.session_state.print_receipt = None
            
        with col_right:
            st.markdown("### 🛠️ Masa İşlemleri")
            if st.session_state.selected_table:
                target_table = st.session_state.selected_table
                t_status = st.session_state.tables[target_table]["status"]
                k_status_text = st.session_state.tables[target_table]["kitchen_status"]
                
                st.info(f"📍 **{target_table}** | 🍽️ Durum: {t_status} | 👨‍🍳 Mutfak: {k_status_text}")
                
                if t_status == "Boş":
                    if st.button("🔓 Masayı Aç", type="primary", use_container_width=True):
                        st.session_state.tables[target_table]["status"] = "Açık"
                        st.session_state.tables[target_table]["opened_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.rerun()
                else:
                    if st.button("📝 Adisyona Git / Sipariş Al", use_container_width=True):
                        st.session_state.view_mode = "masa_detay"
                        st.rerun()
                        
                    if k_status_text == "Hazır":
                        if st.button("🍽️ Yemekleri Servis Ettim", use_container_width=True):
                            st.session_state.tables[target_table]["kitchen_status"] = "Bekliyor"
                            st.rerun()
            else:
                st.write("Sol taraftan masa seçin.")

    # ------------------------------------------
    # SİPARİŞ İÇİ (ADİSYON)
    # ------------------------------------------
    elif st.session_state.view_mode == "masa_detay":
        current_t = st.session_state.selected_table
        
        if st.button("⬅️ Salona Dön", type="secondary"):
            st.session_state.view_mode = "masalar"
            st.rerun()
            
        detay_col1, detay_col2 = st.columns([5, 4])
        
        with detay_col1:
            st.markdown("### 🦀 Menü")
            siparis_notu = st.text_input("📝 Sipariş Notu (Örn: Acısız, Az pişmiş)", placeholder="Notu yazıp ürüne tıklayın...")
            
            categories = list(st.session_state.menu.keys())
            menu_tabs = st.tabs(categories)
            
            for index, cat_name in enumerate(categories):
                with menu_tabs[index]:
                    cat_items = st.session_state.menu[cat_name]
                    cat_cols = st.columns(3)
                    for i, (item_name, item_price) in enumerate(cat_items.items()):
                        if cat_cols[i % 3].button(f"{item_name}\n{item_price} ₺", key=f"itm_{cat_name}_{item_name}", use_container_width=True):
                            final_item_name = f"{item_name} ({siparis_notu})" if siparis_notu.strip() else item_name
                            
                            current_orders = st.session_state.tables[current_t]["orders"]
                            if final_item_name in current_orders:
                                st.session_state.tables[current_t]["orders"][final_item_name]["quantity"] += 1
                            else:
                                st.session_state.tables[current_t]["orders"][final_item_name] = {"price": item_price, "quantity": 1}
                            
                            st.session_state.tables[current_t]["status"] = "Dolu"
                            st.session_state.tables[current_t]["kitchen_status"] = "Mutfakta" 
                            st.rerun()
                            
        with detay_col2:
            st.markdown("### 🧾 Adisyon")
            order_dict = st.session_state.tables[current_t]["orders"]
            
            if len(order_dict) == 0:
                st.info("Sipariş yok.")
            else:
                total = sum(d["price"] * d["quantity"] for d in order_dict.values())
                
                st.markdown("<div style='background: white; padding: 15px; border-radius: 10px; border: 1px solid #ccc;'>", unsafe_allow_html=True)
                for item_name, details in order_dict.items():
                    item_total = details["price"] * details["quantity"]
                    st.markdown(f"**{details['quantity']}x {item_name}** <span style='float:right;'>{item_total} ₺</span>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: right; color: black;'>Ara Toplam: {total} ₺</h3></div><br>", unsafe_allow_html=True)
                
                ikram_tutari = st.number_input("🎁 İndirim / İkram (₺)", min_value=0, max_value=total, step=10, value=0)
                odenecek_tutar = total - ikram_tutari
                if ikram_tutari > 0:
                    st.success(f"İndirimli Ödenecek Tutar: **{odenecek_tutar} ₺**")

                if st.button("🖨️ Adisyon Yazdır", use_container_width=True):
                    st.session_state.print_receipt = current_t
                
                if st.session_state.print_receipt == current_t:
                    receipt_html = f"""
                    <div class="receipt">
                        <div class="receipt-header">YALI BALIK<br><span style='font-size:12px; font-weight:normal;'>Tarih: {datetime.now().strftime("%d.%m.%Y %H:%M")}</span><br>Masa: {current_t}</div>
                    """
                    for n, d in order_dict.items():
                        receipt_html += f"<div style='display:flex; justify-content:space-between;'><span>{d['quantity']}x {n}</span><span>{d['price']*d['quantity']} ₺</span></div>"
                    receipt_html += f"<hr><div style='text-align:right; font-weight:bold;'>TOPLAM: {total} ₺</div>"
                    if ikram_tutari > 0: receipt_html += f"<div style='text-align:right;'>İndirim: -{ikram_tutari} ₺</div>"
                    receipt_html += f"<div style='text-align:right; font-size:18px; font-weight:bold; margin-top:5px;'>ÖDENECEK: {odenecek_tutar} ₺</div>"
                    receipt_html += "<div style='text-align:center; margin-top:15px; font-size:12px;'>Afiyet Olsun...</div></div>"
                    st.markdown(receipt_html, unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 💳 Tahsilat ve Kapatma")
                
                col_n, col_k = st.columns(2)
                if col_n.button("Nakit (Tamamı)", type="primary", use_container_width=True):
                    st.session_state.sales["Nakit"] += odenecek_tutar
                    st.session_state.sales["İkram"] += ikram_tutari
                    st.session_state.tables[current_t] = {"status": "Boş", "orders": {}, "opened_at": None, "kitchen_status": "Bekliyor"}
                    st.session_state.view_mode = "masalar"
                    st.rerun()
                if col_k.button("Kart (Tamamı)", type="primary", use_container_width=True):
                    st.session_state.sales["Kredi Kartı"] += odenecek_tutar
                    st.session_state.sales["İkram"] += ikram_tutari
                    st.session_state.tables[current_t] = {"status": "Boş", "orders": {}, "opened_at": None, "kitchen_status": "Bekliyor"}
                    st.session_state.view_mode = "masalar"
                    st.rerun()

                with st.expander("✂️ Parçalı Ödeme (Alman Usulü)"):
                    alinan_nakit = st.number_input("Alınan Nakit (₺)", min_value=0, max_value=odenecek_tutar, step=50, value=0)
                    kalan_kart = odenecek_tutar - alinan_nakit
                    st.write(f"Kalan Tutar (Karttan Çekilecek): **{kalan_kart} ₺**")
                    
                    if st.button("Parçalı Ödemeyi Tamamla", use_container_width=True):
                        st.session_state.sales["Nakit"] += alinan_nakit
                        st.session_state.sales["Kredi Kartı"] += kalan_kart
                        st.session_state.sales["İkram"] += ikram_tutari
                        st.session_state.tables[current_t] = {"status": "Boş", "orders": {}, "opened_at": None, "kitchen_status": "Bekliyor"}
                        st.session_state.view_mode = "masalar"
                        st.success("Parçalı ödeme alındı!")
                        st.rerun()

# ==========================================
# SEKME 2: MUTFAK PANELİ
# ==========================================
with tab_mutfak:
    st.markdown("## 👨‍🍳 Mutfak Sipariş Ekranı")
    st.info("Garsonların girdiği siparişler anında bu ekrana düşer. Hazırlanan siparişleri onaylayın.")
    
    bekleyen_masalar = [t for t, d in st.session_state.tables.items() if d["kitchen_status"] == "Mutfakta"]
    
    if not bekleyen_masalar:
        st.success("🎉 Şu an mutfakta bekleyen sipariş yok. Elinize sağlık!")
    else:
        m_cols = st.columns(3)
        for i, m_name in enumerate(bekleyen_masalar):
            with m_cols[i % 3]:
                st.markdown(f"""
                <div style='background-color:#fff3cd; border:2px solid #ffc107; padding:15px; border-radius:10px;'>
                    <h3 style='color:#856404; margin-top:0;'>🔔 {m_name}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for urun_adi, detay in st.session_state.tables[m_name]["orders"].items():
                    if "(" in urun_adi and ")" in urun_adi:
                        ana_urun, not_kismi = urun_adi.split("(", 1)
                        st.write(f"- **{detay['quantity']}x {ana_urun}** *(<span style='color:red;'>{not_kismi}</span>*", unsafe_allow_html=True)
                    else:
                        st.write(f"- **{detay['quantity']}x {urun_adi}**")
                
                if st.button(f"✅ {m_name} Hazır", key=f"mutfak_{m_name}", type="primary"):
                    st.session_state.tables[m_name]["kitchen_status"] = "Hazır"
                    st.rerun()

# ==========================================
# SEKME 3: YÖNETİM (ADMİN)
# ==========================================
with tab2:
    st.markdown("## 👑 Yönetim & Kasa Raporları")
    admin_col1, admin_col2, admin_col3 = st.columns(3)
    
    with admin_col1:
        st.metric("💵 Nakit Hasılat", f"{st.session_state.sales['Nakit']} ₺")
    with admin_col2:
        st.metric("💳 Kredi Kartı Hasılat", f"{st.session_state.sales['Kredi Kartı']} ₺")
    with admin_col3:
        st.metric("🎁 Yapılan İkram/İndirim", f"{st.session_state.sales['İkram']} ₺")
        
    toplam = st.session_state.sales['Nakit'] + st.session_state.sales['Kredi Kartı']
    st.info(f"### 💎 KASAYA GİREN TOPLAM CİRO: {toplam} ₺")
    
    st.divider()
    st.markdown("### 🍔 Menü Yönetimi (Hızlı Ürün Ekle)")
    kategoriler = list(st.session_state.menu.keys())
    c1, c2, c3 = st.columns([2, 2, 1])
    sec_kat = c1.selectbox("Kategori", kategoriler, label_visibility="collapsed")
    yeni_ad = c2.text_input("Ürün Adı", placeholder="Yeni Ürün Adı...", label_visibility="collapsed")
    yeni_fiyat = c3.number_input("Fiyat", min_value=1, value=100, label_visibility="collapsed")
    
    if st.button("➕ Ekle"):
        if yeni_ad:
            st.session_state.menu[sec_kat][yeni_ad] = yeni_fiyat
            st.success("Eklendi!")
            st.rerun()
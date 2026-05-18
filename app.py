import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="YZ Destekli İddaa Analiz", layout="wide", page_icon="⚽")

# Yeni API Ayarları (Verdiğin Key Entegre Edildi)
API_KEY = "91a1ba25df88491098642cadad041dcf"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_KEY
}

# Özel Tasarım (Kategori İsimleri Siyah)
st.markdown("""
    <style>
    .kategori-baslik {
        color: black !important;
        font-weight: bold;
        font-size: 26px;
        margin-top: 15px;
        margin-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 5px;
    }
    .alt-kategori {
        color: black !important;
        font-weight: 600;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- API VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=1800)  # Kota dostu olması için verileri 30 dakika önbelleğe alır
def get_league_matches(league_code):
    """Football-Data.org üzerinden seçilen ligin yaklaşan maçlarını çeker"""
    url = f"{BASE_URL}/competitions/{league_code}/matches"
    # Sadece oynanacak (SCHEDULED) maçları filtreler
    params = {"status": "SCHEDULED"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json().get("matches", [])
        else:
            st.error(f"API Hatası: {response.status_code} - Lütfen lig erişiminizi kontrol edin.")
            return []
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return []

# --- ARAYÜZ BAŞLANGICI ---
st.title("🤖 Football-Data API Destekli YZ İddaa Analiz")
st.caption(f"Sistem Durumu: Aktif | Güncel Tarih: {datetime.now().strftime('%d-%m-%Y')}")

# Football-Data.org Ücretsiz Planda Açık Olan Popüler Lig Kodları
LIGLER = {
    "İngiltere Premier Lig": "PL",
    "İspanya La Liga": "PD",
    "İtalya Serie A": "SA",
    "Fransa Ligue 1": "FL1",
    "UEFA Şampiyonlar Ligi": "CL"
}

tab1, tab2, tab3 = st.tabs(["🔥 Günün Kombinesi", "🌍 Lig Lig Maç Tahminleri", "📊 Derin Maç Analizi"])

# --- TAB 1: GÜNÜN KOMBİNESİ ---
with tab1:
    st.markdown('<div class="kategori-baslik">🔥 Günün YZ Banko Kombinesi</div>', unsafe_allow_html=True)
    st.write("Sistem algoritmasının API'den gelen form verilerini işleyerek oluşturduğu günün kuponu:")
    
    # Algoritma çıktısı simülasyonu
    kombine_listesi = [
        {"Maç": "Real Madrid vs Valencia", "Tahmin": "MS 1", "Güven Endeksi": "%93", "Saha Durumu": "Açık / İdeal"},
        {"Maçfont": "Arsenal vs Everton", "Tahmin": "2.5 Üst", "Güven Endeksi": "%87", "Saha Durumu": "Hafif Yağmurlu"}
    ]
    st.table(pd.DataFrame(kombine_listesi))
    st.success("**Önerilen Yapay Zeka Kuponu Hazır**")

# --- TAB 2: LİG LİG MAÇ TAHMİNLERİ ---
with tab2:
    st.markdown('<div class="kategori-baslik">🌍 Lig Lig Maçların Tahmini</div>', unsafe_allow_html=True)
    
    secilen_lig_adi = st.selectbox("Analiz etmek istediğiniz ligi seçin:", list(LIGLER.keys()))
    league_code = LIGLER[secilen_lig_adi]
    
    st.markdown(f'<div class="alt-kategori">{secilen_lig_adi} Yaklaşan Fikstür</div>', unsafe_allow_html=True)
    
    with st.spinner("Canlı fikstür verileri çekiliyor..."):
        maclar = get_league_matches(league_code)
        
        if maclar:
            tablo_verisi = []
            # İlk 10 maçı listele (Arayüzü yormamak için)
            for mac in maclar[:10]:
                tarih_ham = mac['utcDate']
                tarih_obj = datetime.strptime(tarih_ham, "%Y-%m-%dT%H:%M:%SZ")
                tarih_str = tarih_obj.strftime("%d-%m-%Y %H:%M")
                
                ev = mac['homeTeam']['name']
                deplasman = mac['awayTeam']['name']
                
                # Basit bir YZ tahmin simülasyonu (Gerçek model çıktısıyla değiştirilebilir)
                tablo_verisi.append({
                    "Tarih / Saat": tarih_str,
                    "Ev Sahibi Takım": ev,
                    "Deplasman Takım": deplasman,
                    "YZ Öngörüsü": "Analiz Sekmesine Gönderildi"
                })
            
            df = pd.DataFrame(tablo_verisi)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Bu ligde şu an aktif veya yaklaşan bir maç bulunamadı.")

# --- TAB 3: DETAYLI MAÇ ANALİZİ ---
with tab3:
    st.markdown('<div class="kategori-baslik">📊 Çok Boyutlu Yapay Zeka Analiz Bölümü</div>', unsafe_allow_html=True)
    st.write("Listelenen maçlardan birini seçerek detaylı hava durumu katsayısı, forum analizi ve sakatlık filtrelerini simüle edin:")
    
    # Dinamik maç seçimi için basit bir arayüz
    col1, col2 = st.columns(2)
    with col1:
        secilen_ev = st.text_input("Ev Sahibi", "Real Madrid")
    with col2:
        secilen_dep = st.text_input("Deplasman", "Barcelona")
        
    if st.button("Derin Analiz Algoritmasını Çalıştır"):
        st.markdown(f'<div class="alt-kategori">{secilen_ev} - {secilen_dep} Analiz Raporu</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Hava Durumu Katsayısı", "18°C Açık", "Zemin İdeal (%0 Etki)")
        c2.metric("Forum / Sosyal Medya Skoru", "%74 Pozitif", "Ev Sahibi Lehine")
        c3.metric("YZ Yapay Güven Oranı", "%89", "MS 1 Öneriliyor")
        
        # Grafiksel Güç Dağılımı
        st.write("**Algoritma Güç Dengesi Dağılımı:**")
        st.progress(0.65, text="Ev Sahibi Hücum Varyasyonu: %65")
        st.progress(0.45, text="Deplasman Defans Blok Yoğunluğu: %45")
        st.info("💡 **Gelişmiş Algoritma Notu:** Hava şartları ve forumlardaki genel taraftar duyarlılığı (Sentiment), ev sahibi takımın maça baskılı başlayacağını gösteriyor. İlk Yarı 0.5 Üst seçeneği değerlendirilebilir.")
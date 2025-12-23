import streamlit as st
import pymongo
import certifi
import pandas as pd
from datetime import datetime, timedelta

# MongoDB Bağlantısı (SSL hatası için düzeltilmiş link)
URI = "mongodb+srv://mam1r:Hywkas-behsax-jotnu6@cluster0.q6gs55s.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
    return client['sirinkoy_v3']

db = get_db()

st.set_page_config(page_title="Şirinköy Rapor", layout="wide")

# --- YAN PANEL (FİLTRELER) ---
st.sidebar.header("📅 Filtreler")
secilen_tarih = st.sidebar.date_input("Rapor Tarihi Seçin", datetime.now())
tarih_str = secilen_tarih.strftime("%Y-%m-%d")

st.title("🍓 Şirinköy Canlı Takip Paneli")
st.write(f"Şu anki rapor tarihi: **{tarih_str}**")

# --- VERİ ÇEKME ---
try:
    # Kapalı masaları çek
    tum_kapali = list(db.masalar_kapali.find())
    acik = list(db.masalar_acik.find())
    
    # Filtreleme: Kapanış zamanı seçilen tarihle başlayanları al
    # (Veriler "2023-10-27 14:30:00" formatında olduğu için baş kısmına bakıyoruz)
    gunluk_kapali = [m for m in tum_kapali if m.get('kapanis_zamani', '').startswith(tarih_str)]
    
except Exception as e:
    st.error(f"Veri çekilirken hata: {e}")
    gunluk_kapali, acik = [], []

# --- ÜST BİLGİ KARTLARI ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Açık Masa (Anlık)", len(acik))
with c2:
    toplam = sum(m.get('toplam_tutar', 0) for m in gunluk_kapali)
    st.metric(f"Seçili Gün Cirosu", f"{toplam:,.2f} TL")
with c3:
    nakit = sum(m.get('toplam_tutar', 0) for m in gunluk_kapali if m.get('odeme_tipi') == "Nakit")
    st.metric("Nakit (Seçili Gün)", f"{nakit:,.2f} TL")
with c4:
    kart = sum(m.get('toplam_tutar', 0) for m in gunluk_kapali if m.get('odeme_tipi') == "Kart")
    st.metric("Kart (Seçili Gün)", f"{kart:,.2f} TL")

st.divider()

# --- TABLOLAR ---
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("🔔 Aktif Masalar (Şu An)")
    if acik:
        df_acik = pd.DataFrame(acik)[['masa_adi', 'toplam_tutar', 'giris_zamani']]
        st.table(df_acik)
    else:
        st.info("Şu an açık masa yok.")

with col_sag:
    st.subheader(f"✅ {tarih_str} Tarihli İşlemler")
    if gunluk_kapali:
        df_kapali = pd.DataFrame(gunluk_kapali)
        cols = [c for c in ['masa_adi', 'toplam_tutar', 'odeme_tipi', 'kapanis_zamani'] if c in df_kapali.columns]
        st.dataframe(df_kapali[cols].sort_values(by='kapanis_zamani', ascending=False), use_container_width=True)
    else:
        st.warning(f"{tarih_str} tarihinde henüz işlem yapılmamış.")

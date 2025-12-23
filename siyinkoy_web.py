import streamlit as st
import pymongo
import certifi
import pandas as pd
from datetime import datetime, time

# MongoDB Bağlantısı
URI = "mongodb+srv://mam1r:Hywkas-behsax-jotnu6@cluster0.q6gs55s.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
    return client['sirinkoy_v3']

db = get_db()

st.set_page_config(page_title="Şirinköy Gelişmiş Rapor", layout="wide")

# --- YAN PANEL (TARİH ARALIĞI SEÇİMİ) ---
st.sidebar.header("📅 Rapor Aralığı")
baslangic_tarihi = st.sidebar.date_input("Başlangıç Tarihi", datetime.now())
bitis_tarihi = st.sidebar.date_input("Bitiş Tarihi", datetime.now())

# Tarihleri string formatına çeviriyoruz (Karşılaştırma için)
bas_str = baslangic_tarihi.strftime("%Y-%m-%d")
bit_str = bitis_tarihi.strftime("%Y-%m-%d")

st.title("🍓 Şirinköy Canlı Takip Paneli")
st.write(f"📊 Rapor Aralığı: **{bas_str}** ile **{bit_str}** arası")

# --- VERİ ÇEKME VE FİLTRELEME ---
try:
    tum_kapali = list(db.masalar_kapali.find())
    acik = list(db.masalar_acik.find())
    
    # Filtreleme Mantığı: Kapanış zamanı baş str ile bit str arasında olanları al
    aralik_kapali = []
    for m in tum_kapali:
        kapanis = m.get('kapanis_zamani', '')
        if kapanis:
            # Sadece tarih kısmını alıyoruz (YYYY-MM-DD)
            islem_tarihi = kapanis.split(" ")[0] 
            if bas_str <= islem_tarihi <= bit_str:
                aralik_kapali.append(m)
                
except Exception as e:
    st.error(f"Veri hatası: {e}")
    aralik_kapali, acik = [], []

# --- ÜST BİLGİ KARTLARI ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Aktif Masalar", len(acik))
with c2:
    toplam = sum(m.get('toplam_tutar', 0) for m in aralik_kapali)
    st.metric("Seçili Arallık Cirosu", f"{toplam:,.2f} TL")
with c3:
    nakit = sum(m.get('toplam_tutar', 0) for m in aralik_kapali if m.get('odeme_tipi') == "Nakit")
    st.metric("Toplam Nakit", f"{nakit:,.2f} TL")
with c4:
    kart = sum(m.get('toplam_tutar', 0) for m in aralik_kapali if m.get('odeme_tipi') == "Kart")
    st.metric("Toplam Kart", f"{kart:,.2f} TL")

st.divider()

# --- TABLOLAR ---
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("🔔 Şu An Açık Olan Masalar")
    if acik:
        df_acik = pd.DataFrame(acik)[['masa_adi', 'toplam_tutar', 'giris_zamani']]
        st.table(df_acik)
    else:
        st.info("Açık masa bulunmuyor.")

with col_sag:
    st.subheader(f"✅ Aralıktaki Tüm İşlemler ({len(aralik_kapali)} Adet)")
    if aralik_kapali:
        df_kapali = pd.DataFrame(aralik_kapali)
        cols = [c for c in ['masa_adi', 'toplam_tutar', 'odeme_tipi', 'kapanis_zamani'] if c in df_kapali.columns]
        st.dataframe(df_kapali[cols].sort_values(by='kapanis_zamani', ascending=False), use_container_width=True)
    else:
        st.warning("Bu tarih aralığında işlem bulunamadı.")

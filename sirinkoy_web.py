# sirinkoy-takipimport streamlit as st
import pymongo
import certifi
import pandas as pd
from datetime import datetime

# MongoDB Bağlantısı (Dükkanla aynı adres)
URI = "mongodb+srv://mam1r:Hywkas-behsax-jotnu6@cluster0.q6gs55s.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(URI, tlsCAFile=certifi.where())
db = client['sirinkoy_v3']

st.set_page_config(page_title="Şirinköy Canlı Takip", layout="wide")

st.title("🍓 Şirinköy Canlı Takip Paneli")
st.write(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")

# Verileri Çek
kapali = list(db.masalar_kapali.find())
acik = list(db.masalar_acik.find())

# Üst Bilgi Kartları
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Açık Masa", len(acik))
with c2:
    toplam = sum(m.get('toplam_tutar', 0) for m in kapali)
    st.metric("Toplam Ciro", f"{toplam:,.2f} TL")
with c3:
    nakit = sum(m.get('toplam_tutar', 0) for m in kapali if m.get('odeme_tipi') == "Nakit")
    st.metric("Nakit", f"{nakit:,.2f} TL")
with c4:
    kart = sum(m.get('toplam_tutar', 0) for m in kapali if m.get('odeme_tipi') == "Kart")
    st.metric("Kart", f"{kart:,.2f} TL")

st.divider()

# Tablolar
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("🔔 Aktif Masalar")
    if acik:
        df_acik = pd.DataFrame(acik)[['masa_adi', 'toplam_tutar', 'giris_zamani']]
        st.table(df_acik)
    else:
        st.info("Şu an açık masa yok.")

with col_sag:
    st.subheader("✅ Son Kapanan 10 İşlem")
    if kapali:
        df_kapali = pd.DataFrame(kapali)[['masa_adi', 'toplam_tutar', 'odeme_tipi', 'kapanis_zamani']]
        st.dataframe(df_kapali.tail(10), use_container_width=True)

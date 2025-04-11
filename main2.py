import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests

# ---------- Einstellungen ----------
# ML-Modell laden
model = joblib.load("wave_height_model.pkl")

# Beispiel-Surfspots mit Koordinaten (müsst ihr ggf. anpassen)
surfspots = {
    "Carcavelos": "38.6766,-9.3241",
    "Guincho": "38.7324,-9.4723",
    "Costa da Caparica": "38.6453,-9.2485"
}

# WorldWeatherOnline API-Key (ersetzt durch euren eigenen!)
API_KEY = "DEIN_API_KEY_HIER"
BASE_URL = "https://api.worldweatheronline.com/premium/v1/marine.ashx"

# ---------- App UI ----------
st.title("🏄‍♂️ Surfspot Forecast App")
st.markdown("Erhalte Surf-Empfehlungen für drei Spots in Lissabon basierend auf deinen eingegebenen Bedingungen.")

# User Inputs
st.sidebar.header("📥 Surfbedingungen eingeben")
wind_speed = st.sidebar.slider("Windgeschwindigkeit (km/h)", 0, 40, 10)
wind_dir = st.sidebar.slider("Windrichtung (Grad)", 0, 360, 180)
swell_dir = st.sidebar.slider("Swell-Richtung (Grad)", 0, 360, 210)
swell_period = st.sidebar.slider("Swell-Periode (s)", 5, 20, 12)
tide = st.sidebar.slider("Tide (Meter)", -1.0, 2.0, 0.5)

# Feature-Vektor zusammenstellen
def make_features(wind_speed, wind_dir, swell_dir, swell_period, tide):
    return np.array([[wind_speed, wind_dir, swell_dir, swell_period, tide]])

# Vorhersage + Bewertung
def interpret_prediction(height):
    if height >= 1.2:
        return "🌊 Gute Surfbedingungen"
    elif height >= 0.7:
        return "😐 Mittelmäßig"
    else:
        return "🌪️ Schlechte Bedingungen"

st.subheader("🔮 Prognosen für die Surfspots")
for name, coords in surfspots.items():
    st.markdown(f"### 📍 {name}")
    
    # (Optional) Holt Echtzeitdaten – aktuell nutzen wir Nutzereingabe
    # params = {"q": coords, "format": "json", "key": API_KEY}
    # response = requests.get(BASE_URL, params=params).json()

    # Features aus Nutzereingabe
    features = make_features(wind_speed, wind_dir, swell_dir, swell_period, tide)
    prediction = model.predict(features)[0]

    # Ausgabe
    st.write(f"**Vorhergesagte Wellenhöhe:** {round(prediction, 2)} m")
    st.success(interpret_prediction(prediction))

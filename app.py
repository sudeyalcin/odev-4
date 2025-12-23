from __future__ import annotations
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

from src.maps import geocode_locations, distance_matrix_meters
from src.aco import ACOParams, solve_tsp_aco

st.set_page_config(page_title="Senaryo4 - ACO Yol Optimizasyonu (Muratpaşa)", layout="wide")

st.title("🚚 Karınca Kolonisi Algoritması ile Kargo Rota Optimizasyonu")
st.subheader("Antalya Muratpaşa - 20 Mağazaya En Kısa Teslimat Rotası")
st.caption("🆓 %100 ÜCRETSİZ • OpenStreetMap + Nominatim geocoding • OSRM routing • İnteraktif harita görselleştirmesi")

st.success("✅ **Google Maps API'den tamamen kurtulduk!** Artık %100 ücretsiz sistem kullanıyoruz:")
st.info("""
🔹 **Geocoding**: Nominatim (OpenStreetMap) - Ücretsiz  
🔹 **Routing**: OSRM (Open Source Routing Machine) - Ücretsiz  
🔹 **Haritalar**: Folium + OpenStreetMap - Ücretsiz  
🔹 **API Key**: Gerekmiyor! 🎉
""")

# --- Load locations ---
@st.cache_data
def load_locations():
    with open("data/locations.json", "r", encoding="utf-8") as f:
        return json.load(f)

locations = load_locations()

st.subheader("📍 Teslimat Lokasyonları")
df_loc = pd.DataFrame(locations)
st.dataframe(df_loc, use_container_width=True, hide_index=True)

with st.expander("ℹ️ Lokasyonlar Hakkında Bilgi"):
    st.markdown("""
    **Senaryo 4:** Antalya/Muratpaşa ilçesinde faaliyet gösteren kargo firması
    
    - 📦 **Toplam teslimat noktası:** 20 mağaza
    - 🏢 **Başlangıç noktası:** Kargo Firması Merkezi (Çağlayan Mahallesi)
    - 🎯 **Amaç:** En kısa toplam mesafeyle tüm mağazalara uğrayıp başlangıca dönmek
    - 🗺️ **Mesafe hesabı:** OSRM ile gerçek sürüş mesafeleri (ÜCRETSIZ!)
    
    **Lokasyon türleri:**
    - 🏬 Alışveriş merkezleri (TerraCity, MarkAntalya)
    - 💻 Teknoloji mağazaları (Teknosa, Vatan, MediaMarkt)
    - 🛒 Market zincirleri (Migros, BİM, ŞOK, A101)
    - 👕 Giyim mağazaları (LC Waikiki, Mavi, Koton)
    - 💄 Kozmetik mağazaları (Watsons, Gratis)
    """)

# --- Parameters ---
st.subheader("🔧 ACO Algoritması Parametreleri")

with st.expander("ℹ️ Parametre Açıklamaları"):
    st.markdown("""
    - **α (Alpha)**: Feromon etkisi - Karıncaların önceki deneyimlerini ne kadar dikkate aldığı
    - **β (Beta)**: Heuristik bilgi etkisi - Mesafe bilgisinin ne kadar önemli olduğu
    - **ρ (Rho)**: Buharlaşma oranı - Feromon izlerinin ne kadar hızla kaybolduğu
    - **Q**: Feromon miktarı sabiti - Bırakılan feromon miktarı
    - **Karınca sayısı**: Her iterasyonda çözüm arayan karınca sayısı
    - **İterasyon sayısı**: Algoritmanın kaç kez tekrarlanacağı
    """)

c1, c2, c3, c4, c5 = st.columns(5)
ants = c1.number_input("Karınca sayısı", min_value=5, max_value=200, value=40, step=5)
iters = c2.number_input("İterasyon sayısı", min_value=10, max_value=2000, value=150, step=10)
alpha = c3.slider("α (feromon)", 0.1, 5.0, 1.0, 0.1)
beta = c4.slider("β (heuristik)", 0.1, 8.0, 3.0, 0.1)
rho = c5.slider("ρ (buharlaşma)", 0.01, 0.99, 0.35, 0.01)

c6, c7 = st.columns(2)
q = c6.number_input("Q (feromon miktarı)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0)
seed = c7.number_input("Random seed", min_value=0, max_value=10_000, value=42, step=1)

run = st.button("🚀 ACO Algoritmasını Çalıştır", type="primary", use_container_width=True)

@st.cache_data(show_spinner=True)
def compute_coords_and_dist(locations_obj):
    coords = geocode_locations(locations_obj)
    dist = distance_matrix_meters(coords)
    return coords, dist

if run:
    with st.spinner("📍 Koordinatlar alınıyor (Nominatim) ve mesafe matrisi hesaplanıyor (OSRM)..."):
        coords, dist = compute_coords_and_dist(locations)

    params = ACOParams(
        ants=int(ants),
        iterations=int(iters),
        alpha=float(alpha),
        beta=float(beta),
        rho=float(rho),
        q=float(q),
        seed=int(seed),
    )

    with st.spinner("🐜 ACO algoritması çalışıyor..."):
        best_route, best_len_m, history = solve_tsp_aco(dist, params, start=0)

    st.success(f"✅ En iyi rota bulundu! Toplam mesafe: **{best_len_m/1000:.2f} km**")

    # Results in columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Route table
        ordered = [locations[i]["name"] for i in best_route] + [locations[best_route[0]]["name"]]
        st.subheader("🛣️ Optimum Rota Sırası")
        route_df = pd.DataFrame({
            "Sıra": list(range(1, len(ordered)+1)), 
            "Durak": ordered,
            "Durum": ["🏢 Başlangıç"] + ["📦 Teslimat"]*(len(ordered)-2) + ["🔄 Dönüş"]
        })
        st.dataframe(route_df, use_container_width=True, hide_index=True)
        
        # Statistics
        st.subheader("📊 İstatistikler")
        st.metric("Toplam Mesafe", f"{best_len_m/1000:.2f} km")
        st.metric("Ortalama Durak Arası", f"{best_len_m/len(locations)/1000:.2f} km")
        st.metric("Toplam Durak Sayısı", len(locations))

    with col2:
        # Plot history
        st.subheader("📈 Algoritma Performansı")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(np.array(history)/1000.0, linewidth=2, color='#1f77b4')
        ax.set_xlabel("İterasyon Sayısı")
        ax.set_ylabel("En İyi Mesafe (km)")
        ax.set_title("ACO Algoritması - İterasyon Bazında İyileşme")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig, clear_figure=True)
        
        # Performance metrics
        improvement = ((history[0] - history[-1])/history[0]*100)
        st.metric("Başlangıç Mesafesi", f"{history[0]/1000:.2f} km")
        st.metric("Final Mesafesi", f"{history[-1]/1000:.2f} km")
        st.metric("İyileşme Oranı", f"{improvement:.1f}%")

    # Map
    st.subheader("🗺️ Harita Üzerinde Optimum Rota")
    
    # Center map on first point
    start_lat, start_lng = coords[0]
    m = folium.Map(location=[start_lat, start_lng], zoom_start=12)

    # Add markers with custom icons
    for idx, (lat, lng) in enumerate(coords):
        if idx == 0:
            # Starting point - different color
            folium.Marker(
                [lat, lng], 
                popup=f"🏢 BAŞLANGIÇ: {locations[idx]['name']}", 
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
        else:
            folium.Marker(
                [lat, lng], 
                popup=f"📦 {idx}: {locations[idx]['name']}", 
                icon=folium.Icon(color='blue', icon='shopping-cart')
            ).add_to(m)

    # Add route polyline
    path = [coords[i] for i in best_route] + [coords[best_route[0]]]
    folium.PolyLine(
        path, 
        weight=4, 
        opacity=0.8, 
        color='red',
        popup=f"Optimum Rota - {best_len_m/1000:.2f} km"
    ).add_to(m)

    # Add route numbers
    for i, route_idx in enumerate(best_route[1:], 1):
        lat, lng = coords[route_idx]
        folium.CircleMarker(
            [lat, lng],
            radius=15,
            popup=f"Sıra: {i+1}",
            color='white',
            fillColor='red',
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
        
        folium.map.Marker(
            [lat, lng],
            icon=folium.DivIcon(
                html=f"<div style='font-size: 12px; color: white; font-weight: bold; text-align: center; margin-top: -6px;'>{i+1}</div>",
                icon_size=(20, 20),
                icon_anchor=(10, 10)
            )
        ).add_to(m)

    st_folium(m, width=1200, height=600)

st.markdown("---")
st.success("🎉 **Artık tamamen ücretsiz!** Google Maps API'ye veda ettik. OpenStreetMap ve OSRM sayesinde hiçbir ücret ödemeden rota optimizasyonu yapabiliyorsunuz!")
st.caption("ℹ️ **Not:** Nominatim ve OSRM ücretsiz servisleri kullanıyoruz. Yoğun kullanımda rate limiting olabilir, bu durumda birkaç saniye bekleyip tekrar deneyin.")
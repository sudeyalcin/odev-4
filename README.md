# 🎉 Karınca Kolonisi Algoritması ile Yol Optimizasyonu 
## Antalya Muratpaşa Kargo Firması Rota Optimizasyonu

**Ders:** BLG-307 Yapay Zeka Sistemleri — 2. Proje (2025-26 Güz)  
**Senaryo 4:** Antalya/Muratpaşa ilçesinde faaliyet gösteren bir kargo firmasının **20 farklı mağazaya** günlük teslimat yapması için **en kısa rotanın** bulunması.


### 🆓 Kullanılan Ücretsiz Teknolojiler:
- **Nominatim (OpenStreetMap)**: Adres → Koordinat dönüşümü
- **OSRM (Open Source Routing Machine)**: Gerçek sürüş mesafeleri
- **Folium + OpenStreetMap**: Harita görselleştirme
- **Karınca Kolonisi Algoritması**: TSP optimizasyonu
- **Streamlit**: Web arayüzü

## 🎯 Proje Amacı

Bu proje, gerçek hayat senaryosunda Karınca Kolonisi Algoritması (ACO) kullanarak Traveling Salesman Problem (TSP) çözümü sunmaktadır. Kargo firması her gün merkez noktasından çıkış yaparak 20 farklı mağazaya uğrayıp tekrar başlangıç noktasına dönmek zorundadır.

## 🚀 Özellikler

- **Ücretsiz Geocoding**: Nominatim ile gerçek adreslerden koordinat alma
- **Ücretsiz Routing**: OSRM ile gerçek sürüş mesafesi hesaplama
- **Karınca Kolonisi Algoritması**: TSP için optimize edilmiş ACO implementasyonu
- **İnteraktif Streamlit Arayüzü**: Kullanıcı dostu web arayüzü
- **Gerçek Zamanlı Görselleştirme**: 
  - İterasyon bazında mesafe grafiği
  - Harita üzerinde optimum rota çizimi
  - Detaylı rota tablosu
- **Parametre Ayarlama**: α, β, buharlaşma oranı, karınca sayısı vb.

## 📋 Gereksinimler

```bash
pip install -r requirements.txt
```

### Gerekli Kütüphaneler:
- `streamlit>=1.31` - Web arayüzü
- `numpy>=1.24` - Sayısal hesaplamalar
- `pandas>=2.0` - Veri işleme
- `matplotlib>=3.7` - Grafik çizimi
- `folium>=0.15` - Harita görselleştirme
- `streamlit-folium>=0.20` - Streamlit-Folium entegrasyonu
- `requests>=2.31.0` - HTTP istekleri
- `geopy>=2.4.0` - Geocoding (Nominatim)
- `osmnx>=1.8.0` - OpenStreetMap araçları





## 📁 Proje Yapısı

```
aco_yol_optimizasyonu/
├── app.py                      # Ana Streamlit uygulaması (ÜCRETSİZ!)
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Proje dokümantasyonu
├── .gitignore                  # Git ignore dosyası
├── data/
│   └── locations.json          # 20 mağaza lokasyonu
├── src/
│   ├── aco.py                  # ACO algoritması
│   ├── maps.py                 # Ücretsiz geocoding & routing
│   └── utils.py                # Yardımcı fonksiyonlar
└── notebooks/
    ├── aco_demo.ipynb          # Eski notebook (Google Maps)
    └── aco_demo_free.ipynb     # Yeni notebook (ÜCRETSİZ!)
```

## 🧮 Algoritma Detayları

### Karınca Kolonisi Algoritması (ACO)
- **Feromon Matrisi**: Karıncaların bıraktığı iz bilgisi
- **Heuristik Bilgi**: 1/mesafe (yakın mesafeler tercih edilir)
- **Olasılık Hesabı**: τ^α × η^β formülü
- **Feromon Güncellemesi**: Buharlaşma + en iyi rotadan feromon bırakma

### Parametreler:
- **α (alpha)**: Feromon etkisi (1.0)
- **β (beta)**: Heuristik bilgi etkisi (3.0)
- **ρ (rho)**: Buharlaşma oranı (0.35)
- **Q**: Feromon miktarı sabiti (100.0)
- **Karınca sayısı**: 40
- **İterasyon sayısı**: 150

## 🆓 Ücretsiz Servisler Detayları

### 1. Nominatim (Geocoding)
- OpenStreetMap tabanlı ücretsiz geocoding servisi
- Adres → Koordinat dönüşümü
- Rate limiting: 1 saniye bekleme (otomatik)

### 2. OSRM (Routing)
- Açık kaynak routing engine
- Gerçek sürüş mesafeleri ve süreleri
- Public server: `router.project-osrm.org`
- Fallback: Haversine mesafesi

### 3. Folium + OpenStreetMap
- Ücretsiz harita görselleştirme
- İnteraktif haritalar
- Marker ve rota çizimi

## 📊 Sonuçlar

Uygulama şu çıktıları sağlar:
1. **Optimum Rota**: Sıralı mağaza listesi
2. **Toplam Mesafe**: Kilometre cinsinden
3. **Mesafe Grafiği**: İterasyonlara göre iyileşme
4. **Harita Görselleştirmesi**: Folium ile interaktif harita




## 📝 Lisans

Bu proje eğitim amaçlı hazırlanmıştır.


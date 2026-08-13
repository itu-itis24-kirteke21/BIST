# BIST 100 Profesyonel Hisse Analiz Sistemi

## 📊 Özellikler

- **Gerçek Veriler**: Yahoo Finance API üzerinden canlı BIST verileri
- **Teknik Analiz**: RSI(14), MACD(12,26,9), EMA 20/50, Bollinger Bands(20,2), Hacim analizi
- **Temel Analiz**: F/K, PD/DD, Beta, ROE, Kâr Marjı, Borç/Özsermaye, Analist tavsiyeleri
- **Skorlama Motoru**: Teknik 50 puan + Temel 50 puan = Toplam 100 puan
- **İnteraktif Dashboard**: HTML tabanlı, tıklanabilir detaylı analiz kartları
- **Filtreleme & Arama**: Hisse kodu, sentiment, skor sıralaması

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Kurun
```bash
pip install -r requirements.txt
```

### 2. Analizi Çalıştırın
```bash
python bist_analyzer.py
```
Bu komut:
- Tüm BIST 100 hisselerini Yahoo Finance'den çeker
- Teknik ve temel göstergeleri hesaplar
- Skorlama yapar
- Sonuçları `bist_analysis_results.json` olarak kaydeder

### 3. Dashboard'u Görüntüleyin
```bash
# Windows
cd bist_analyzer_package
start bist_dashboard.html

# Mac
open bist_dashboard.html

# Linux
xdg-open bist_dashboard.html
```

VEYA `bist_dashboard.html` dosyasını doğrudan tarayıcıda açın.

> **Not**: Dashboard, aynı klasördeki `bist_analysis_results.json` dosyasını otomatik yükler.

## ⚙️ Yapılandırma

### Sadece Belirli Hisseleri Analiz Etme
`bist_analyzer.py` dosyasının en altındaki bölümü değiştirin:

```python
# Tüm listeyi analiz et
results = run_analysis()

# VEYA sadece belirli hisseleri analiz et:
selected = {k: v for k, v in BIST100_STOCKS.items() if v['code'] in ['THYAO', 'GARAN', 'ASELS']}
results = run_analysis(selected)
```

### Yeni Hisse Ekleme
`BIST100_STOCKS` sözlüğüne ekleme yapın:

```python
BIST100_STOCKS = {
    'THYAO.IS': {'code': 'THYAO', 'name': 'Türk Hava Yolları', 'sector': 'Havacılık'},
    'GARAN.IS': {'code': 'GARAN', 'name': 'Garanti BBVA', 'sector': 'Bankacılık'},
    # ... mevcut hisseler ...
    'YENI.IS': {'code': 'YENI', 'name': 'Yeni Şirket', 'sector': 'Teknoloji'},
}
```

> **Önemli**: Yahoo Finance ticker formatı `KOD.IS` şeklindedir.

### Skorlama Algoritmasını Değiştirme

`calculate_technical_score()` ve `calculate_fundamental_score()` fonksiyonlarını düzenleyerek kendi skorlama kriterlerinizi belirleyebilirsiniz.

## 📁 Dosya Yapısı

```
bist_analyzer_package/
├── bist_analyzer.py          # Ana Python analiz scripti
├── bist_dashboard.html       # İnteraktif HTML dashboard
├── requirements.txt          # Python bağımlılıkları
├── README.md                 # Bu dosya
└── bist_analysis_results.json # Otomatik oluşturulan sonuçlar
```

## 🔄 Günlük Otomatik Çalıştırma (Cron Job)

### Linux/Mac
```bash
crontab -e
# Her gün saat 18:30'da çalıştır:
30 18 * * * cd /path/to/bist_analyzer_package && /usr/bin/python3 bist_analyzer.py >> log.txt 2>&1
```

### Windows (Görev Zamanlayıcı)
1. Görev Zamanlayıcı'yı açın
2. "Temel görev oluştur" seçeneğini seçin
3. Günlük tekrar ayarlayın
4. Program olarak `python.exe` seçin
5. Argüman olarak `bist_analyzer.py` ekleyin

## 📊 Skorlama Sistemi

| Kategori | Gösterge | Maks Puan |
|----------|----------|-----------|
| **Teknik** | RSI Momentum | 12 |
| | MACD Sinyali | 12 |
| | EMA Trend | 10 |
| | Hacim Analizi | 8 |
| | Bollinger Pozisyonu | 8 |
| **Temel** | F/K Oranı (Değerleme) | 10 |
| | PD/DD (Defter Değeri) | 8 |
| | Beta (Risk) | 6 |
| | Kâr Marjı | 8 |
| | ROE (Özsermaye Kârlılığı) | 8 |
| | Borç/Özsermaye | 6 |
| | Analist Tavsiyesi | 4 |

**Toplam**: 100 puan

### Sentiment Sınıflandırması
- 🟢 **Olumlu**: 50+ puan
- ⚪ **Nötr**: 35-49 puan
- 🔴 **Olumsuz**: <35 puan

## ⚠️ Sınırlamalar

- Yahoo Finance ücretsiz API'si dakikada ~20 istek kabul eder
- 100 hisse için toplam analiz süresi ~8-10 dakika
- Bazı hisselerde veri eksikliği olabilir (yeni halka arzlar vb.)
- API rate limit aşılırsa 1-2 dakika bekleyip tekrar deneyin

## 📄 Lisans

Bu proje eğitim ve kişisel kullanım amaçlıdır. Yatırım tavsiyesi değildir.

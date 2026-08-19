# CLAUDE.md - BIST 100 Hisse Analiz Sistemi Geliştirici Kılavuzu

Bu belge, BIST 100 analiz sisteminin mimarisini, test çalıştırma prosedürlerini ve geliştirme kurallarını özetler.

---

## 📌 Proje Özeti

Bu proje, Borsa İstanbul (BIST) hisselerinin Yahoo Finance üzerinden canlı verilerini çekerek **Teknik Analiz (RSI, MACD, EMA, Bollinger, Hacim)** ve **Temel Analiz (F/K, PD/DD, Beta, ROE, Kâr Marjı, Borç/Özsermaye, Analist Tavsiyesi)** metrikleriyle 100 puan üzerinden skorlayan ve sonuçları hem JSON formatında hem de interaktif bir HTML Dashboard üzerinde sunan bir karar destek sistemidir.

---

## 🧪 Test Kuralları ve Yönergeleri (ZORUNLU)

> [!IMPORTANT]
> **KURAL**: Projeye eklenen her yeni özellik, düzeltme veya gösterge değişikliğinde mevcut testlerin bozulmadığından emin olunmalı ve **tüm testler çalıştırılmalıdır**. Yeni bir işlev eklendiğinde o işlev için `tests/` klasörüne karşılık gelen testler yazılmalıdır.

### Testleri Çalıştırma Komutları

```bash
# Tüm testleri detaylı çalıştırma
pytest -v
# veya
python -m pytest -v

# Belirli bir test dosyasını çalıştırma
pytest tests/test_technical_indicators.py -v
pytest tests/test_scoring.py -v
pytest tests/test_helpers_and_text.py -v
pytest tests/test_analyzer_pipeline.py -v
pytest tests/test_config.py -v

# Başarısız olan ilk testte durma (hızlı hata ayıklama)
pytest -x
```

### Test Mimarisi ve Dosya Yapısı

* `tests/conftest.py`: Ortak fixture'lar (yükselen/düşen/dalgalı fiyat serileri, yfinance DataFrame şablonları, mock Ticker fabrikası ve temel veri sözlükleri).
* `tests/test_technical_indicators.py`: RSI, MACD, EMA20/50, Bollinger Bantları hesaplama testleri.
* `tests/test_scoring.py`: Teknik (0-50) ve Temel (0-50) skorlama motoru kademe ve sınır testleri.
* `tests/test_helpers_and_text.py`: `safe_float`, otomatik Türkçe gerekçe üretimi (`generate_reasons`) ve özet analiz metni (`generate_analysis`) testleri.
* `tests/test_analyzer_pipeline.py`: Tekil analiz (`analyze_stock`), toplu analiz (`run_analysis`), hata yakalama, sentiment sınıflandırması ve JSON dışa aktarma testleri (Yahoo Finance mock'lanarak dış ağa bağımlı olmadan çalışır).
* `tests/test_config.py`: `stocks_config.json` ve `BIST100_STOCKS` hisse yapılandırma ve `.IS` ticker formatı doğrulama testleri.

---

## 🔒 Git Hook Güvencesi (Otomatik Test Zorunluluğu)

Bu proje, testlerin commit/push öncesinde otomatik çalıştırılmasını zorunlu kılan Git hook'ları içerir.

> [!IMPORTANT]
> **Pre-commit hook**: Her `git commit` işleminde `pytest` otomatik çalışır. Testler başarısız olursa **commit engellenir**.
> **Pre-push hook**: Her `git push` işleminde detaylı test çıktısı ile `pytest -v` çalışır. Testler başarısız olursa **push engellenir**.

### İlk Kurulum (Klonlama Sonrası)

```powershell
# PowerShell ile hook kurulumu
powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1

# veya manuel
Copy-Item hooks/pre-commit .git/hooks/pre-commit
Copy-Item hooks/pre-push .git/hooks/pre-push
```

### Acil Durumlarda Atlatma

```bash
# Yalnızca kritik acil durumlarda kullanılmalıdır:
git commit --no-verify -m "acil düzeltme"
git push --no-verify
```

### Dosya Yapısı

```
hooks/                      # Version-controlled hook kaynak dosyaları
├── pre-commit              # Commit öncesi pytest çalıştırır
└── pre-push                # Push öncesi pytest -v çalıştırır
scripts/
└── setup-hooks.ps1         # Hook'ları .git/hooks/'a kopyalayan kurulum scripti
```

---

## 🚀 Projeyi Çalıştırma

```bash
# 1. Bağımlılıkları yükleme
pip install -r requirements.txt

# 2. Analiz scriptini çalıştırma (bist_analysis_results.json üretir)
python bist_analyzer.py

# 3. Web Dashboard'u açma (tarayıcıda doğrudan açılabilir)
# Windows:
start bist_dashboard.html
# Mac:
open bist_dashboard.html
```

---

## 📐 Geliştirme ve Kodlama Standartları

1. **Dış API Çağrılarında Mock Kullanımı**: `yfinance` veya harici veri kaynakları test edilirken gerçek ağ istekleri yapılmamalı; `conftest.py` içerisindeki `mock_ticker_factory` ve `unittest.mock.patch` kullanılmalıdır.
2. **Defansif Programlama**: Yahoo Finance'ten gelen `None`, `NaN`, `Inf` gibi eksik veya bozuk veri alanları her zaman `safe_float()` ve liste/seri uzunluk kontrolleriyle (`len(prices) <= period`) karşılanmalıdır.
3. **Puanlama Tutarlılığı**: Teknik skor toplamda maksimum 50, Temel skor toplamda maksimum 50 puan olmalı; toplam puan 0-100 aralığında kalmalıdır.
4. **Sentiment Eşikleri**:
   - `50 - 100`: 🟢 `positive` (Olumlu)
   - `35 - 49`: ⚪ `neutral` (Nötr)
   - `< 35`: 🔴 `negative` (Olumsuz)

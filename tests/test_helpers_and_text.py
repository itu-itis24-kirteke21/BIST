import numpy as np
import pytest
from bist_analyzer import safe_float, generate_reasons, generate_analysis


class TestSafeFloat:
    """safe_float yardımcı fonksiyon testleri."""

    def test_valid_numbers(self):
        """Geçerli sayı ve sayısal string dönüşümlerini test eder."""
        assert safe_float(10) == 10.0
        assert safe_float(15.75) == 15.75
        assert safe_float("42.5") == 42.5
        assert safe_float("-3.14") == -3.14

    def test_nan_and_inf(self):
        """NaN ve sonsuz (inf) değerlerin default değere dönüştüğünü doğrular."""
        assert safe_float(np.nan) == 0
        assert safe_float(float('nan')) == 0
        assert safe_float(np.inf) == 0
        assert safe_float(float('inf')) == 0
        assert safe_float(-np.inf) == 0

    def test_none_and_invalid_string(self):
        """None veya metinsel geçersiz girdilerin default değer döndürdüğünü doğrular."""
        assert safe_float(None) == 0
        assert safe_float("not-a-number") == 0
        assert safe_float([1, 2]) == 0

    def test_custom_default(self):
        """Özelleştirilmiş varsayılan değer parametresini doğrular."""
        assert safe_float(None, default=3) == 3
        assert safe_float(np.nan, default=1.0) == 1.0


class TestGenerateReasons:
    """Analiz gerekçeleri (reasons) üretimi testleri."""

    @pytest.fixture
    def base_stock_data(self):
        return {
            'code': 'THYAO',
            'name': 'Türk Hava Yolları',
            'rsi': 60.0,
            'macd': 1.5,
            'macd_hist': 0.3,
            'price': 150.0,
            'ema20': 140.0,
            'ema50': 130.0,
            'vol_ratio': 1.4,
            'change': 2.0,
            'pe': 7.5,
            'roe': 22.0,
            'debt_equity': 35.0,
            'rec_mean': 1.5
        }

    def test_positive_reasons_generation(self, base_stock_data):
        """Olumlu göstergelerde doğru gerekçe mesajlarının üretildiğini doğrular."""
        reasons = generate_reasons(base_stock_data)
        joined = " ".join(reasons)
        assert "güçlü momentum" in joined
        assert "güçlü alım sinyali" in joined
        assert "güçlü yükseliş trendi" in joined
        assert "alım baskısı güçlü" in joined
        assert "değerlemesi makul/ucuz" in joined
        assert "Özsermaye kârlılığı (ROE)" in joined
        assert "sağlam bilanço" in joined
        assert "Güçlü Al" in joined

    def test_negative_and_warning_reasons_generation(self, base_stock_data):
        """Aşırı alım, düşüş trendi, yüksek kaldıraç durumlarındaki uyarı gerekçelerini doğrular."""
        stock = base_stock_data.copy()
        stock['rsi'] = 75.0
        stock['macd'] = -1.0
        stock['macd_hist'] = -0.5
        stock['price'] = 120.0
        stock['ema20'] = 125.0
        stock['ema50'] = 130.0
        stock['vol_ratio'] = 1.5
        stock['change'] = -2.5
        stock['pe'] = 50.0
        stock['roe'] = 3.0
        stock['debt_equity'] = 150.0
        stock['rec_mean'] = 4.0

        reasons = generate_reasons(stock)
        joined = " ".join(reasons)
        assert "aşırı alım bölgesinde" in joined
        assert "satış baskısı devam ediyor" in joined
        assert "düşüş trendi sinyali" in joined
        assert "satış baskısı" in joined
        assert "yüksek değerleme" in joined
        assert "Özsermaye kârlılığı (ROE)" in joined and "zayıf" in joined
        assert "yüksek kaldıraç" in joined
        assert "Zayıf" in joined


class TestGenerateAnalysis:
    """Yapay zeka analiz metni (narrative) üretimi testleri."""

    @pytest.fixture
    def stock_summary_data(self):
        return {
            'code': 'GARAN',
            'name': 'Garanti BBVA',
            'totalScore': 80,
            'rsi': 58.0,
            'macd_hist': 0.4,
            'price': 95.0,
            'ema50': 90.0,
            'pe': 5.2,
            'roe': 28.0,
            'debt_equity': 45.0,
            'rec_mean': 1.3,
            'range_position': 85.0
        }

    @pytest.mark.parametrize("score, expected_phrase", [
        (80, "güçlü bir görünüm sergiliyor"),
        (65, "genel olarak olumlu sinyaller veriyor"),
        (50, "karışık sinyaller veriyor"),
        (30, "zayıf sinyaller veriyor, dikkatli olunması önerilir"),
    ])
    def test_analysis_score_tiers(self, stock_summary_data, score, expected_phrase):
        """Farklı toplam skor seviyelerine göre özet giriş cümlesinin doğruluğunu test eder."""
        stock = stock_summary_data.copy()
        stock['totalScore'] = score
        analysis = generate_analysis(stock)
        assert expected_phrase in analysis
        assert stock['name'] in analysis
        assert stock['code'] in analysis

    def test_analysis_includes_metrics(self, stock_summary_data):
        """Oluşturulan analiz metninin temel ve teknik göstergeleri içerdiğini doğrular."""
        analysis = generate_analysis(stock_summary_data)
        assert "RSI 58.0" in analysis
        assert "MACD histogram pozitif" in analysis
        assert "EMA 50'nin üzerinde" in analysis
        assert "F/K oranı 5.2" in analysis
        assert "ROE %28.0" in analysis
        assert "%85.0 pozisyonunda" in analysis

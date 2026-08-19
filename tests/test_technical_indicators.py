import numpy as np
import pytest

from bist_analyzer import (
    calculate_bollinger,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
)


class TestCalculateRSI:
    """RSI (Relative Strength Index) hesaplama testleri."""

    def test_rsi_bounds(self, sample_prices_oscillating):
        """RSI değerinin 0 ile 100 arasında olduğunu doğrular."""
        rsi = calculate_rsi(sample_prices_oscillating)
        assert 0.0 <= rsi <= 100.0

    def test_rsi_uptrend_high(self, sample_prices_uptrend):
        """Güçlü yükseliş trendinde RSI değerinin 50'nin üzerinde olduğunu doğrular."""
        rsi = calculate_rsi(sample_prices_uptrend)
        assert rsi > 50.0

    def test_rsi_downtrend_low(self, sample_prices_downtrend):
        """Güçlü düşüş trendinde RSI değerinin 50'nin altında olduğunu doğrular."""
        rsi = calculate_rsi(sample_prices_downtrend)
        assert rsi < 50.0

    def test_rsi_monotonic_increase(self):
        """Sürekli artan fiyatta RSI değerinin 100'e yakın olduğunu doğrular."""
        prices = np.array([float(i) for i in range(1, 30)])
        rsi = calculate_rsi(prices)
        assert rsi > 95.0

    def test_rsi_monotonic_decrease(self):
        """Sürekli düşen fiyatta RSI değerinin 0'a yakın olduğunu doğrular."""
        prices = np.array([float(30 - i) for i in range(30)])
        rsi = calculate_rsi(prices)
        assert rsi < 5.0

    def test_rsi_flat_prices(self, sample_prices_flat):
        """Sabit fiyatta sıfıra bölünme hatası vermeden geçerli bir değer ürettiğini doğrular."""
        rsi = calculate_rsi(sample_prices_flat)
        assert isinstance(rsi, float | np.floating)
        assert 0.0 <= rsi <= 100.0

    def test_rsi_insufficient_data(self):
        """Boş veya çok kısa veri geldiğinde varsayılan (50) değer döndüğünü doğrular."""
        assert calculate_rsi(np.array([])) == 50
        assert calculate_rsi(np.array([100.0])) == 50


class TestCalculateMACD:
    """MACD hesaplama testleri."""

    def test_macd_returns_three_floats(self, sample_prices_uptrend):
        """MACD fonksiyonunun 3 sayısal değer (macd, signal, hist) döndürdüğünü doğrular."""
        macd, signal, hist = calculate_macd(sample_prices_uptrend)
        assert isinstance(macd, float | np.floating)
        assert isinstance(signal, float | np.floating)
        assert isinstance(hist, float | np.floating)

    def test_macd_histogram_relation(self, sample_prices_oscillating):
        """MACD histogramının macd - signal farkına eşit olduğunu doğrular."""
        macd, signal, hist = calculate_macd(sample_prices_oscillating)
        assert pytest.approx(macd - signal, rel=1e-5) == hist

    def test_macd_uptrend_positive(self, sample_prices_uptrend):
        """Yükseliş trendinde MACD değerinin pozitif olmasını doğrular."""
        macd, _, _ = calculate_macd(sample_prices_uptrend)
        assert macd > 0

    def test_macd_downtrend_negative(self, sample_prices_downtrend):
        """Düşüş trendinde MACD değerinin negatif olmasını doğrular."""
        macd, _, _ = calculate_macd(sample_prices_downtrend)
        assert macd < 0


class TestCalculateEMA:
    """EMA (Üstel Hareketli Ortalama) hesaplama testleri."""

    def test_ema_span_calculation(self, sample_prices_uptrend):
        """EMA20 ve EMA50 hesaplamalarının geçerli float değerler ürettiğini doğrular."""
        ema20 = calculate_ema(sample_prices_uptrend, 20)
        ema50 = calculate_ema(sample_prices_uptrend, 50)
        assert isinstance(ema20, float | np.floating)
        assert isinstance(ema50, float | np.floating)

    def test_ema_uptrend_alignment(self, sample_prices_uptrend):
        """Yükselen trendde EMA20'nin EMA50'den büyük olduğunu doğrular."""
        ema20 = calculate_ema(sample_prices_uptrend, 20)
        ema50 = calculate_ema(sample_prices_uptrend, 50)
        assert ema20 > ema50

    def test_ema_downtrend_alignment(self, sample_prices_downtrend):
        """Düşen trendde EMA20'nin EMA50'den küçük olduğunu doğrular."""
        ema20 = calculate_ema(sample_prices_downtrend, 20)
        ema50 = calculate_ema(sample_prices_downtrend, 50)
        assert ema20 < ema50


class TestCalculateBollinger:
    """Bollinger Bantları hesaplama testleri."""

    def test_bollinger_bands_ordering(self, sample_prices_oscillating):
        """Üst bandın alt banttan büyük olduğunu doğrular."""
        upper, lower, position = calculate_bollinger(sample_prices_oscillating)
        assert upper > lower
        assert isinstance(position, float | np.floating)

    def test_bollinger_position_formula(self, sample_prices_uptrend):
        """Bollinger bant pozisyonunun (fiyat - alt) / (üst - alt) formülüne uyduğunu doğrular."""
        upper, lower, position = calculate_bollinger(sample_prices_uptrend)
        current = sample_prices_uptrend[-1]
        expected_pos = (current - lower) / (upper - lower + 1e-10)
        assert pytest.approx(expected_pos, rel=1e-5) == position

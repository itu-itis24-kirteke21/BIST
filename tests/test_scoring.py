import pytest
from bist_analyzer import (
    calculate_technical_score,
    calculate_fundamental_score,
)


class TestTechnicalScore:
    """Teknik analiz skorlama fonksiyonu testleri (0 - 50 Puan)."""

    def test_maximum_technical_score(self):
        """Mükemmel teknik göstergelerde skorun 50 olduğunu doğrular."""
        score = calculate_technical_score(
            rsi=60.0,            # 12 puan (50 <= rsi <= 70)
            macd=2.5,            # 12 puan (macd > 0 and macd_hist > 0)
            macd_hist=0.5,
            price=120.0,         # 10 puan (price > ema20 > ema50)
            ema20=110.0,
            ema50=100.0,
            vol_ratio=1.5,       # 8 puan (vol_ratio > 1.2 and daily_change > 0)
            daily_change=2.5,
            bb_position=0.75     # 8 puan (0.6 < bb_position < 0.95)
        )
        assert score == 50

    def test_minimum_technical_score(self):
        """Kötü teknik göstergelerde taban puanların hesaplandığını doğrular."""
        score = calculate_technical_score(
            rsi=85.0,            # 4 puan (rsi > 80)
            macd=-2.0,           # 3 puan (macd < 0 and macd_hist < 0)
            macd_hist=-0.5,
            price=80.0,          # 3 puan (price <= ema20 and price <= ema50)
            ema20=90.0,
            ema50=100.0,
            vol_ratio=0.5,       # 3 puan (vol_ratio <= 0.8)
            daily_change=-1.0,
            bb_position=0.1      # 3 puan (bb_position <= 0.2)
        )
        assert score == (4 + 3 + 3 + 3 + 3)

    @pytest.mark.parametrize("rsi, expected_points", [
        (65.0, 12),  # 50 <= rsi <= 70
        (45.0, 10),  # 40 <= rsi < 50
        (75.0, 8),   # 70 < rsi <= 80
        (35.0, 7),   # 30 <= rsi < 40
        (85.0, 4),   # rsi > 80
        (25.0, 5),   # else (rsi < 30)
    ])
    def test_rsi_scoring_brackets(self, rsi, expected_points):
        """RSI puan kademelerini doğrular."""
        # Diğer göstergeleri sabit tutup sadece RSI katkısını test et
        score = calculate_technical_score(
            rsi=rsi,
            macd=1.0, macd_hist=0.5,
            price=120.0, ema20=110.0, ema50=100.0,
            vol_ratio=1.5, daily_change=1.0,
            bb_position=0.7
        )
        # Baz puan: macd(12) + ema(10) + vol(8) + bb(8) = 38
        assert score == 38 + expected_points

    @pytest.mark.parametrize("macd, macd_hist, expected_points", [
        (1.0, 0.5, 12),    # hist > 0 and macd > 0
        (-0.5, 0.2, 9),    # hist > 0 (macd <= 0)
        (-1.0, -0.5, 3),   # hist < 0 and macd < 0
        (1.0, -0.2, 6),    # else
    ])
    def test_macd_scoring_brackets(self, macd, macd_hist, expected_points):
        """MACD puan kademelerini doğrular."""
        score = calculate_technical_score(
            rsi=60.0,
            macd=macd, macd_hist=macd_hist,
            price=120.0, ema20=110.0, ema50=100.0,
            vol_ratio=1.5, daily_change=1.0,
            bb_position=0.7
        )
        # Baz puan: rsi(12) + ema(10) + vol(8) + bb(8) = 38
        assert score == 38 + expected_points


class TestFundamentalScore:
    """Temel analiz skorlama fonksiyonu testleri (0 - 50 Puan)."""

    def test_maximum_fundamental_score(self):
        """En iyi temel oranlarda skorun 50 olduğunu doğrular."""
        score = calculate_fundamental_score(
            pe=6.0,               # 10 puan (0 < pe <= 8)
            pb=1.2,               # 8 puan (0 < pb <= 1.5)
            beta=1.0,             # 6 puan (0.8 <= beta <= 1.2)
            profit_margin=25.0,   # 8 puan (>= 20)
            roe=22.0,             # 8 puan (>= 20)
            debt_equity=20.0,     # 6 puan (0 <= debt_equity <= 30)
            rec_mean=1.2          # 4 puan (<= 1.5)
        )
        assert score == 50

    def test_minimum_fundamental_score(self):
        """En zayıf temel oranlarda taban puanların hesaplandığını doğrular."""
        score = calculate_fundamental_score(
            pe=50.0,              # 3 puan (pe > 40)
            pb=15.0,              # 2 puan (pb > 10)
            beta=2.0,             # 4 puan (else)
            profit_margin=-5.0,   # 2 puan (else)
            roe=-10.0,            # 2 puan (else)
            debt_equity=180.0,    # 2 puan (else)
            rec_mean=4.5          # 0 puan (> 3.5)
        )
        assert score == (3 + 2 + 4 + 2 + 2 + 2 + 0)

    @pytest.mark.parametrize("pe, expected_points", [
        (5.0, 10),
        (10.0, 9),
        (20.0, 7),
        (30.0, 5),
        (50.0, 3),
        (0.0, 4),    # N/A veya <= 0 durumu
        (-5.0, 4),
    ])
    def test_pe_scoring_brackets(self, pe, expected_points):
        """Fiyat/Kazanç (P/E) puan kademelerini doğrular."""
        score = calculate_fundamental_score(
            pe=pe,
            pb=1.2, beta=1.0, profit_margin=25.0, roe=22.0,
            debt_equity=20.0, rec_mean=1.2
        )
        # Baz puan (pe hariç): pb(8) + beta(6) + margin(8) + roe(8) + debt(6) + rec(4) = 40
        assert score == 40 + expected_points

    @pytest.mark.parametrize("roe, expected_points", [
        (25.0, 8),
        (18.0, 7),
        (12.0, 6),
        (8.0, 5),
        (3.0, 4),
        (-2.0, 2),
    ])
    def test_roe_scoring_brackets(self, roe, expected_points):
        """Özsermaye kârlılığı (ROE) puan kademelerini doğrular."""
        score = calculate_fundamental_score(
            pe=6.0, pb=1.2, beta=1.0, profit_margin=25.0,
            roe=roe,
            debt_equity=20.0, rec_mean=1.2
        )
        # Baz puan (roe hariç): pe(10) + pb(8) + beta(6) + margin(8) + debt(6) + rec(4) = 42
        assert score == 42 + expected_points

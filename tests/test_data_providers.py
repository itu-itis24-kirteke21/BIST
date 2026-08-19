"""Veri Sağlayıcıları ve Aggregator Test Paketi."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from data_providers.aggregator import StockDataAggregator
from data_providers.base import BaseDataProvider, FundamentalData, PriceHistoryData, TechnicalSummaryData
from data_providers.isyatirim_provider import IsYatirimProvider
from data_providers.tradingview_provider import TradingViewProvider
from data_providers.yahoo_provider import YahooFinanceProvider


class TestYahooFinanceProvider:
    """YahooFinanceProvider birim testleri."""

    def test_get_price_history_success(self, sample_history_df):
        """Geçerli geçmiş verisiyle PriceHistoryData nesnesinin oluşturulmasını test eder."""
        provider = YahooFinanceProvider()
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = sample_history_df
        mock_ticker.info = {"fiftyTwoWeekLow": 80.0, "fiftyTwoWeekHigh": 140.0}

        with patch("yfinance.Ticker", return_value=mock_ticker):
            result = provider.get_price_history("THYAO.IS")

        assert result is not None
        assert isinstance(result, PriceHistoryData)
        assert len(result.close) == len(sample_history_df)
        assert result.fifty_two_week_low == 80.0
        assert result.fifty_two_week_high == 140.0
        assert result.latest_price == sample_history_df["Close"].iloc[-1]

    def test_get_price_history_empty_or_short(self):
        """Boş veya yetersiz veri durumunda None döndüğünü test eder."""
        provider = YahooFinanceProvider()
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()

        with patch("yfinance.Ticker", return_value=mock_ticker):
            assert provider.get_price_history("EMPTY.IS") is None

    def test_get_fundamental_data_success(self, sample_info_positive):
        """Temel analiz rasyolarının başarıyla çekildiğini doğrular."""
        provider = YahooFinanceProvider()
        mock_ticker = MagicMock()
        mock_ticker.info = sample_info_positive

        with patch("yfinance.Ticker", return_value=mock_ticker):
            result = provider.get_fundamental_data("THYAO", "THYAO.IS")

        assert result is not None
        assert isinstance(result, FundamentalData)
        assert result.pe == sample_info_positive["trailingPE"]
        assert result.pb == sample_info_positive["priceToBook"]
        assert result.beta == sample_info_positive["beta"]
        assert result.roe == sample_info_positive["returnOnEquity"] * 100.0
        assert result.source == "YahooFinance"


class TestIsYatirimProvider:
    """IsYatirimProvider birim testleri."""

    def test_get_fundamental_data_success(self):
        """İş Yatırım kütüphanesi başarıyla çalıştığında veri döner."""
        provider = IsYatirimProvider()
        mock_df = pd.DataFrame({"Kalem": ["Net Kar", "Ozkaynaklar"], "Deger": [1000, 5000]})

        with patch("isyatirimhisse.fetch_financials", return_value=mock_df):
            result = provider.get_fundamental_data("THYAO", "THYAO.IS")

        assert result is not None
        assert isinstance(result, FundamentalData)
        assert result.source == "IsYatirim"

    def test_get_fundamental_data_exception_handling(self):
        """İş Yatırım hata verdiğinde çökmeden None döner."""
        provider = IsYatirimProvider()
        with patch("isyatirimhisse.fetch_financials", side_effect=Exception("Baglanti hatasi")):
            result = provider.get_fundamental_data("THYAO", "THYAO.IS")

        assert result is None


class TestTradingViewProvider:
    """TradingViewProvider birim testleri."""

    def test_get_technical_summary_success(self):
        """TradingView teknik özetinin çekilmesini test eder."""
        provider = TradingViewProvider()
        mock_analysis = MagicMock()
        mock_analysis.summary = {"RECOMMENDATION": "STRONG_BUY", "BUY": 16, "SELL": 2, "NEUTRAL": 8}
        mock_analysis.indicators = {"RSI": 62.5, "MACD.macd": 1.45}

        mock_handler = MagicMock()
        mock_handler.get_analysis.return_value = mock_analysis

        with patch("tradingview_ta.TA_Handler", return_value=mock_handler):
            result = provider.get_technical_summary("THYAO")

        assert result is not None
        assert isinstance(result, TechnicalSummaryData)
        assert result.recommendation == "STRONG_BUY"
        assert result.buy_signals == 16
        assert result.rsi == 62.5
        assert result.source == "TradingView"

    def test_get_technical_summary_exception_handling(self):
        """TradingView hata verdiğinde None döner."""
        provider = TradingViewProvider()
        with patch("tradingview_ta.TA_Handler", side_effect=Exception("TV timeout")):
            assert provider.get_technical_summary("THYAO") is None


class TestStockDataAggregator:
    """StockDataAggregator hibrit entegrasyon testleri."""

    @pytest.fixture
    def mock_price_provider(self, sample_prices_uptrend):
        provider = MagicMock(spec=BaseDataProvider)
        provider.get_price_history.return_value = PriceHistoryData(
            close=sample_prices_uptrend,
            volume=np.array([2000000] * len(sample_prices_uptrend)),
            fifty_two_week_low=90.0,
            fifty_two_week_high=140.0,
            latest_price=sample_prices_uptrend[-1],
            daily_change_pct=1.5,
        )
        return provider

    def test_aggregator_enrichment_fallback(self, mock_price_provider):
        """Birincil sağlayıcıda eksik olan F/K ve ROE verisinin ikincil sağlayıcıdan zenginleştirilmesini test eder."""
        # 1. Birincil sağlayıcı (Yahoo): F/K ve ROE eksik (0.0)
        yahoo_mock = MagicMock(spec=BaseDataProvider)
        yahoo_mock.get_fundamental_data.return_value = FundamentalData(
            pe=0.0, pb=1.2, beta=1.0, profit_margin=10.0, roe=0.0, debt_equity=40.0, source="Yahoo"
        )

        # 2. İkincil sağlayıcı (İş Yatırım): F/K ve ROE mevcut
        isyatirim_mock = MagicMock(spec=BaseDataProvider)
        isyatirim_mock.get_fundamental_data.return_value = FundamentalData(
            pe=6.5, pb=1.2, roe=24.0, debt_equity=40.0, source="IsYatirim"
        )

        aggregator = StockDataAggregator(
            price_provider=mock_price_provider,
            fundamental_providers=[yahoo_mock, isyatirim_mock],
            enable_tv_summary=False,
        )

        meta = {"code": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"}
        result = aggregator.fetch_full_stock_data("THYAO.IS", meta)

        assert result is not None
        assert result["code"] == "THYAO"
        # F/K ve ROE ikincil sağlayıcıdan zenginleştirilmiş olmalı
        assert result["fundamental"].pe == 6.5
        assert result["fundamental"].roe == 24.0
        assert result["fundamental"].pb == 1.2

    def test_aggregator_batch_data(self, mock_price_provider):
        """Toplu hisse listesi veri çekimini test eder."""
        fundamental_mock = MagicMock(spec=BaseDataProvider)
        fundamental_mock.get_fundamental_data.return_value = FundamentalData(pe=8.0, roe=15.0)

        aggregator = StockDataAggregator(
            price_provider=mock_price_provider,
            fundamental_providers=[fundamental_mock],
            enable_tv_summary=False,
        )

        stocks = {
            "THYAO.IS": {"code": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"},
            "GARAN.IS": {"code": "GARAN", "name": "Garanti BBVA", "sector": "Bankacılık"},
        }

        results = aggregator.fetch_batch_data(stocks, delay_seconds=0.0)
        assert len(results) == 2
        assert results[0]["code"] == "THYAO"
        assert results[1]["code"] == "GARAN"

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_stock_meta():
    """Örnek hisse meta bilgisi."""
    return {"code": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"}


@pytest.fixture
def sample_stocks_dict():
    """Analiz testleri için örnek hisse listesi sözlüğü."""
    return {
        "THYAO.IS": {"code": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"},
        "GARAN.IS": {"code": "GARAN", "name": "Garanti BBVA", "sector": "Bankacılık"},
        "ASELS.IS": {"code": "ASELS", "name": "Aselsan", "sector": "Savunma"},
    }


@pytest.fixture
def sample_prices_uptrend():
    """60 günlük yükselen fiyat serisi."""
    np.random.seed(42)
    base = 100.0
    steps = 60
    trend = np.linspace(0, 30, steps)
    noise = np.random.normal(0, 0.5, steps)
    return base + trend + noise


@pytest.fixture
def sample_prices_downtrend():
    """60 günlük düşen fiyat serisi."""
    np.random.seed(42)
    base = 100.0
    steps = 60
    trend = np.linspace(0, -30, steps)
    noise = np.random.normal(0, 0.5, steps)
    return base + trend + noise


@pytest.fixture
def sample_prices_flat():
    """60 günlük sabit fiyat serisi."""
    return np.full(60, 100.0)


@pytest.fixture
def sample_prices_oscillating():
    """60 günlük dalgalı (sinüs) fiyat serisi."""
    x = np.linspace(0, 4 * np.pi, 60)
    return 100.0 + 10.0 * np.sin(x)


@pytest.fixture
def sample_history_df(sample_prices_uptrend):
    """yfinance.history formatında 60 günlük örnek DataFrame."""
    dates = pd.date_range(end=datetime.now(), periods=len(sample_prices_uptrend), freq="B")
    np.random.seed(42)
    volumes = np.random.randint(1_000_000, 5_000_000, size=len(sample_prices_uptrend))

    df = pd.DataFrame(
        {
            "Open": sample_prices_uptrend * 0.99,
            "High": sample_prices_uptrend * 1.02,
            "Low": sample_prices_uptrend * 0.98,
            "Close": sample_prices_uptrend,
            "Volume": volumes,
        },
        index=dates,
    )
    return df


@pytest.fixture
def sample_info_positive():
    """Güçlü temel analize sahip örnek info sözlüğü."""
    return {
        "trailingPE": 6.5,
        "priceToBook": 1.2,
        "beta": 1.0,
        "profitMargins": 0.25,
        "returnOnEquity": 0.28,
        "debtToEquity": 25.0,
        "recommendationMean": 1.4,
        "fiftyTwoWeekLow": 80.0,
        "fiftyTwoWeekHigh": 140.0,
    }


@pytest.fixture
def sample_info_negative():
    """Zayıf temel analize sahip örnek info sözlüğü."""
    return {
        "trailingPE": 55.0,
        "priceToBook": 12.0,
        "beta": 1.8,
        "profitMargins": -0.05,
        "returnOnEquity": -0.08,
        "debtToEquity": 180.0,
        "recommendationMean": 4.2,
        "fiftyTwoWeekLow": 70.0,
        "fiftyTwoWeekHigh": 150.0,
    }


@pytest.fixture
def sample_info_neutral():
    """Dengeli/Nötr temel analize sahip örnek info sözlüğü."""
    return {
        "trailingPE": 18.0,
        "priceToBook": 3.5,
        "beta": 1.1,
        "profitMargins": 0.08,
        "returnOnEquity": 0.12,
        "debtToEquity": 75.0,
        "recommendationMean": 2.8,
        "fiftyTwoWeekLow": 85.0,
        "fiftyTwoWeekHigh": 130.0,
    }


@pytest.fixture
def sample_info_missing():
    """Boş / None / Geçersiz değerler içeren info sözlüğü."""
    return {
        "trailingPE": None,
        "priceToBook": None,
        "beta": None,
        "profitMargins": None,
        "returnOnEquity": None,
        "debtToEquity": None,
        "recommendationMean": None,
        "fiftyTwoWeekLow": None,
        "fiftyTwoWeekHigh": None,
    }


@pytest.fixture
def mock_ticker_factory():
    """Özelleştirilebilir sahte yfinance.Ticker nesnesi üreten fabrika fixture."""

    def _create_mock_ticker(history_df, info_dict):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = history_df
        mock_ticker.info = info_dict
        return mock_ticker

    return _create_mock_ticker

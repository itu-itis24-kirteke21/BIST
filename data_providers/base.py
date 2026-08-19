"""BIST Veri Sağlayıcıları için Temel Soyut Arayüz ve Veri Modelleri."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


@dataclass
class PriceHistoryData:
    """Fiyat geçmişi ve hacim veri modeli."""

    close: np.ndarray
    volume: np.ndarray
    fifty_two_week_low: float = 0.0
    fifty_two_week_high: float = 0.0
    latest_price: float = 0.0
    daily_change_pct: float = 0.0


@dataclass
class FundamentalData:
    """Temel analiz ve finansal oranlar veri modeli."""

    pe: float = 0.0  # F/K Oranı
    pb: float = 0.0  # PD/DD Oranı
    beta: float = 1.0  # Beta
    profit_margin: float = 0.0  # Net Kâr Marjı (%)
    roe: float = 0.0  # Özsermaye Kârlılığı (%)
    debt_equity: float = 0.0  # Borç/Özsermaye Oranı
    rec_mean: float = 3.0  # Analist tavsiye ortalaması (1=Strong Buy, 5=Sell)
    source: str = "unknown"
    extra_metrics: dict = field(default_factory=dict)


@dataclass
class TechnicalSummaryData:
    """Canlı teknik osilatör ve indikatör özet modeli."""

    recommendation: str = "NEUTRAL"
    buy_signals: int = 0
    sell_signals: int = 0
    neutral_signals: int = 0
    rsi: float | None = None
    macd: float | None = None
    source: str = "unknown"


class BaseDataProvider(ABC):
    """Tüm veri sağlayıcıların uygulayacağı soyut temel sınıf."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Sağlayıcının benzersiz adı."""
        pass

    @abstractmethod
    def get_price_history(self, ticker: str, period: str = "6mo") -> PriceHistoryData | None:
        """Geçmiş fiyat ve hacim serilerini çeker."""
        pass

    @abstractmethod
    def get_fundamental_data(self, stock_code: str, ticker: str) -> FundamentalData | None:
        """Temel analiz finansal rasyolarını çeker."""
        pass

"""Yahoo Finance Veri Sağlayıcısı (yfinance)."""

import numpy as np
import yfinance as yf

from data_providers.base import BaseDataProvider, FundamentalData, PriceHistoryData


def _safe_float(val, default: float = 0.0) -> float:
    """Güvenli float dönüşümü."""
    try:
        if val is None:
            return default
        v = float(val)
        return default if np.isnan(v) or np.isinf(v) else v
    except (TypeError, ValueError):
        return default


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance API üzerinden OHLCV ve temel veri çeken sağlayıcı."""

    @property
    def name(self) -> str:
        return "YahooFinance"

    def get_price_history(self, ticker: str, period: str = "6mo") -> PriceHistoryData | None:
        """Belirtilen hissenin fiyat ve hacim geçmişini çeker."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty or len(hist) < 50:
                return None

            close = hist["Close"].values
            volume = hist["Volume"].values
            info = getattr(stock, "info", {}) or {}

            wk_low = _safe_float(info.get("fiftyTwoWeekLow"), default=float(np.min(close)))
            wk_high = _safe_float(info.get("fiftyTwoWeekHigh"), default=float(np.max(close)))
            latest_price = float(close[-1])

            daily_change = 0.0
            if len(close) >= 2 and close[-2] != 0:
                daily_change = (close[-1] - close[-2]) / close[-2] * 100.0

            return PriceHistoryData(
                close=close,
                volume=volume,
                fifty_two_week_low=wk_low,
                fifty_two_week_high=wk_high,
                latest_price=latest_price,
                daily_change_pct=daily_change,
            )
        except Exception:
            return None

    def get_fundamental_data(self, stock_code: str, ticker: str) -> FundamentalData | None:
        """Hissenin temel finansal oranlarını çeker."""
        try:
            stock = yf.Ticker(ticker)
            info = getattr(stock, "info", {}) or {}

            pe = _safe_float(info.get("trailingPE"), default=0.0)
            pb = _safe_float(info.get("priceToBook"), default=0.0)
            beta = _safe_float(info.get("beta"), default=1.0)
            profit_margin = _safe_float(info.get("profitMargins"), default=0.0) * 100.0
            roe = _safe_float(info.get("returnOnEquity"), default=0.0) * 100.0
            debt_equity = _safe_float(info.get("debtToEquity"), default=0.0)
            rec_mean = _safe_float(info.get("recommendationMean"), default=3.0)

            return FundamentalData(
                pe=pe,
                pb=pb,
                beta=beta,
                profit_margin=profit_margin,
                roe=roe,
                debt_equity=debt_equity,
                rec_mean=rec_mean,
                source=self.name,
            )
        except Exception:
            return None

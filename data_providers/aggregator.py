"""BIST Veri Sağlayıcılarını Birleştiren ve Eksik Verileri Tamamlayan Toplayıcı (Aggregator)."""

import time
from typing import Any

from data_providers.base import BaseDataProvider, FundamentalData, PriceHistoryData, TechnicalSummaryData
from data_providers.isyatirim_provider import IsYatirimProvider
from data_providers.tradingview_provider import TradingViewProvider
from data_providers.yahoo_provider import YahooFinanceProvider


class StockDataAggregator:
    """Çoklu kaynaklardan hisse verisi toplayıp birleştiren ve yedekli çalışan servis."""

    def __init__(
        self,
        price_provider: BaseDataProvider | None = None,
        fundamental_providers: list[BaseDataProvider] | None = None,
        technical_summary_provider: Any | None = None,
        enable_tv_summary: bool = True,
    ):
        self.price_provider = price_provider or YahooFinanceProvider()
        self.fundamental_providers = fundamental_providers or [
            YahooFinanceProvider(),
            IsYatirimProvider(),
        ]
        self.tv_provider = technical_summary_provider or (TradingViewProvider() if enable_tv_summary else None)

    def fetch_full_stock_data(self, ticker: str, meta: dict[str, Any], period: str = "6mo") -> dict[str, Any] | None:
        """Belirtilen hisse için fiyat geçmişi, temel rasyolar ve canlı teknik sinyalleri birleştirir."""
        code = meta.get("code", ticker.replace(".IS", ""))

        # 1. Fiyat ve Hacim Geçmişi (OHLCV)
        price_data: PriceHistoryData | None = self.price_provider.get_price_history(ticker, period=period)
        if price_data is None or len(price_data.close) < 50:
            return None

        # 2. Temel Analiz Verileri (Öncelikli sağlayıcıdan al, eksikse yedekten zenginleştir)
        fundamental: FundamentalData | None = None
        for provider in self.fundamental_providers:
            try:
                data = provider.get_fundamental_data(code, ticker)
                if data is not None:
                    if fundamental is None:
                        fundamental = data
                    else:
                        # Eksik alanları zenginleştir
                        if fundamental.pe <= 0 and data.pe > 0:
                            fundamental.pe = data.pe
                        if fundamental.pb <= 0 and data.pb > 0:
                            fundamental.pb = data.pb
                        if fundamental.roe == 0 and data.roe != 0:
                            fundamental.roe = data.roe
                        if fundamental.debt_equity == 0 and data.debt_equity != 0:
                            fundamental.debt_equity = data.debt_equity
            except Exception:
                continue

        if fundamental is None:
            fundamental = FundamentalData()

        # 3. TradingView Canlı Teknik Özeti (Opsiyonel)
        tv_summary: TechnicalSummaryData | None = None
        if self.tv_provider is not None:
            try:
                tv_summary = self.tv_provider.get_technical_summary(code)
            except Exception:
                tv_summary = None

        return {
            "code": code,
            "name": meta.get("name", code),
            "sector": meta.get("sector", "Genel"),
            "price_data": price_data,
            "fundamental": fundamental,
            "tv_summary": tv_summary,
        }

    def fetch_batch_data(
        self,
        stock_list: dict[str, dict[str, str]],
        delay_seconds: float = 0.3,
    ) -> list[dict[str, Any]]:
        """Toplu hisse listesi için veri çeker."""
        results = []
        for ticker, meta in stock_list.items():
            data = self.fetch_full_stock_data(ticker, meta)
            if data is not None:
                results.append(data)
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        return results

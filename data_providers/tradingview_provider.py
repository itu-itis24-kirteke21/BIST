"""TradingView Canlı Teknik Analiz Sağlayıcısı (tradingview-ta)."""

from data_providers.base import BaseDataProvider, FundamentalData, PriceHistoryData, TechnicalSummaryData


class TradingViewProvider(BaseDataProvider):
    """TradingView üzerinden BIST hisselerinin canlı teknik özetini çeken sağlayıcı."""

    @property
    def name(self) -> str:
        return "TradingView"

    def get_price_history(self, ticker: str, period: str = "6mo") -> PriceHistoryData | None:
        """TradingView TA sağlayıcısı teknik özet sağlar, ham OHLCV dizisi için Yahoo kullanılır."""
        return None

    def get_fundamental_data(self, stock_code: str, ticker: str) -> FundamentalData | None:
        """TradingView TA sağlayıcısı teknik analiz odaklıdır."""
        return None

    def get_technical_summary(self, stock_code: str) -> TechnicalSummaryData | None:
        """TradingView üzerinden canlı teknik özet ve konsensüsü çeker."""
        try:
            from tradingview_ta import Interval, TA_Handler

            code = stock_code.upper().replace(".IS", "")
            handler = TA_Handler(
                symbol=code,
                screener="turkey",
                exchange="BIST",
                interval=Interval.INTERVAL_1_DAY,
            )
            analysis = handler.get_analysis()
            if not analysis or not analysis.summary:
                return None

            summary = analysis.summary
            indicators = getattr(analysis, "indicators", {}) or {}

            return TechnicalSummaryData(
                recommendation=summary.get("RECOMMENDATION", "NEUTRAL"),
                buy_signals=summary.get("BUY", 0),
                sell_signals=summary.get("SELL", 0),
                neutral_signals=summary.get("NEUTRAL", 0),
                rsi=indicators.get("RSI"),
                macd=indicators.get("MACD.macd"),
                source=self.name,
            )
        except Exception:
            return None

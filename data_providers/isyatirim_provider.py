"""İş Yatırım Temel Finansal Veri Sağlayıcısı (isyatirimhisse)."""

import numpy as np

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


class IsYatirimProvider(BaseDataProvider):
    """İş Yatırım kaynaklı resmi finansal tablo ve rasyo verilerini çeken sağlayıcı."""

    @property
    def name(self) -> str:
        return "IsYatirim"

    def get_price_history(self, ticker: str, period: str = "6mo") -> PriceHistoryData | None:
        """İş Yatırım sağlayıcısı temel analiz odaklıdır, fiyat geçmişi için Yahoo tercih edilir."""
        return None

    def get_fundamental_data(self, stock_code: str, ticker: str) -> FundamentalData | None:
        """İş Yatırım API / kütüphanesi üzerinden temel oranları çeker."""
        try:
            from isyatirimhisse import fetch_financials

            code = stock_code.upper().replace(".IS", "")
            # Finansal tablo verilerini çekmeyi dene
            df = fetch_financials(symbols=[code])
            if df is None or df.empty:
                return None

            # BIST şirketleri için bilanço kalemlerinden oran tahmini veya ekleme yapılabilir
            return FundamentalData(
                source=self.name,
                extra_metrics={"has_financials": True, "rows": len(df)},
            )
        except Exception:
            # Ağ, format veya API kaynaklı hatalarda None dönerek fallback'e bırakır
            return None

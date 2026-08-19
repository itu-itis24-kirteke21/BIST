import json
import os
from unittest.mock import patch

import pandas as pd

from bist_analyzer import analyze_stock, run_analysis


class TestAnalyzeStock:
    """analyze_stock fonksiyonunun birim testleri (Mock Ticker ile)."""

    def test_analyze_stock_success(
        self, sample_stock_meta, sample_history_df, sample_info_positive, mock_ticker_factory
    ):
        """Geçerli veri ile hisse analizinin tüm alanları eksiksiz ürettiğini doğrular."""
        mock_ticker = mock_ticker_factory(sample_history_df, sample_info_positive)

        with patch("yfinance.Ticker", return_value=mock_ticker):
            result = analyze_stock("THYAO.IS", sample_stock_meta)

        assert result is not None
        assert result["code"] == "THYAO"
        assert result["name"] == "Türk Hava Yolları"
        assert result["sector"] == "Havacılık"
        assert isinstance(result["price"], float)
        assert isinstance(result["change"], float)
        assert 0 <= result["technicalScore"] <= 50
        assert 0 <= result["fundamentalScore"] <= 50
        assert 0 <= result["totalScore"] <= 100
        assert result["sentiment"] in ["positive", "neutral", "negative"]
        assert isinstance(result["reasons"], list)
        assert len(result["reasons"]) > 0
        assert isinstance(result["analysis"], str)
        assert len(result["analysis"]) > 0

    def test_analyze_stock_insufficient_history(self, sample_stock_meta, sample_info_positive, mock_ticker_factory):
        """50 günden az geçmiş veri olduğunda analizin None döndürdüğünü doğrular."""
        short_df = pd.DataFrame({"Close": [100.0] * 30, "Volume": [1000] * 30})
        mock_ticker = mock_ticker_factory(short_df, sample_info_positive)

        with patch("yfinance.Ticker", return_value=mock_ticker):
            result = analyze_stock("THYAO.IS", sample_stock_meta)

        assert result is None

    def test_analyze_stock_empty_history(self, sample_stock_meta, sample_info_positive, mock_ticker_factory):
        """Geçmiş veri boş DataFrame olduğunda None döndürdüğünü doğrular."""
        empty_df = pd.DataFrame()
        mock_ticker = mock_ticker_factory(empty_df, sample_info_positive)

        with patch("yfinance.Ticker", return_value=mock_ticker):
            result = analyze_stock("THYAO.IS", sample_stock_meta)

        assert result is None

    def test_analyze_stock_exception_handling(self, sample_stock_meta):
        """yfinance API hatası veya istisna durumunda çökmeden None döndürdüğünü doğrular."""
        with patch("yfinance.Ticker", side_effect=Exception("API connection timeout")):
            result = analyze_stock("THYAO.IS", sample_stock_meta)

        assert result is None

    def test_sentiment_classification(
        self,
        sample_stock_meta,
        sample_history_df,
        sample_prices_downtrend,
        sample_info_positive,
        sample_info_negative,
        mock_ticker_factory,
    ):
        """Farklı skor profillerinde sentiment değerinin doğru atandığını doğrular."""
        # 1. Pozitif senaryo (Yükselen trend + Güçlü temel)
        mock_ticker_pos = mock_ticker_factory(sample_history_df, sample_info_positive)
        with patch("yfinance.Ticker", return_value=mock_ticker_pos):
            res_pos = analyze_stock("THYAO.IS", sample_stock_meta)
        assert res_pos["sentiment"] == "positive"
        assert res_pos["totalScore"] >= 50

        # 2. Negatif senaryo (Düşen trend + Zayıf temel)
        downtrend_df = pd.DataFrame(
            {
                "Open": sample_prices_downtrend * 1.01,
                "High": sample_prices_downtrend * 1.02,
                "Low": sample_prices_downtrend * 0.98,
                "Close": sample_prices_downtrend,
                "Volume": [1000000] * len(sample_prices_downtrend),
            },
            index=pd.date_range(end=pd.Timestamp.now(), periods=len(sample_prices_downtrend), freq="B"),
        )

        mock_ticker_neg = mock_ticker_factory(downtrend_df, sample_info_negative)
        with patch("yfinance.Ticker", return_value=mock_ticker_neg):
            res_neg = analyze_stock("THYAO.IS", sample_stock_meta)
        assert res_neg["sentiment"] in ["negative", "neutral"]
        assert res_neg["totalScore"] < 50


class TestRunAnalysis:
    """run_analysis fonksiyonunun toplu analiz ve JSON çıktısı testleri."""

    def test_run_analysis_creates_json_and_sorts(
        self,
        sample_stocks_dict,
        sample_history_df,
        sample_info_positive,
        sample_info_neutral,
        mock_ticker_factory,
        tmp_path,
    ):
        """Toplu analizin JSON dosyasını oluşturduğunu ve sonuçları skora göre azalan sıraladığını test eder."""
        output_file = tmp_path / "test_bist_results.json"

        def mock_ticker_dispatcher(ticker):
            if "THYAO" in ticker:
                return mock_ticker_factory(sample_history_df, sample_info_positive)
            elif "GARAN" in ticker:
                return mock_ticker_factory(sample_history_df, sample_info_neutral)
            else:
                # Başarısız/Yetersiz veri simülasyonu
                return mock_ticker_factory(pd.DataFrame(), {})

        with patch("yfinance.Ticker", side_effect=mock_ticker_dispatcher), patch("time.sleep", return_value=None):
            results = run_analysis(stock_list=sample_stocks_dict, output_file=str(output_file))

        # 3 hisseden 2'si başarılı, 1'i başarısız olmalı
        assert len(results) == 2
        assert os.path.exists(output_file)

        # Skora göre azalan sıralı olmalı
        scores = [r["totalScore"] for r in results]
        assert scores == sorted(scores, reverse=True)

        # JSON dosya içeriğinin doğrulanması
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["code"] == results[0]["code"]
        assert data[0]["totalScore"] >= data[1]["totalScore"]

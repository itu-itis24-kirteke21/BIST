import json
import os

from bist_analyzer import BIST100_STOCKS


class TestStocksConfiguration:
    """stocks_config.json ve BIST100_STOCKS yapılandırma testleri."""

    def test_stocks_config_file_exists_and_valid_json(self):
        """stocks_config.json dosyasının var ve geçerli JSON olduğunu doğrular."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "stocks_config.json")
        assert os.path.exists(config_path), "stocks_config.json dosyası bulunamadı"

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "stocks" in data
        assert isinstance(data["stocks"], dict)
        assert len(data["stocks"]) > 0

    def test_stocks_config_schema(self):
        """stocks_config.json içindeki tüm hisselerin gerekli alanlara ve formata sahip olduğunu doğrular."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "stocks_config.json")
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        for ticker, meta in data["stocks"].items():
            assert ticker.endswith(".IS"), f"{ticker} Yahoo Finance formatına (.IS) uymuyor"
            assert "code" in meta and isinstance(meta["code"], str) and len(meta["code"]) > 0
            assert "name" in meta and isinstance(meta["name"], str) and len(meta["name"]) > 0
            assert "sector" in meta and isinstance(meta["sector"], str) and len(meta["sector"]) > 0
            assert ticker.startswith(meta["code"]), f"Ticker ({ticker}) kod ({meta['code']}) ile başlamıyor"

    def test_bist100_stocks_dict_in_analyzer(self):
        """bist_analyzer.py içindeki BIST100_STOCKS sözlüğünün geçerliliğini test eder."""
        assert isinstance(BIST100_STOCKS, dict)
        assert len(BIST100_STOCKS) > 0

        for ticker, meta in BIST100_STOCKS.items():
            assert ticker.endswith(".IS")
            assert "code" in meta
            assert "name" in meta
            assert "sector" in meta

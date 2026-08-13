#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST 100 Profesyonel Hisse Analiz Sistemi
==========================================
Yahoo Finance API üzerinden gerçek verileri çekip,
RSI, MACD, EMA, Bollinger Bands gibi teknik göstergeler ve
F/K, ROE, PD/DD gibi temel verilerle skorlama yapan profesyonel sistem.

Kullanım:
    python bist_analyzer.py

Gereksinimler:
    pip install yfinance pandas numpy

Yazar: AI Asistan
Tarih: 2026-08-08
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
import sys

# ============================================
# BIST 100 HİSSE LİSTESİ (Yahoo Finance .IS suffix)
# ============================================
BIST100_STOCKS = {
    'THYAO.IS': {'code': 'THYAO', 'name': 'Türk Hava Yolları', 'sector': 'Havacılık'},
    'GARAN.IS': {'code': 'GARAN', 'name': 'Garanti BBVA', 'sector': 'Bankacılık'},
    'ASELS.IS': {'code': 'ASELS', 'name': 'Aselsan', 'sector': 'Savunma'},
    'KCHOL.IS': {'code': 'KCHOL', 'name': 'Koç Holding', 'sector': 'Holding'},
    'SISE.IS':  {'code': 'SISE',  'name': 'Şişecam', 'sector': 'Cam'},
    'EREGL.IS': {'code': 'EREGL', 'name': 'Ereğli Demir Çelik', 'sector': 'Demir-Çelik'},
    'BIMAS.IS': {'code': 'BIMAS', 'name': 'BİM Mağazalar', 'sector': 'Perakende'},
    'SAHOL.IS': {'code': 'SAHOL', 'name': 'Sabancı Holding', 'sector': 'Holding'},
    'TUPRS.IS': {'code': 'TUPRS', 'name': 'Tüpraş', 'sector': 'Enerji'},
    'KRDMD.IS': {'code': 'KRDMD', 'name': 'Kardemir', 'sector': 'Demir-Çelik'},
    'PGSUS.IS': {'code': 'PGSUS', 'name': 'Pegasus', 'sector': 'Havacılık'},
    'AKBNK.IS': {'code': 'AKBNK', 'name': 'Akbank', 'sector': 'Bankacılık'},
    'YKBNK.IS': {'code': 'YKBNK', 'name': 'Yapı Kredi', 'sector': 'Bankacılık'},
    'ISCTR.IS': {'code': 'ISCTR', 'name': 'İş Bankası', 'sector': 'Bankacılık'},
    'ARCLK.IS': {'code': 'ARCLK', 'name': 'Arçelik', 'sector': 'Beyaz Eşya'},
    'TOASO.IS': {'code': 'TOASO', 'name': 'Tofaş', 'sector': 'Otomotiv'},
    'FROTO.IS': {'code': 'FROTO', 'name': 'Ford Otosan', 'sector': 'Otomotiv'},
    'KOZAA.IS': {'code': 'KOZAA', 'name': 'Koza Altın', 'sector': 'Madencilik'},
    'PETKM.IS': {'code': 'PETKM', 'name': 'Petkim', 'sector': 'Petrokimya'},
    'TCELL.IS': {'code': 'TCELL', 'name': 'Turkcell', 'sector': 'Telekom'},
    'HEKTS.IS': {'code': 'HEKTS', 'name': 'Hektaş', 'sector': 'Kimya'},
    'KONTR.IS': {'code': 'KONTR', 'name': 'Kontrolmatik', 'sector': 'Teknoloji'},
    'MAVI.IS':  {'code': 'MAVI',  'name': 'Mavi Giyim', 'sector': 'Tekstil'},
    'SOKM.IS':  {'code': 'SOKM',  'name': 'Şok Marketler', 'sector': 'Perakende'},
    'ALARK.IS': {'code': 'ALARK', 'name': 'Alarko Holding', 'sector': 'Holding'},
    'DOHOL.IS': {'code': 'DOHOL', 'name': 'Doğan Holding', 'sector': 'Holding'},
    'ENKAI.IS': {'code': 'ENKAI', 'name': 'Enka İnşaat', 'sector': 'İnşaat'},
    'TAVHL.IS': {'code': 'TAVHL', 'name': 'TAV Havalimanları', 'sector': 'Havacılık'},
    'VESTL.IS': {'code': 'VESTL', 'name': 'Vestel', 'sector': 'Elektronik'},
    'KZBGY.IS': {'code': 'KZBGY', 'name': 'Kuzu Grup', 'sector': 'İnşaat'},
}

# ============================================
# TEKNİK GÖSTERGE HESAPLAMA FONKSİYONLARI
# ============================================

def calculate_rsi(prices, period=14):
    """RSI (Relative Strength Index) hesaplama"""
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.convolve(gain, np.ones(period)/period, mode='valid')
    avg_loss = np.convolve(loss, np.ones(period)/period, mode='valid')
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1] if len(rsi) > 0 else 50

def calculate_macd(prices):
    """MACD (Moving Average Convergence Divergence) hesaplama"""
    ema12 = pd.Series(prices).ewm(span=12, adjust=False).mean()
    ema26 = pd.Series(prices).ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line.iloc[-1], signal_line.iloc[-1], macd_hist.iloc[-1]

def calculate_ema(prices, span):
    """EMA (Exponential Moving Average) hesaplama"""
    return pd.Series(prices).ewm(span=span, adjust=False).mean().iloc[-1]

def calculate_bollinger(prices, period=20, std_dev=2):
    """Bollinger Bands hesaplama"""
    sma = pd.Series(prices).rolling(period).mean().iloc[-1]
    std = pd.Series(prices).rolling(period).std().iloc[-1]
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    current = prices[-1]
    position = (current - lower) / (upper - lower + 1e-10)
    return upper, lower, position

# ============================================
# SKORLAMA MOTORU
# ============================================

def calculate_technical_score(rsi, macd, macd_hist, price, ema20, ema50, vol_ratio, daily_change, bb_position):
    """Teknik analiz skoru (0-50)"""
    score = 0

    # RSI (0-12)
    if 50 <= rsi <= 70:
        score += 12
    elif 40 <= rsi < 50:
        score += 10
    elif 70 < rsi <= 80:
        score += 8
    elif 30 <= rsi < 40:
        score += 7
    elif rsi > 80:
        score += 4
    else:
        score += 5

    # MACD (0-12)
    if macd_hist > 0 and macd > 0:
        score += 12
    elif macd_hist > 0:
        score += 9
    elif macd_hist < 0 and macd < 0:
        score += 3
    else:
        score += 6

    # EMA Trend (0-10)
    if price > ema20 and ema20 > ema50:
        score += 10
    elif price > ema20 and price > ema50:
        score += 8
    elif price > ema50:
        score += 6
    elif price > ema20:
        score += 5
    else:
        score += 3

    # Volume (0-8)
    if vol_ratio > 1.2 and daily_change > 0:
        score += 8
    elif vol_ratio > 1.0 and daily_change > 0:
        score += 6
    elif vol_ratio > 1.2 and daily_change < 0:
        score += 4
    elif vol_ratio > 0.8:
        score += 5
    else:
        score += 3

    # Bollinger (0-8)
    if 0.6 < bb_position < 0.95:
        score += 8
    elif bb_position > 0.4:
        score += 6
    elif bb_position > 0.2:
        score += 5
    else:
        score += 3

    return score

def calculate_fundamental_score(pe, pb, beta, profit_margin, roe, debt_equity, rec_mean):
    """Temel analiz skoru (0-50)"""
    score = 0

    # P/E (0-10)
    if 0 < pe <= 8:
        score += 10
    elif 8 < pe <= 15:
        score += 9
    elif 15 < pe <= 25:
        score += 7
    elif 25 < pe <= 40:
        score += 5
    elif pe > 40:
        score += 3
    else:
        score += 4

    # P/B (0-8)
    if 0 < pb <= 1.5:
        score += 8
    elif 1.5 < pb <= 3:
        score += 7
    elif 3 < pb <= 5:
        score += 5
    elif 5 < pb <= 10:
        score += 4
    elif pb > 10:
        score += 2
    else:
        score += 4

    # Beta (0-6)
    if 0.8 <= beta <= 1.2:
        score += 6
    elif 0.5 <= beta < 0.8 or 1.2 < beta <= 1.5:
        score += 5
    else:
        score += 4

    # Profit Margin (0-8)
    if profit_margin >= 20:
        score += 8
    elif profit_margin >= 10:
        score += 7
    elif profit_margin >= 5:
        score += 6
    elif profit_margin >= 2:
        score += 5
    elif profit_margin > 0:
        score += 4
    else:
        score += 2

    # ROE (0-8)
    if roe >= 20:
        score += 8
    elif roe >= 15:
        score += 7
    elif roe >= 10:
        score += 6
    elif roe >= 5:
        score += 5
    elif roe > 0:
        score += 4
    else:
        score += 2

    # Debt/Equity (0-6)
    if 0 <= debt_equity <= 30:
        score += 6
    elif 30 < debt_equity <= 60:
        score += 5
    elif 60 < debt_equity <= 100:
        score += 4
    elif 100 < debt_equity <= 150:
        score += 3
    else:
        score += 2

    # Analyst recommendation (0-4)
    if rec_mean <= 1.5:
        score += 4
    elif rec_mean <= 2.0:
        score += 3
    elif rec_mean <= 2.5:
        score += 2
    elif rec_mean <= 3.5:
        score += 1

    return score

def safe_float(val, default=0):
    """Güvenli float dönüşümü"""
    try:
        v = float(val)
        return v if not (np.isnan(v) or np.isinf(v)) else default
    except:
        return default

def generate_reasons(stock_data):
    """Analiz nedenlerini oluştur"""
    reasons = []
    s = stock_data

    # RSI
    if s['rsi'] > 70:
        reasons.append(f"⚠️ RSI {s['rsi']:.1f} aşırı alım bölgesinde, düzeltme riski var")
    elif s['rsi'] < 30:
        reasons.append(f"✅ RSI {s['rsi']:.1f} aşırı satım bölgesinde, dönüş potansiyeli yüksek")
    elif 50 <= s['rsi'] <= 70:
        reasons.append(f"✅ RSI {s['rsi']:.1f} güçlü momentum bölgesinde")
    else:
        reasons.append(f"⚪ RSI {s['rsi']:.1f} nötr bölgede")

    # MACD
    if s['macd_hist'] > 0 and s['macd'] > 0:
        reasons.append("✅ MACD pozitif bölgede ve histogram artıyor — güçlü alım sinyali")
    elif s['macd_hist'] > 0:
        reasons.append("✅ MACD histogram pozitif — yukarı momentum devam ediyor")
    elif s['macd_hist'] < 0 and s['macd'] < 0:
        reasons.append("❌ MACD negatif bölgede — satış baskısı devam ediyor")
    else:
        reasons.append("⚪ MACD kararsız bölgede — yön belirsizliği")

    # EMA
    if s['price'] > s['ema20'] and s['ema20'] > s['ema50']:
        reasons.append("✅ Fiyat EMA 20 ve EMA 50'nin üzerinde — güçlü yükseliş trendi")
    elif s['price'] > s['ema50']:
        reasons.append("⚪ Fiyat EMA 50'nin üzerinde ancak EMA 20'nin altında")
    else:
        reasons.append("❌ Fiyat EMA 50'nin altında — düşüş trendi sinyali")

    # Volume
    if s['vol_ratio'] > 1.2 and s['change'] > 0:
        reasons.append(f"✅ Hacim {s['vol_ratio']:.1f}x ortalamanın üzerinde, alım baskısı güçlü")
    elif s['vol_ratio'] > 1.2 and s['change'] < 0:
        reasons.append(f"❌ Hacim {s['vol_ratio']:.1f}x ortalamanın üzerinde ancak fiyat düşüyor — satış baskısı")
    else:
        reasons.append(f"⚪ Hacim normal seviyelerde ({s['vol_ratio']:.1f}x ortalama)")

    # Fundamental
    if isinstance(s['pe'], (int, float)) and s['pe'] > 0 and s['pe'] <= 15:
        reasons.append(f"✅ F/K oranı {s['pe']:.1f} — değerlemesi makul/ucuz")
    elif isinstance(s['pe'], (int, float)) and s['pe'] > 40:
        reasons.append(f"⚠️ F/K oranı {s['pe']:.1f} — yüksek değerleme")

    if s['roe'] >= 15:
        reasons.append(f"✅ Özsermaye kârlılığı (ROE) %{s['roe']:.1f} — güçlü")
    elif s['roe'] < 5:
        reasons.append(f"⚠️ Özsermaye kârlılığı (ROE) %{s['roe']:.1f} — zayıf")

    if s['debt_equity'] > 100:
        reasons.append(f"⚠️ Borç/Özsermaye oranı {s['debt_equity']:.1f} — yüksek kaldıraç")
    elif s['debt_equity'] < 50:
        reasons.append(f"✅ Borç/Özsermaye oranı {s['debt_equity']:.1f} — sağlam bilanço")

    if s['rec_mean'] <= 2.0:
        reasons.append(f"✅ Analist ortalama tavsiyesi: Güçlü Al ({s['rec_mean']:.1f})")
    elif s['rec_mean'] >= 3.5:
        reasons.append(f"⚠️ Analist ortalama tavsiyesi: Zayıf ({s['rec_mean']:.1f})")

    return reasons

def generate_analysis(stock_data):
    """Yapay zeka analiz metni oluştur"""
    s = stock_data

    if s['totalScore'] >= 75:
        text = f"{s['name']} ({s['code']}) hem teknik hem temel göstergeler açısından güçlü bir görünüm sergiliyor. "
    elif s['totalScore'] >= 60:
        text = f"{s['name']} ({s['code']}) genel olarak olumlu sinyaller veriyor ancak bazı risk faktörleri mevcut. "
    elif s['totalScore'] >= 45:
        text = f"{s['name']} ({s['code']}) karışık sinyaller veriyor, hem olumlu hem olumsuz faktörler bulunuyor. "
    else:
        text = f"{s['name']} ({s['code']}) zayıf sinyaller veriyor, dikkatli olunması önerilir. "

    if s['rsi'] >= 50 and s['rsi'] <= 70:
        text += f"RSI {s['rsi']:.1f} seviyesiyle hisse güçlü momentum bölgesinde. "
    elif s['rsi'] < 30:
        text += f"RSI {s['rsi']:.1f} aşırı satım bölgesinde olup dönüş potansiyeli taşıyor. "
    elif s['rsi'] > 70:
        text += f"RSI {s['rsi']:.1f} aşırı alım bölgesinde, kâr realizasyonu riski var. "

    if s['macd_hist'] > 0:
        text += "MACD histogram pozitif olup yukarı yönlü momentum devam ediyor. "
    else:
        text += "MACD negatif bölgede olup satış baskısı gözlemleniyor. "

    if s['price'] > s['ema50']:
        text += "Fiyat EMA 50'nin üzerinde seyrediyor. "
    else:
        text += "Fiyat EMA 50'nin altında, orta vadeli düşüş trendi söz konusu. "

    if isinstance(s['pe'], (int, float)) and s['pe'] > 0 and s['pe'] <= 15:
        text += f"F/K oranı {s['pe']:.1f} ile değerlemesi makul seviyelerde. "
    elif isinstance(s['pe'], (int, float)) and s['pe'] > 40:
        text += f"F/K oranı {s['pe']:.1f} ile yüksek değerlemeye sahip. "

    if s['roe'] >= 15:
        text += f"ROE %{s['roe']:.1f} ile şirket kârlılığı güçlü. "
    elif s['roe'] < 5:
        text += f"ROE %{s['roe']:.1f} ile kârlılık zayıf seyrediyor. "

    if s['debt_equity'] > 100:
        text += f"Borç/Özsermaye oranı {s['debt_equity']:.1f} ile yüksek kaldıraç dikkat çekiyor. "

    text += f"Analistlerin ortalama tavsiyesi {s['rec_mean']:.1f} seviyesinde. 52 haftalık aralıkta %{s['range_position']:.1f} pozisyonunda."

    return text

# ============================================
# ANA ANALİZ FONKSİYONU
# ============================================

def analyze_stock(ticker, meta, period="6mo"):
    """Tek bir hisseyi analiz et"""
    try:
        print(f"  📊 {meta['code']} analiz ediliyor...", end=" ")

        # Veri çek
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info

        if hist.empty or len(hist) < 50:
            print("❌ Yetersiz veri")
            return None

        close = hist['Close'].values
        volume = hist['Volume'].values

        # Teknik göstergeler
        rsi = calculate_rsi(close)
        macd, macd_signal, macd_hist = calculate_macd(close)
        ema20 = calculate_ema(close, 20)
        ema50 = calculate_ema(close, 50)
        bb_upper, bb_lower, bb_position = calculate_bollinger(close)

        vol_10d = np.mean(volume[-10:])
        vol_ratio = volume[-1] / (vol_10d + 1e-10)
        daily_change = (close[-1] - close[-2]) / close[-2] * 100

        wk_low = info.get('fiftyTwoWeekLow', close[-1])
        wk_high = info.get('fiftyTwoWeekHigh', close[-1])
        range_position = (close[-1] - wk_low) / (wk_high - wk_low + 1e-10) * 100

        # Temel veriler
        pe = safe_float(info.get('trailingPE', 0))
        pb = safe_float(info.get('priceToBook', 0))
        beta = safe_float(info.get('beta', 1))
        profit_margin = safe_float(info.get('profitMargins', 0)) * 100
        roe = safe_float(info.get('returnOnEquity', 0)) * 100
        debt_equity = safe_float(info.get('debtToEquity', 0))
        rec_mean = safe_float(info.get('recommendationMean', 3))

        # Skorlama
        tech_score = calculate_technical_score(rsi, macd, macd_hist, close[-1], ema20, ema50, vol_ratio, daily_change, bb_position)
        fund_score = calculate_fundamental_score(pe, pb, beta, profit_margin, roe, debt_equity, rec_mean)
        total_score = tech_score + fund_score

        # Sentiment
        if total_score >= 70:
            sentiment = 'positive'
        elif total_score >= 50:
            sentiment = 'positive'
        elif total_score >= 35:
            sentiment = 'neutral'
        else:
            sentiment = 'negative'

        result = {
            'code': meta['code'],
            'name': meta['name'],
            'sector': meta['sector'],
            'price': round(float(close[-1]), 2),
            'change': round(daily_change, 2),
            'technicalScore': tech_score,
            'fundamentalScore': fund_score,
            'totalScore': total_score,
            'sentiment': sentiment,
            'rsi': round(rsi, 1),
            'macd': round(macd, 3),
            'macd_signal': round(macd_signal, 3),
            'macd_hist': round(macd_hist, 3),
            'ema20': round(ema20, 2),
            'ema50': round(ema50, 2),
            'bb_position': round(bb_position, 2),
            'vol_ratio': round(vol_ratio, 2),
            'range_position': round(range_position, 1),
            'pe': round(pe, 2) if pe > 0 else 'N/A',
            'pb': round(pb, 2) if pb > 0 else 'N/A',
            'beta': round(beta, 2),
            'profit_margin': round(profit_margin, 2),
            'roe': round(roe, 2),
            'debt_equity': round(debt_equity, 2),
            'rec_mean': round(rec_mean, 2),
            'wk_low': round(wk_low, 2),
            'wk_high': round(wk_high, 2),
        }

        result['reasons'] = generate_reasons(result)
        result['analysis'] = generate_analysis(result)

        print(f"✅ Skor: {total_score}")
        return result

    except Exception as e:
        print(f"❌ Hata: {str(e)[:50]}")
        return None

def run_analysis(stock_list=None, output_file="bist_analysis_results.json"):
    """Tüm hisseleri analiz et ve sonuçları kaydet"""
    if stock_list is None:
        stock_list = BIST100_STOCKS

    print("=" * 70)
    print("BIST 100 PROFESYONEL ANALİZ SİSTEMİ")
    print("=" * 70)
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Analiz edilecek hisse sayısı: {len(stock_list)}")
    print("-" * 70)

    results = []
    failed = []

    for i, (ticker, meta) in enumerate(stock_list.items(), 1):
        print(f"[{i}/{len(stock_list)}]", end="")
        result = analyze_stock(ticker, meta)
        if result:
            results.append(result)
        else:
            failed.append(meta['code'])
        time.sleep(0.5)  # Rate limit koruması

    # Skora göre sırala
    results.sort(key=lambda x: x['totalScore'], reverse=True)

    # JSON olarak kaydet
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Özet rapor
    print("
" + "=" * 70)
    print("ANALİZ TAMAMLANDI")
    print("=" * 70)
    print(f"Başarılı: {len(results)} | Başarısız: {len(failed)}")
    if failed:
        print(f"Başarısız hisseler: {', '.join(failed)}")

    print(f"
{'Hisse':<8} {'Fiyat':>10} {'Değ.':>7} {'Teknik':>7} {'Temel':>7} {'Toplam':>7} {'Durum':<10}")
    print("-" * 70)
    for r in results:
        status = "🟢 OLUMLU" if r['sentiment'] == 'positive' else "🔴 OLUMSUZ" if r['sentiment'] == 'negative' else "⚪ NÖTR"
        print(f"{r['code']:<8} {r['price']:>10.2f} {r['change']:>+6.1f}% {r['technicalScore']:>7} {r['fundamentalScore']:>7} {r['totalScore']:>7} {status:<10}")

    print(f"
📁 Sonuçlar kaydedildi: {output_file}")
    return results

# ============================================
# ÇALIŞTIRMA
# ============================================

if __name__ == "__main__":
    # Tüm listeyi analiz et
    results = run_analysis()

    # VEYA sadece belirli hisseleri analiz et:
    # selected = {k: v for k, v in BIST100_STOCKS.items() if v['code'] in ['THYAO', 'GARAN']}
    # results = run_analysis(selected)

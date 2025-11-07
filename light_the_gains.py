"""
💡 LightTheGains — Real-time Portfolio Mood Light
------------------------------------------------
Tracks your stock portfolio performance and uses
a Tuya smart bulb to visualize your portfolio mood:
   🟢 Green → Gain
   🔴 Red   → Loss
   ⚪ White → Neutral
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf
import tinytuya
from dotenv import load_dotenv

PORTFOLIO_FILE = "portfolio.json"
REFRESH_INTERVAL = 600  # seconds (10 minutes)
AUTO_APPEND_NS = True

# Terminal colors
GREEN = "\033[92m"
RED = "\033[91m"
GRAY = "\033[90m"
RESET = "\033[0m"

load_dotenv()
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")
DEVICE_IP = os.getenv("TUYA_DEVICE_IP")
LOCAL_KEY = os.getenv("TUYA_LOCAL_KEY")

if not all([DEVICE_ID, DEVICE_IP, LOCAL_KEY]):
    raise SystemExit("❌ Missing Tuya environment variables in .env")

def init_bulb() -> tinytuya.BulbDevice:
    """Initialize and return the Tuya bulb device."""
    bulb = tinytuya.BulbDevice(DEVICE_ID, DEVICE_IP, LOCAL_KEY)
    bulb.set_version(3.5)
    return bulb

def set_bulb_color(bulb: tinytuya.BulbDevice, change_pct: Optional[float]) -> None:
    """Change bulb color based on portfolio performance."""
    if change_pct is None:
        return

    try:
        bulb.turn_on()
        if change_pct > 0.3:
            bulb.set_colour(0, 255, 0)  # Green
            print("💡 Bulb → GREEN (Gain)")
        elif change_pct < -0.3:
            bulb.set_colour(255, 0, 0)  # Red
            print("💡 Bulb → RED (Loss)")
        else:
            bulb.set_white()
            print("💡 Bulb → WHITE (Neutral)")
    except Exception as e:
        print(f"⚠️ Bulb control failed: {e}")


def clear_console() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def load_portfolio(path: Path) -> pd.DataFrame:
    """Load portfolio data from JSON file."""
    if path.suffix.lower() != ".json":
        raise ValueError("Only .json files are supported for the portfolio.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except Exception as e:
        raise ValueError(f"Failed to read JSON portfolio: {e}")

    required = {"symbol", "qty", "buy_price"}
    if not required.issubset(df.columns):
        raise ValueError(f"Portfolio JSON must contain keys: {required}")

    return df


def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol for Yahoo Finance."""
    s = symbol.strip().upper()
    if AUTO_APPEND_NS and not s.endswith(".NS"):
        s += ".NS"
    return s.replace("&", "%26")


def fetch_yfinance_price(symbol: str) -> tuple[Optional[float], Optional[float]]:
    """Fetch live price and 1D return for a given stock."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        last_price = info.get("last_price")
        prev_close = info.get("previous_close")

        if not prev_close or not last_price or prev_close == 0:
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_price = hist["Close"].iloc[-1]
            elif len(hist) == 1:
                last_price = hist["Close"].iloc[-1]

        if not prev_close or prev_close == 0:
            prev_close = ticker.info.get("previousClose")

        one_day_return = (
            ((last_price - prev_close) / prev_close) * 100
            if last_price and prev_close else None
        )

        return (
            float(last_price) if last_price else None,
            round(one_day_return, 2) if one_day_return else None,
        )

    except Exception as e:
        print(f"⚠️ Failed to fetch {symbol}: {e}")
        return None, None


def fetch_live_prices(symbols: list[str]) -> tuple[dict, dict]:
    """Fetch prices and 1-day returns for all tickers."""
    prices, returns = {}, {}
    for sym in symbols:
        price, daily_ret = fetch_yfinance_price(sym)
        prices[sym] = price
        returns[sym] = daily_ret
    return prices, returns


def compute_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """Compute P/L, returns, and values for the portfolio."""
    df = df.copy()
    df["symbol_norm"] = df["symbol"].apply(normalize_symbol)

    print("\n📡 Fetching live prices...")
    price_map, ret_map = fetch_live_prices(df["symbol_norm"].tolist())

    df["current_price"] = df["symbol_norm"].map(price_map)
    df["1d_return_pct"] = df["symbol_norm"].map(ret_map)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0)
    df["buy_price"] = pd.to_numeric(df["buy_price"], errors="coerce").fillna(0.0)

    df["invested"] = df["qty"] * df["buy_price"]
    df["current_value"] = df["qty"] * df["current_price"]
    df["profit_loss"] = df["current_value"] - df["invested"]
    df["return_pct"] = df.apply(
        lambda r: (r["profit_loss"] / r["invested"] * 100) if r["invested"] else None,
        axis=1,
    )

    return df.round(2)

def colorize(value: float, suffix: str = "%") -> str:
    """Return a colorized string based on value."""
    if pd.isna(value):
        return f"{GRAY}{'—':>6}{RESET}"
    color = GREEN if value > 0 else RED if value < 0 else GRAY
    return f"{color}{value:>6.2f}{suffix}{RESET}"

def print_summary(df: pd.DataFrame) -> Optional[float]:
    """Display portfolio summary and return 1D overall change."""
    total_invested = df["invested"].sum()
    total_current = df["current_value"].sum()
    total_pnl = total_current - total_invested
    total_return_pct = (total_pnl / total_invested * 100) if total_invested else None

    valid_1d = df.dropna(subset=["1d_return_pct", "current_value"])
    overall_1d_change = (
        (valid_1d["1d_return_pct"] * valid_1d["current_value"]).sum()
        / valid_1d["current_value"].sum()
        if not valid_1d.empty else None
    )

    print("\n💼 --- Portfolio Summary ---")
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Invested: ₹{total_invested:,.2f}")
    print(f"Current Value: ₹{total_current:,.2f}")
    print(f"Unrealized P/L: ₹{total_pnl:,.2f}")
    print(f"Total Return: {colorize(total_return_pct)}")
    print(f"Overall 1D Change: {colorize(overall_1d_change)}")

    print("\n📈 Holdings Overview:")
    print(f"{'Symbol':<12} {'Qty':>5} {'Buy':>10} {'Current':>10} {'P/L':>10} {'Ret%':>8} {'1D%':>8}")
    print("-" * 68)
    for _, row in df.iterrows():
        print(
            f"{row['symbol']:<12} "
            f"{int(row['qty']):>5} "
            f"{row['buy_price']:>10.2f} "
            f"{row['current_price']:>10.2f} "
            f"{colorize(row['profit_loss'], ''):>10} "
            f"{colorize(row['return_pct']):>8} "
            f"{colorize(row['1d_return_pct']):>8}"
        )

    return overall_1d_change

def main() -> None:
    """Run LightTheGains main loop."""
    path = Path(PORTFOLIO_FILE)
    if not path.exists():
        raise SystemExit(f"Portfolio file not found: {path}")

    bulb = init_bulb()
    df_port = load_portfolio(path)

    try:
        while True:
            clear_console()
            df_result = compute_portfolio(df_port)
            one_d_change = print_summary(df_result)
            set_bulb_color(bulb, one_d_change)
            print(f"\n🔁 Refreshing in {REFRESH_INTERVAL} seconds... (Ctrl+C to exit)")
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print("\n👋 Exiting LightTheGains.")
        bulb.turn_off()


if __name__ == "__main__":
    main()

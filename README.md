# 🚀 Roostoo Trading Bot

A modular cryptocurrency trading bot built with Python, implementing a Moving Average (MA) crossover strategy with integrated risk management and live API interaction.

---

## 📌 Overview

This project is a fully functional algorithmic trading system designed to:

* Fetch real-time market data via the Roostoo API
* Generate trading signals using a Moving Average crossover strategy
* Apply strict risk management rules (drawdown, position sizing)
* Execute trades in a continuous automated loop

The architecture is modular, allowing easy extension to new strategies and trading logic.

---

## ⚙️ Features

* 📈 **MA Crossover Strategy**

  * Configurable short and long windows
  * Multi-asset support (BTC, ETH, SOL)

* 🛡️ **Risk Management System**

  * Maximum daily drawdown control
  * Risk per trade limits
  * Position sizing constraints
  * Capital tracking

* 🔌 **API Integration**

  * Account balance retrieval
  * Market data access (ticker, exchange info)

* 🔁 **Automated Trading Loop**

  * Continuous execution
  * Signal generation → execution → wait cycle

* 🧾 **Logging System**

  * File + console logging
  * Timestamped execution logs

---

## 🏗️ Project Structure

```text
config/        → environment variables & trading configuration
src/
  ├── core/    → API client
  ├── strategies/ → MA crossover strategy
  ├── risk/    → risk management logic
scripts/       → entry point (main bot runner)
tests/         → debugging & testing scripts
```

---

## ⚙️ Configuration

Environment variables are defined in:

```bash
config/.env
```

Example:

```bash
ROOSTOO_API_KEY=your_api_key
ROOSTOO_API_SECRET=your_api_secret
INITIAL_CAPITAL=1000000
MAX_DAILY_DRAWDOWN=0.05
RISK_PER_TRADE=0.02
```

⚠️ Never commit real API keys.

---

## 🚀 Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Bot

```bash
python scripts/main.py
```

---

## 📊 Strategy Logic

**Moving Average Crossover**

* Buy → short MA crosses above long MA
* Sell → short MA crosses below long MA

Runs on multiple symbols:

* BTC/USD
* ETH/USD
* SOL/USD

---

## 🧠 How It Works (Flow)

1. Load configuration from `.env`
2. Initialize risk manager & strategy
3. Fetch account balance
4. Enter trading loop:

   * Check drawdown limits
   * Generate signals
   * Execute signals (placeholder)
   * Wait 60 seconds
5. Repeat

---

## 🧪 Testing

Debug and testing scripts are located in:

```bash
tests/
```

---

## 📈 Future Improvements

* Backtesting engine
* Portfolio performance tracking
* Advanced strategies (RSI, MACD, ML-based)
* Web dashboard / UI
* Deployment (cloud / VPS)

---



# 💡 LightTheGains

> _"Let your gains light up the room."_  
> **LightTheGains** is a Python-based portfolio tracker that connects your stock performance to your Tuya Wi-Fi light bulb — making your portfolio literally glow green (or red 😅).

---

## ✨ Features

- 📊 Tracks your portfolio from a simple JSON file  
- ⚡ Fetches live prices using [Yahoo Finance](https://pypi.org/project/yfinance/)  
- 💹 Calculates:
  - Unrealized Profit / Loss  
  - Total Return %  
  - Weighted 1-Day Change %  
- 💡 Syncs your Tuya smart bulb color with your portfolio mood  
  - 🟢 Green → Portfolio Gain  
  - 🔴 Red → Portfolio Loss  
  - ⚪ White → Flat Day  
- 🔁 Auto-refreshes every 10 minutes  

---

## ⚙️ Setup Guide

### 1️⃣ Clone the repository

```bash
git clone https://github.com/AviSharmaaa/light_the_gains.git

cd LightTheGains
````

### 2️⃣ Create a virtual environment

```bash
python3 -m venv venv

source venv/bin/activate   # macOS / Linux

venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure your Tuya device

Create a `.env` file in the project root:

```bash
TUYA_DEVICE_ID=your_device_id_here
TUYA_DEVICE_IP=your_device_ip_here
TUYA_LOCAL_KEY=your_local_key_here
```

### 5️⃣ Add your portfolio data

Copy and edit the sample JSON:

```bash
cp portfolio.sample.json portfolio.json
```

Example structure:

```json
[
  { "symbol": "TCS", "qty": 10, "buy_price": 3580 },
  { "symbol": "INFY", "qty": 15, "buy_price": 1450 },
  { "symbol": "HDFCBANK", "qty": 12, "buy_price": 1550 }
]
```

### 6️⃣ Run the app

```bash
python3 light_the_gains.py
```

---

## 🧾 Example Output

```
📡 Fetching live prices...

💼 --- Portfolio Summary ---
Date/Time: 2025-11-06 15:48:16
Total Invested: ₹25,000.00
Current Value: ₹28,200.00
Unrealized P/L: ₹3,200.00
Total Return: +12.8%
Overall 1D Change: +0.45%

💡 Bulb → GREEN (Gain)
🔁 Refreshing in 600 seconds... (Ctrl+C to exit)
```

---

## 🧠 How It Works

* Uses **Yahoo Finance** (`yfinance`) to fetch live stock prices
* Computes portfolio-level metrics with **pandas**
* Controls your **Tuya smart bulb** via [`tinytuya`](https://pypi.org/project/tinytuya/)
* Refreshes automatically every 10 minutes and updates bulb color accordingly

---

## 🤝 Contributing

Pull requests are welcome!
If you’ve got creative ideas — like connecting to other smart home devices — open an issue 💬

---

## 🛡️ License

This project is licensed under the Apache License - see the [`LICENSE`](LICENSE) file for details.

### 👤 Avi Sharma

- Twitter: [@avisharma_exe](https://twitter.com/avisharmaaaa)
- Github: [@AviSharmaaa](https://github.com/AviSharmaaa)
- Medium: [@AviSharma.exe](https://medium.com/@AviSharma.exe)

## 🙏 Support

This project needs a ⭐️ from you. Don't forget to leave a star ⭐️

---

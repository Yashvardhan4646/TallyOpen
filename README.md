# 📒 OpenSource TallyWeb

A simple, open-source web-based accounting app for small businesses and shopkeepers.
Built with Flask + MySQL. No jargon — designed so anyone can use it.

---

## ⚙️ Setup (First Time Only)

### 1. Install Python packages
```bash
pip install -r requirements.txt
```

### 2. Set up MySQL
- Create a database (e.g. `tallyopen`)
- The app will auto-create all tables on first run

### 3. Create your `keys.json`
Copy the example file and fill in your own details:
```bash
cp keys.example.json keys.json
```

Edit `keys.json`:
```json
{
  "db": {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "tallyopen"
  }
}
```

> ⚠️ `keys.json` is in `.gitignore` — it will NEVER be committed to git.

### 4. Run the app
```bash
python app.py
```

Open your browser at **http://localhost:5000**

Default login: `admin` / `admin123` (change this immediately in Settings → Password)

---

## 🔑 API Keys (Optional Features)

Go to **Settings → API Keys & Email Setup** to configure:

| Feature | Where to get the key |
|---|---|
| Send bills by email | Gmail — create an App Password at myaccount.google.com |
| AI Assistant (Ask AI) | Free at aistudio.google.com/apikey |
| Scan bills/receipts | Free at ocr.space/ocrapi |

All keys are stored in YOUR database only — never in code.

---

## 🔒 Security Note

- `keys.json` → contains your DB password (never committed)
- API keys → stored in your MySQL database (only you can access)
- No personal data is in any committed file

---

## 📋 Features

- 🏠 **Dashboard** — Quick overview of your business health
- 👤 **Accounts & People** — Track customers, suppliers, and bank accounts
- 📦 **Stock / Inventory** — Manage your products and prices
- 💰 **Money Entries** — Record every payment, sale, and purchase
- 🧾 **Create a Bill** — Generate professional PDF invoices
- 📊 **Reports** — View your Profit, Business Value, and Trends
- 🤖 **AI Assistant** — Ask questions about your business in plain language
- 📷 **Bill Scanner** — Scan paper bills with your camera

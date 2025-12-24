# Trendyol PDP Scraper (AE)

This project extracts Product Detail Page (PDP) information from **Trendyol**
for **United Arab Emirates (AE)**  marketplaces.

---

## 📌 Features
- Scrapes PDP HTML using Playwright
- Extracts clean product data using regex
- Handles missing fields gracefully
- Removes duplicate variants and duplicate products
- Outputs clean JSON

---

## 📦 Extracted Fields
- product_title
- brand
- review
- rating
- category_path
- variants
- msrp
- price
- seller_name

---

## 🛠️ Requirements
- Python 3.9+
- Playwright

---

## 🚀 Installation
```bash
pip install -r requirements.txt
playwright install

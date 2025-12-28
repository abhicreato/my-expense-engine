# 🛡️ Sovereign Expense Engine

> ### 🛑 READ THIS FIRST (The "Reality Check" Warning)
> 
> 
> **Viewer Discretion is Advised:** This tool is 100% secure, but the results are not for the faint of heart. Running this "Sync" may cause side effects including, but not limited to:
> * Immediate regret over your "Midnight Biryani" habits.
> * Physical shock upon seeing your lifetime contribution to the Uber CEO's vacation fund.
> * Spontaneous vows to start cooking at home (which usually last 48 hours).
> 
> 
> **Use at your own risk.** The author is not responsible for any existential crises caused by your yearly Zomato/Swiggy totals. Self-realization can be expensive.

---

## 🏗️ What is this?

A privacy-first, local-only financial intelligence tool designed to break the **"Walled Gardens"** of modern service providers. Extract and visualize your spending patterns across **Uber, Swiggy, and Zomato** without ever uploading your data to a third-party server.

---

## ⚠️ Disclaimer & License

### **Commercial Use**

**Strictly Prohibited.** This software is licensed under the **PolyForm Noncommercial License 1.0.0**. You may use this for personal, educational, and non-business purposes only.

### **Security**

This tool is **Local-First**. Your data and your Gmail App Password never leave your machine. The "Sync" happens in-memory on your local CPU and saves to a local file.

---

## 🛠️ Prerequisites

* **Python 3.9+**
* **Pip** (Python package manager)

---

## 🚀 Setup & Installation

### 1. Get a Gmail App Password

To allow the engine to read your receipts securely without using your main password:

1. Go to your **Google Account Management**.
2. Navigate to **Security**.
3. Search for **"App Passwords"** (Note: You must have 2-Factor Authentication enabled).
4. Create a new app called **"Expense Engine."**
5. Copy the **16-character code** generated.

### 2. Install Requirements

Open your terminal in the project folder and run:

```bash
pip install -r requirements.txt

```

### 3. Configure Secrets

Create a file named `.env` in the root folder and add your credentials:

```env
EMAIL_USER=yourname@gmail.com
EMAIL_PASS=xxxx xxxx xxxx xxxx  # Paste your 16-character App Password here

```

---

## 📊 How to Run

To launch the dashboard and start your data recovery, use the following command:

```bash
streamlit run dashboard.py

```

---

## ✨ Features

* **Zero-Cloud Architecture:** Your data stays in a local `expenses.db` (SQLite) file.
* **Smart Sync:** Engineered logic to only fetch *new* receipts since the last check.
* **AI-Optimized Parsing:** Built with **Gemini 1.5 Pro** to handle high-entropy HTML receipts and messy email formats from major vendors.
* **Privacy Mode:** A native toggle to mask actual amounts while keeping the trend "shapes" visible.

---

## 🛠️ Extending the Engine (Add New Services)

This project uses a **Factory Pattern** to make adding new services (like Amazon, Ola, or local utilities) incredibly simple.

To add a new service:

1. **Create a Parser:** Add a new class in the parsers directory that inherits from the Base Parser.
2. **Define Logic:** Implement the parsing logic for that specific vendor's email HTML structure (Gemini is great at helping with this!).
3. **Register:** Add the vendor name to the `ParserFactory`.
4. **Sync:** The engine will automatically begin identifying and categorizing those emails during the next sync.

This modularity ensures that the engine stays lean while being infinitely expandable to your specific digital footprint.

---

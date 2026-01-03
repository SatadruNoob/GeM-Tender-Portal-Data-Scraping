# GeM Bid Data Extraction & Analysis

## Overview

This project provides a robust and scalable solution to **extract, deduplicate, and analyze bid data** from the **Government e-Marketplace (GeM)** portal.

The GeM portal uses **JavaScript-driven pagination with unstable ordering**, which makes traditional scraping approaches unreliable. This project addresses those challenges by using **real browser automation**, **DOM-based synchronization**, and **on-the-fly deduplication** to ensure accurate and complete data collection.

The extracted data is stored in a clean, reusable CSV format and can be used for further analysis, reporting, and dashboarding.

---

## Key Features

- Real browser automation for JavaScript-rendered pages  
- Handles unstable and reshuffled pagination reliably  
- Extracts only **unique bids** using Bid Number as the primary key  
- Incremental CSV persistence for long-running jobs  
- Safe restart and recovery without data loss  
- Designed for large-scale data extraction (tens of thousands of bids)  
- Output ready for downstream analysis and UI visualization  

---

## Data Extracted

For each unique GeM bid, the following fields are captured:

- **Bid Number**
- **Item Description** (full list via tooltip data)
- **Quantity**
- **Department Name and Address**
- **Bid Start Date**
- **Bid End Date**

Output file:


gem_all_bids.csv




## Installation Prerequisites

Before running the project, ensure the following are installed on your system:
---
- **Python 3.9 or higher**
- **pip** (Python package manager)
- **Google Chrome / Chromium** (for Playwright browser automation)
- Stable internet connection (long-running session recommended)

> ⚠️ Note: Headed (non-headless) browser mode is used to reduce blocking risk.

---

## Installation & Setup

###  Installation Pre requisites

```bash

1️⃣ Install Python dependencies
pip install playwright pandas

2️⃣ Install Playwright browser binaries
playwright install chromium

```

This installs the required Chromium browser used by Playwright.

How to Run
python gem_all_bids_playwright_csv.py


The script will:

Open the GeM bid listing page

Navigate pagination via real UI clicks

Extract bid data page by page

Deduplicate bids in real time

Save results incrementally to gem_all_bids.csv

How It Works (High-Level)

Launches a headed browser to mimic normal user navigation

Clicks pagination controls instead of guessing backend APIs

Waits for actual DOM changes to confirm page updates

Extracts bid data from rendered HTML

Deduplicates bids in real time using Bid Number

Saves data incrementally to CSV

Retries on temporary UI or pagination glitches

Technology Stack

Python

Playwright (Browser Automation)

Pandas (Data handling)

CSV-based data pipeline

DOM inspection and JavaScript synchronization

Project Structure
```
.
├── gem_all_bids_playwright_csv.py   # Main extraction script
├── gem_all_bids.csv                 # Extracted data (generated)
├── README.md                        # Project documentation

```

Use Cases

Monitoring procurement opportunities

Keyword-based bid analysis (e.g. Lead Acid, Planté, Traction Batteries)

Department-wise demand analysis

Bid expiry tracking and planning

Feeding BI dashboards or internal tools

Notes & Limitations

The scraper relies on UI behavior; long uninterrupted runs are recommended

Bid order is not stable by design; deduplication ensures correctness

Parallel scraping is intentionally avoided to reduce blocking risk

Disclaimer

This project is intended for educational and analytical purposes.
Users are responsible for ensuring compliance with applicable terms of service and regulations.

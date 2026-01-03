# file: gem_all_bids_playwright_csv.py

from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import time
import os

START_URL = "https://bidplus.gem.gov.in/all-bids"
CSV_FILE = "gem_all_bids.csv"

PAGE_DELAY_SEC = 1.5
SAVE_EVERY_PAGES = 3
MAX_NEXT_MISSES = 2


def extract_bids(page):
    bids = []
    cards = page.locator("div.card")
    count = cards.count()

    for i in range(count):
        card = cards.nth(i)

        bid_link = card.locator("a.bid_no_hover", has_text="/B/")
        if bid_link.count() == 0:
            continue

        bid_no = bid_link.first.inner_text().strip()

        items_el = card.locator("strong:has-text('Items:') + a")
        items = items_el.get_attribute("data-content") if items_el.count() else ""

        quantity_text = (
            card.locator("strong:has-text('Quantity:')")
            .locator("..")
            .inner_text()
        )
        quantity = quantity_text.replace("Quantity:", "").strip()

        dept_block = card.locator("div.col-md-5 .row").nth(1)
        department = dept_block.inner_text().replace("\n", " | ").strip()

        start_date = card.locator(".start_date").inner_text().strip()
        end_date = card.locator(".end_date").inner_text().strip()

        bids.append({
            "Bid No": bid_no,
            "Items": items,
            "Quantity": quantity,
            "Department Name And Address": department,
            "Start Date": start_date,
            "End Date": end_date,
        })

    return bids


def append_to_csv(rows):
    df = pd.DataFrame(rows)
    write_header = not os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode="a", index=False, header=write_header)


def load_seen_from_csv():
    if not os.path.exists(CSV_FILE):
        return set()
    df = pd.read_csv(CSV_FILE, usecols=["Bid No"])
    return set(df["Bid No"].astype(str))


def main():
    buffer = []
    seen = load_seen_from_csv()
    page_index = 1
    next_misses = 0

    print(f"[init] Loaded {len(seen)} existing bids from CSV")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        print("[*] Opening GeM All Bids…")
        page.goto(START_URL, timeout=90_000)
        page.wait_for_selector("div.card", timeout=60_000)

        while True:
            print(f"[*] Parsing page {page_index}")

            bids = extract_bids(page)
            added = 0

            for bid in bids:
                if bid["Bid No"] not in seen:
                    seen.add(bid["Bid No"])
                    buffer.append(bid)
                    added += 1

            print(f"[+] Added {added} bids | buffer={len(buffer)}")

            if page_index % SAVE_EVERY_PAGES == 0 and buffer:
                append_to_csv(buffer)
                print(f"[✓] Saved {len(buffer)} rows to CSV")
                buffer.clear()

            print("[debug] Checking Next button state")
            next_btn = page.locator("#light-pagination .next:not(.current)")

            if next_btn.count() == 0:
                next_misses += 1
                print(f"[warn] Next button missing ({next_misses}/{MAX_NEXT_MISSES})")
                if next_misses >= MAX_NEXT_MISSES:
                    print("[✓] Next button gone consistently. Done.")
                    break
                time.sleep(2)
                continue
            else:
                next_misses = 0

            first_bid = page.locator("a.bid_no_hover", has_text="/B/").first.inner_text()

            next_btn.click()
            time.sleep(PAGE_DELAY_SEC)

            try:
                page.wait_for_function(
                    f"""
                    () => {{
                        const el = [...document.querySelectorAll('a.bid_no_hover')]
                          .find(a => a.innerText.includes('/B/'));
                        return el && el.innerText !== {first_bid!r};
                    }}
                    """,
                    timeout=60_000,
                )
            except TimeoutError:
                print(f"[!] Pagination stalled on page {page_index}")
                page.screenshot(path=f"stall_page_{page_index}.png")
                print("[warn] Retrying click instead of stopping")
                next_btn.click()
                time.sleep(PAGE_DELAY_SEC)
                continue

            page_index += 1

        browser.close()

    if buffer:
        append_to_csv(buffer)
        print(f"[✓] Final save: {len(buffer)} rows")

    print(f"[✓] Finished. Output file: {CSV_FILE}")


if __name__ == "__main__":
    main()

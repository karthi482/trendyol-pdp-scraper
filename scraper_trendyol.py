
import json
import os
import re
import time
import random
from playwright.sync_api import Playwright, sync_playwright

def save_html(path: str, html: str):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)



def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.trendyol.com/en/select-country?cb=/en", wait_until="domcontentloaded")
    time.sleep(3)

    try:
        page.get_by_role("button", name="Accept All Cookies").click(timeout=8000)
    except Exception:
        pass

    time.sleep(1)
    page.get_by_test_id("country-select").select_option("United Arab Emirates")
    page.get_by_test_id("country-select-btn-desktop").click()
    time.sleep(2)

    # Close popup if present
    try:
        page.get_by_role("button", name="Close").click(timeout=4000)
    except Exception:
        pass

    # --- Go listing
    page.goto("https://www.trendyol.com/en/women-sneakers-x-g1-c1172", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    results = []

    a_xpath = "/html/body/main/div[2]/div/div/div/div[2]/div[3]/div[1]/div/a[{i}]"

    max_consecutive_miss = 40
    miss_count = 0

    for i in range(1, 5000):
        # step scroll
        page.evaluate("window.scrollBy(0, 350)")
        page.wait_for_timeout(int(random.uniform(250, 700)))

        locator = page.locator(f"xpath={a_xpath.format(i=i)}")
        if locator.count() == 0:
            miss_count += 1
            if miss_count >= max_consecutive_miss:
                print(f"[STOP] {miss_count} misses in a row → end of loaded list.")
                break
            continue

        miss_count = 0

        href = None
        try:
            href = locator.get_attribute("href")
        except Exception:
            href = None

        if not href:
            print(f"[!] No href at index {i}")
            continue

        if href.startswith("/"):
            href = "https://www.trendyol.com" + href

        print(f"\n[+] Opening {i}: {href}")

        page.goto(href, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)

        html = page.content()
        save_path = os.path.join("pdp_html", f"pdp_{i}.html")
        save_html(save_path, html)

        page.go_back(wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    with open("pdp_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n==============================")
    print("TOTAL PDPs extracted:", len(results))
    print("==============================")

    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

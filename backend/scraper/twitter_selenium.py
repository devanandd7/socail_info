from __future__ import annotations

from datetime import datetime, timezone
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape_profile(handle: str, max_scrolls: int = 4, pause_seconds: float = 2.0) -> list[dict]:
    """
    Prototype mode for X using Selenium.
    Requires manual login in the opened browser window.
    """
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://x.com/login")
        input("Log in to X in the browser, then press Enter here to continue...")

        clean = handle.lstrip("@")
        driver.get(f"https://x.com/{clean}")
        time.sleep(3)

        seen_urls: set[str] = set()
        posts: list[dict] = []

        for _ in range(max_scrolls):
            articles = driver.find_elements(By.CSS_SELECTOR, "article")
            for article in articles:
                try:
                    anchors = article.find_elements(By.CSS_SELECTOR, "a[href*='/status/']")
                    if not anchors:
                        continue
                    url = anchors[-1].get_attribute("href")
                    if not url or url in seen_urls:
                        continue

                    text = article.text.strip()
                    if not text:
                        continue

                    seen_urls.add(url)
                    posts.append(
                        {
                            "platform": "twitter",
                            "author": clean,
                            "content": text,
                            "url": url,
                            "timestamp": datetime.now(timezone.utc),
                            "engagement_score": 0.0,
                        }
                    )
                except Exception:
                    continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_seconds)

        return posts
    finally:
        driver.quit()

#!/usr/bin/env python3
"""Add to workflow between 'Wait for Obscura' and 'Run scraper':
  - run: python scraper/debug.py
"""
import asyncio, re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
        )
        page = await ctx.new_page()
        url = "https://www.google.com/maps/search/?api=1&query=Tuticorin-1&query_place_id=ChIJ5zJNoJfvAzsR-bJE_3bbNYw"
        print(f"Loading: {url}", flush=True)
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(4000)
        print(f"Final URL: {page.url}", flush=True)
        print(f"Title: {await page.title()}", flush=True)

        # Dump all aria-labels
        print("\n=== ALL ARIA-LABELS ===", flush=True)
        locs = page.locator("[aria-label]")
        n = await locs.count()
        print(f"Total elements with aria-label: {n}", flush=True)
        for i in range(min(n, 40)):
            try:
                lbl = await locs.nth(i).get_attribute("aria-label", timeout=2000)
                txt = (await locs.nth(i).text_content(timeout=2000) or "").strip()[:50]
                tag = await locs.nth(i).evaluate("el => el.tagName")
                if any(x in (lbl or "").lower() for x in ["review","star","rating","rated"]):
                    print(f"  {tag} | aria-label={lbl!r} | text={txt!r}", flush=True)
            except Exception:
                pass

        # Dump all buttons
        print("\n=== BUTTONS ===", flush=True)
        btns = page.locator("button")
        nb = await btns.count()
        print(f"Total buttons: {nb}", flush=True)
        for i in range(min(nb, 30)):
            try:
                txt = (await btns.nth(i).text_content(timeout=2000) or "").strip()[:60]
                lbl = await btns.nth(i).get_attribute("aria-label", timeout=2000) or ""
                if txt or lbl:
                    print(f"  text={txt!r} aria={lbl!r}", flush=True)
            except Exception:
                pass

        # Sample of all text on page
        print("\n=== PAGE TEXT SAMPLE ===", flush=True)
        all_spans = page.locator("span, div")
        ns = await all_spans.count()
        shown = 0
        for i in range(min(ns, 500)):
            try:
                txt = (await all_spans.nth(i).text_content(timeout=1000) or "").strip()
                if re.search(r"\d.*review", txt, re.I) and len(txt) < 50:
                    print(f"  REVIEW TEXT: {txt!r}", flush=True)
                    shown += 1
                    if shown > 10: break
            except Exception:
                pass

        await browser.close()

asyncio.run(main())

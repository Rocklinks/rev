#!/usr/bin/env python3
"""
Diagnostic tool — dumps aria-labels, buttons, and review text from a Google Maps page.
NO page.evaluate() — only locators.
Run via Obscura CDP on localhost:9222.
"""
import asyncio, re
from playwright.async_api import async_playwright

async def get_text(loc) -> str:
    try: return (await loc.text_content(timeout=3000) or "").strip()
    except Exception: return ""

async def get_attr(loc, attr) -> str:
    try: return (await loc.get_attribute(attr, timeout=3000) or "").strip()
    except Exception: return ""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.25 Safari/537.36",
        )
        page = await ctx.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}", lambda r: r.abort())

        # Establish session first
        try:
            await page.goto("https://www.google.com/maps", wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)
        except Exception: pass

        url = "https://www.google.com/maps/place/?q=place_id:ChIJ5zJNoJfvAzsR-bJE_3bbNYw"
        print(f"Loading: {url}", flush=True)
        await page.goto(url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(5000)
        print(f"Final URL: {page.url}", flush=True)
        print(f"Title: {await page.title()}", flush=True)

        # Dump all aria-labels (no evaluate — use locator only)
        print("\n=== ALL ARIA-LABELS ===", flush=True)
        locs = page.locator("[aria-label]")
        n = await locs.count()
        print(f"Total elements with aria-label: {n}", flush=True)
        for i in range(min(n, 120)):
            try:
                lbl = await get_attr(locs.nth(i), "aria-label")
                txt = (await get_text(locs.nth(i)))[:50]
                if any(x in (lbl or "").lower() for x in ["review","star","rating","rated"]):
                    print(f"  [{i}] aria-label={lbl!r} | text={txt!r}", flush=True)
            except Exception:
                pass

        # Dump all buttons
        print("\n=== BUTTONS ===", flush=True)
        btns = page.locator("button")
        nb = await btns.count()
        print(f"Total buttons: {nb}", flush=True)
        for i in range(min(nb, 40)):
            try:
                txt = (await get_text(btns.nth(i)))[:80]
                lbl = await get_attr(btns.nth(i), "aria-label")
                if txt or lbl:
                    print(f"  text={txt!r} aria={lbl!r}", flush=True)
            except Exception:
                pass

        # Review text scan
        print("\n=== REVIEW TEXT SAMPLE ===", flush=True)
        all_spans = page.locator("span, div")
        ns = await all_spans.count()
        shown = 0
        for i in range(min(ns, 1000)):
            try:
                txt = (await get_text(all_spans.nth(i)))
                if re.search(r"\d.*review", txt, re.I) and len(txt) < 80:
                    print(f"  REVIEW TEXT: {txt!r}", flush=True)
                    shown += 1
                    if shown > 20: break
            except Exception:
                pass

        # Dump page HTML snippet for review section
        print("\n=== PAGE HTML SNIPPET (body first 5000 chars) ===", flush=True)
        try:
            html = await page.content()
            print(html[:5000], flush=True)
        except Exception as e:
            print(f"  Error getting content: {e}", flush=True)

        await page.close()
        await ctx.close()
        await browser.close()

asyncio.run(main())

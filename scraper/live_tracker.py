#!/usr/bin/env python3
"""
Live Tracker — scrolls Reviews tab, counts all [data-review-id] blocks
loaded since 12 AM IST. Scrolls until no new reviews appear (handles 50+).
"""
import asyncio, traceback, sys, json, re, shutil, glob as globmod
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST        = timedelta(hours=5, minutes=30)
DATA_FILE  = Path(__file__).parent / "reviews.json"
LIVE_FILE  = Path(__file__).parent / "live_data.json"
CONCURRENCY = 3

BRANCHES = [
    {"id":1,  "name":"Tuticorin-1",     "place_id":"ChIJ5zJNoJfvAzsR-bJE_3bbNYw", "agm":"Sivaperumal"},
    {"id":2,  "name":"Tuticorin-2",     "place_id":"ChIJH6gY4-PvAzsRJ50skTlx3cs", "agm":"Sivaperumal"},
    {"id":3,  "name":"Thiruchendur-1",  "place_id":"ChIJeXA4vJKRAzsRBovAtv6lMuQ", "agm":"Sivaperumal"},
    {"id":4,  "name":"Thisayanvilai-1", "place_id":"ChIJVWkvdfh_BDsRdvtimKCLS5Y", "agm":"Sivaperumal"},
    {"id":5,  "name":"Eral-2",          "place_id":"ChIJbwAA0KGMAzsRkQilW5PceeA", "agm":"Sivaperumal"},
    {"id":6,  "name":"Udankudi",        "place_id":"ChIJPQAAACyEAzsRgjznQ1GLom0", "agm":"Sivaperumal"},
    {"id":7,  "name":"Tirunelveli-1",   "place_id":"ChIJ2RU2NvQRBDsRq-Fw7IVwx7k", "agm":"Johnson"},
    {"id":8,  "name":"Valliyur-1",      "place_id":"ChIJcVNk6TtnBDsRBoP4zpExt5k", "agm":"Johnson"},
    {"id":9,  "name":"Ambasamudram-1",  "place_id":"ChIJ9SGeIi85BDsRZk4QdyW9BSY", "agm":"Johnson"},
    {"id":10, "name":"Anjugramam-1",    "place_id":"ChIJ4yeJebLtBDsRDceoxujdGyc", "agm":"Johnson"},
    {"id":11, "name":"Nagercoil",       "place_id":"ChIJe1LZBiTxBDsRJFLjlbgZoIs", "agm":"Jeeva"},
    {"id":12, "name":"Marthandam",      "place_id":"ChIJcWptCRdVBDsRlJh2q0-rnfY", "agm":"Jeeva"},
    {"id":13, "name":"Thuckalay-1",     "place_id":"ChIJc9QgEub4BDsRoyDR4Wd6tYA", "agm":"Jeeva"},
    {"id":14, "name":"Colachel-1",      "place_id":"ChIJgRkBLw39BDsR58D0lwNo5Ts", "agm":"Jeeva"},
    {"id":15, "name":"Kulasekharam-1",  "place_id":"ChIJw0Ep-kNXBDsRe5ad32jAeAk", "agm":"Jeeva"},
    {"id":16, "name":"Monday Market",   "place_id":"ChIJTceRGAD5BDsR65i3YNTcYHk", "agm":"Jeeva"},
    {"id":17, "name":"Karungal-1",      "place_id":"ChIJfTP5ASr_BDsRgsBaeQltkw4", "agm":"Jeeva"},
    {"id":18, "name":"Kovilpatti",      "place_id":"ChIJHY0o-26yBjsRt7wbXB1pDUE", "agm":"Seenivasan"},
    {"id":19, "name":"Ramnad",          "place_id":"ChIJNVVVVaGiATsRnunSgOTvbE8", "agm":"Seenivasan"},
    {"id":20, "name":"Paramakudi",      "place_id":"ChIJ-dgjBzQHATsRf27FWAJgmsA", "agm":"Seenivasan"},
    {"id":21, "name":"Sayalkudi-1",     "place_id":"ChIJRTqudn9lATsR2fYyMmxlOrw", "agm":"Seenivasan"},
    {"id":22, "name":"Villathikullam",  "place_id":"ChIJi_wAkwVbATsRtFl3_V5rGrY", "agm":"Seenivasan"},
    {"id":23, "name":"Sattur-2",        "place_id":"ChIJNVVVVcHKBjsR7xMX97RFn8Q", "agm":"Seenivasan"},
    {"id":24, "name":"Sankarankovil-1", "place_id":"ChIJE1mKnhSXBjsRKMQ-9JKQf_c", "agm":"Seenivasan"},
    {"id":25, "name":"Kayathar-1",      "place_id":"ChIJx5ebtUgRBDsRMquPZNUJVpw", "agm":"Seenivasan"},
    {"id":26, "name":"Thenkasi",        "place_id":"ChIJuaqqquEpBDsRVITw0MMYklc", "agm":"Muthuselvam"},
    {"id":27, "name":"Thenkasi-2",      "place_id":"ChIJiwqLye6DBjsRo9v1mWXaycI", "agm":"Muthuselvam"},
    {"id":28, "name":"Surandai-1",      "place_id":"ChIJPb1_eEOdBjsRjL9IVCVJhi8", "agm":"Muthuselvam"},
    {"id":29, "name":"Puliyankudi-1",   "place_id":"ChIJjZqoc46RBjsRQTGHnNC8xxA", "agm":"Muthuselvam"},
    {"id":30, "name":"Sengottai-1",     "place_id":"ChIJw3zzKiaBBjsR9KDyGpn1nXU", "agm":"Muthuselvam"},
    {"id":31, "name":"Rajapalayam",     "place_id":"ChIJW2ot-DDpBjsRMTfMF2IV-xE", "agm":"Muthuselvam"},
    {"id":32, "name":"Virudhunagar",    "place_id":"ChIJN3jzNJgsATsRCU3nrB5ntKE", "agm":"Venkadesan"},
    {"id":33, "name":"Virudhunagar-2",  "place_id":"ChIJPezaX7wtATsR9sHhFOG6A1c", "agm":"Venkadesan"},
    {"id":34, "name":"Aruppukottai",    "place_id":"ChIJy6qqqgYwATsRbcp-hXnoruM", "agm":"Venkadesan"},
    {"id":35, "name":"Aruppukottai-2",  "place_id":"ChIJY04wY58xATsRuoJSichVQQE", "agm":"Venkadesan"},
    {"id":36, "name":"Sivakasi",        "place_id":"ChIJI2JvEePOBjsREh8b-x4WF4U", "agm":"Venkadesan"},
]

def ist_now():
    return datetime.now(timezone.utc) + IST

async def get_text(loc) -> str:
    try: return (await loc.text_content(timeout=3000) or "").strip()
    except Exception: return ""

async def get_attr(loc, attr) -> str:
    try: return (await loc.get_attribute(attr, timeout=3000) or "").strip()
    except Exception: return ""

async def extract_review_count(page):
    total = 0
    for sel in [
        'button[aria-label*="review" i]',
        'a[aria-label*="review" i]',
        'span[aria-label*="review" i]',
        'div[aria-label*="review" i]',
        '[aria-label*="reviews on Google" i]',
        '[aria-label*="Review" i]',
    ]:
        locs = page.locator(sel)
        n = await locs.count()
        for i in range(min(n, 20)):
            lbl = await get_attr(locs.nth(i), "aria-label")
            m = re.search(r"^[\(]?\s*([\d,]+)\s*reviews?\s*[\)]?", lbl, re.I)
            if m:
                total = int(m.group(1).replace(",",""))
                if total > 0: break
            m = re.search(r"([\d,]+)\s*reviews?\s*on Google", lbl, re.I)
            if m:
                total = int(m.group(1).replace(",",""))
                if total > 0: break
        if total: break
    if not total:
        for sel in ['button', 'a', 'span', 'div']:
            locs = page.locator(sel)
            n = await locs.count()
            for i in range(min(n, 200)):
                txt = await get_text(locs.nth(i))
                m = re.search(r"[\(]?\s*([\d,]+)\s*reviews?\s*[\)]?", txt, re.I)
                if m:
                    candidate = int(m.group(1).replace(",",""))
                    if candidate > 0:
                        total = candidate
                        break
            if total: break
    if not total:
        try:
            html = await page.content()
            for pat in [
                r'"([\d,]+)\s*reviews?"',
                r'([\d,]+)\s*reviews?\s*on Google',
                r'aria-label="[^"]*([\d,]+)\s*review',
                r'>([\d,]+)\s*reviews?<',
            ]:
                m = re.search(pat, html, re.I)
                if m:
                    total = int(m.group(1).replace(",",""))
                    if total > 0: break
        except Exception: pass
    return total

async def extract_stars(page):
    stars = 0.0
    for sel in [
        '[aria-label*="Rated" i]',
        '[aria-label*="stars" i]',
        '[aria-label*="star" i]',
        '[aria-label*="rating" i]',
    ]:
        locs = page.locator(sel)
        n = await locs.count()
        for i in range(min(n, 10)):
            lbl = await get_attr(locs.nth(i), "aria-label")
            m = re.search(r"([1-5][.,]\d)", lbl)
            if m:
                v = float(m.group(1).replace(",","."))
                if 1.0 <= v <= 5.0:
                    stars = v
                    break
        if stars: break
    if not stars:
        try:
            html = await page.content()
            m = re.search(r'"rating"[^}]*"([\d.]+)"', html)
            if m:
                v = float(m.group(1))
                if 1.0 <= v <= 5.0: stars = v
        except Exception: pass
    return stars

def parse_relative_date(text, today_ist):
    t = text.lower().strip()
    today     = today_ist.date()
    yesterday = (today_ist - timedelta(days=1)).date()
    if any(x in t for x in ["just now","second","minute","hour"]):
        return today.strftime("%Y-%m-%d")
    if any(x in t for x in ["yesterday","1 day ago","a day ago"]):
        return yesterday.strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*day", t)
    if m:
        return (today_ist - timedelta(days=int(m.group(1)))).date().strftime("%Y-%m-%d")
    return None

async def count_reviews_by_scroll(page, today_str):
    """Click Reviews tab, sort newest, scroll and count all reviews from today.
    Stops when it hits a review older than today (sorted newest first)."""
    today_ist_dt = ist_now()
    seen_ids = set()
    today_count = 0

    # Click Reviews tab
    try:
        tab_sel = (
            'button[aria-label*="Review" i], '
            'button:has-text("Reviews"), '
            'a[aria-label*="Review" i]'
        )
        if await page.locator(tab_sel).count() > 0:
            await page.locator(tab_sel).first.click(timeout=5000)
            await page.wait_for_timeout(2000)
    except Exception: pass

    # Sort newest
    try:
        sb_sel = 'button[aria-label*="Sort" i], button[aria-label*="sort" i]'
        if await page.locator(sb_sel).count() > 0:
            await page.locator(sb_sel).first.click(timeout=5000)
            await page.wait_for_timeout(800)
            nw_sel = (
                '[role="menuitemradio"]:has-text("Newest"), '
                'li:has-text("Newest"), '
                '[role="option"]:has-text("Newest")'
            )
            if await page.locator(nw_sel).count() > 0:
                await page.locator(nw_sel).first.click(timeout=5000)
                await page.wait_for_timeout(2000)
    except Exception: pass

    # Scroll and count every review from today. Stop when we see one older than today.
    for scroll_round in range(200):
        blocks = page.locator('[data-review-id]')
        n = await blocks.count()

        found_older_than_today = False

        for i in range(n):
            try:
                blk = blocks.nth(i)
                rid = await get_attr(blk, "data-review-id")
                if not rid or rid in seen_ids: continue
                seen_ids.add(rid)

                dt = ""
                spans = blk.locator("span")
                sc = await spans.count()
                for j in range(min(sc, 30)):
                    t = await get_text(spans.nth(j))
                    if re.search(r"ago|yesterday|day|week|month|year|edited", t, re.I) and len(t) < 40:
                        dt = t; break
                if not dt: continue

                parsed = parse_relative_date(dt, today_ist_dt)
                if parsed is None: continue

                if parsed == today_str:
                    today_count += 1
                    if today_count >= 50:
                        break
                elif parsed < today_str:
                    found_older_than_today = True
                    break
            except Exception: continue

        if today_count >= 50 or found_older_than_today:
            break

        # Scroll down
        try:
            panel_sel = '[tabindex="-1"]'
            if await page.locator(panel_sel).count() > 0:
                await page.locator(panel_sel).first.focus()
            await page.keyboard.press("End")
        except Exception: pass
        await page.wait_for_timeout(1000)

    return today_count

async def fetch_branch(browser, branch, today_str):
    """Fetch total count + today's review count via scroll method."""
    url = f"https://www.google.com/maps/place/?q=place_id:{branch['place_id']}"
    page = None
    try:
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.25 Safari/537.36",
        )
        page = await ctx.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}", lambda r: r.abort())
        try:
            await page.goto("https://www.google.com/maps", wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)
        except Exception: pass
        await page.goto(url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(5000)

        total = await extract_review_count(page)
        stars = await extract_stars(page)

        today_count = 0
        if total > 0:
            today_count = await count_reviews_by_scroll(page, today_str)

        await page.close(); await ctx.close()
        return total, stars, today_count
    except Exception:
        try:
            if page: await page.close()
        except Exception: pass
        return 0, 0.0, 0

async def run_live():
    from playwright.async_api import async_playwright
    now_ist  = ist_now()
    run_time = now_ist.isoformat()
    today    = now_ist.date().strftime("%Y-%m-%d")

    # Get 12 AM IST baseline
    base = {}
    if DATA_FILE.exists():
        try:
            d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            dates = sorted([x for x in d.get("daily",{}) if x <= today], reverse=True)
            if dates:
                base = d["daily"].get(dates[0],{})
        except Exception: pass

    results = {}
    async with async_playwright() as p:
        brave = shutil.which("brave") or shutil.which("brave-browser") or shutil.which("google-chrome") or shutil.which("chromium")
        if not brave:
            candidates = globmod.glob(str(Path.home() / ".cache" / "ms-playwright" / "chromium-*" / "chrome-linux" / "chrome"))
            if candidates: brave = candidates[0]
        if not brave:
            print("FATAL: No browser found.", flush=True); sys.exit(1)
        browser = await p.chromium.launch(
            executable_path=brave, headless=True,
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
                   "--disable-blink-features=AutomationControlled"],
        )
        print(f"  Launched {brave}", flush=True)
        sem = asyncio.Semaphore(CONCURRENCY)

        async def fetch_one(branch):
            async with sem:
                bid = str(branch["id"])
                print(f"  [{branch['id']:02}/36] {branch['name']} ...", flush=True)
                total, stars, today_count = await fetch_branch(browser, branch, today)
                if total == 0:
                    await asyncio.sleep(2)
                    total, stars, today_count = await fetch_branch(browser, branch, today)
                baseline = base.get(bid,{}).get("total_snap", 0)
                results[bid] = {
                    "id":branch["id"],"name":branch["name"],"agm":branch["agm"],
                    "total":total,"stars":stars,"baseline":baseline,
                    "today_count":today_count,
                }
                status = "✓" if total else "✗"
                print(f"  {status} {branch['name']}: total={total} today={today_count}", flush=True)
                await asyncio.sleep(0.3)

        await asyncio.gather(*[fetch_one(b) for b in BRANCHES])
        await browser.close()

    agm_summary = {}
    for bid, r in results.items():
        agm = r["agm"]
        if agm not in agm_summary:
            agm_summary[agm] = {"total_today":0,"branches":[]}
        agm_summary[agm]["total_today"] += r["today_count"]
        agm_summary[agm]["branches"].append(r)

    LIVE_FILE.write_text(json.dumps({
        "run_time":run_time,"today":today,
        "branches":results,"agm_summary":agm_summary,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved live_data.json", flush=True)

async def main():
    print(f"=== Live Tracker === {ist_now().strftime('%Y-%m-%d %H:%M IST')}")
    await run_live()
    print("=== Done ===")

if __name__ == "__main__":
    try: asyncio.run(main())
    except Exception as e:
        print(f"FATAL: {e}"); traceback.print_exc(); sys.exit(1)

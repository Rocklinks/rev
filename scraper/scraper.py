#!/usr/bin/env python3
"""
Google Reviews Scraper — Obscura CDP + Playwright locators only.
NO page.evaluate() — Obscura Chrome/145 returns proper values via locators.
Runs at 12 AM IST daily. Scrapes total, stars, yesterday's individual reviews.
"""
import asyncio, traceback, sys, json, re, shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST        = timedelta(hours=5, minutes=30)
DATA_FILE  = Path(__file__).parent / "reviews.json"
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
    {"id":26, "name":"Ramnad-2",        "place_id":"ChIJcWPpFSSZATsR1ai6lxBXkAw", "agm":"Seenivasan"},
    {"id":27, "name":"Thenkasi",        "place_id":"ChIJuaqqquEpBDsRVITw0MMYklc", "agm":"Muthuselvam"},
    {"id":28, "name":"Thenkasi-2",      "place_id":"ChIJiwqLye6DBjsRo9v1mWXaycI", "agm":"Muthuselvam"},
    {"id":29, "name":"Surandai-1",      "place_id":"ChIJPb1_eEOdBjsRjL9IVCVJhi8", "agm":"Muthuselvam"},
    {"id":30, "name":"Puliyankudi-1",   "place_id":"ChIJjZqoc46RBjsRQTGHnNC8xxA", "agm":"Muthuselvam"},
    {"id":31, "name":"Sengottai-1",     "place_id":"ChIJw3zzKiaBBjsR9KDyGpn1nXU", "agm":"Muthuselvam"},
    {"id":32, "name":"Rajapalayam",     "place_id":"ChIJW2ot-DDpBjsRMTfMF2IV-xE", "agm":"Muthuselvam"},
    {"id":33, "name":"Virudhunagar",    "place_id":"ChIJN3jzNJgsATsRCU3nrB5ntKE", "agm":"Venkadesan"},
    {"id":34, "name":"Virudhunagar-2",  "place_id":"ChIJPezaX7wtATsR9sHhFOG6A1c", "agm":"Venkadesan"},
    {"id":35, "name":"Aruppukottai",    "place_id":"ChIJy6qqqgYwATsRbcp-hXnoruM", "agm":"Venkadesan"},
    {"id":36, "name":"Aruppukottai-2",  "place_id":"ChIJY04wY58xATsRuoJSichVQQE", "agm":"Venkadesan"},
    {"id":37, "name":"Sivakasi",        "place_id":"ChIJI2JvEePOBjsREh8b-x4WF4U", "agm":"Venkadesan"},
]

def load_data():
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception: pass
    return {"branches":{}, "daily":{}, "logs":[]}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def ist_now():
    return datetime.now(timezone.utc) + IST

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

async def get_text(loc) -> str:
    try: return (await loc.text_content(timeout=3000) or "").strip()
    except Exception: return ""

async def get_attr(loc, attr) -> str:
    try: return (await loc.get_attribute(attr, timeout=3000) or "").strip()
    except Exception: return ""

async def extract_review_count(page):
    total = 0

    # Strategy 1: aria-label on clickable elements (buttons, links, spans)
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
            # Match "7,213 reviews" but NOT "laptop, mentioned in 91 reviews"
            # Prefer exact patterns: "X reviews", "X reviews on Google"
            m = re.search(r"^[\(]?\s*([\d,]+)\s*reviews?\s*[\)]?", lbl, re.I)
            if m:
                total = int(m.group(1).replace(",",""))
                if total > 0: break
            m = re.search(r"([\d,]+)\s*reviews?\s*on Google", lbl, re.I)
            if m:
                total = int(m.group(1).replace(",",""))
                if total > 0: break
        if total: break

    # Strategy 2: text content scan — look for "X reviews" in buttons, links, spans
    if not total:
        for sel in ['button', 'a', 'span', 'div']:
            locs = page.locator(sel)
            n = await locs.count()
            for i in range(min(n, 200)):
                txt = await get_text(locs.nth(i))
                # Match "1,234 reviews" or "(1,234 reviews)" or "1234 reviews"
                m = re.search(r"[\(]?\s*([\d,]+)\s*reviews?\s*[\)]?", txt, re.I)
                if m:
                    candidate = int(m.group(1).replace(",",""))
                    if candidate > 0:
                        total = candidate
                        break
            if total: break

    # Strategy 3: parse from full page HTML
    if not total:
        try:
            html = await page.content()
            # Common patterns in Google Maps HTML
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

    # Strategy 1: aria-label containing star rating
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

    # Strategy 2: parse from page HTML
    if not stars:
        try:
            html = await page.content()
            m = re.search(r'"rating"[^}]*"([\d.]+)"', html)
            if m:
                v = float(m.group(1))
                if 1.0 <= v <= 5.0: stars = v
            if not stars:
                m = re.search(r'aria-label="[^"]*([1-5]\.\d)\s*out\s*of', html, re.I)
                if m:
                    v = float(m.group(1))
                    if 1.0 <= v <= 5.0: stars = v
        except Exception: pass

    return stars

async def extract_review_cards(page):
    reviews_found = []
    seen_ids = set()
    today_ist_dt = ist_now()

    # Try data-review-id blocks first
    blocks = page.locator('[data-review-id]')
    n = await blocks.count()

    if n > 0:
        for i in range(n):
            try:
                blk = blocks.nth(i)
                rid = await get_attr(blk, "data-review-id")
                if not rid or rid in seen_ids: continue
                seen_ids.add(rid)

                # Date
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

                # Stars from individual review
                rev_stars = 0
                for ss in ['[role="img"][aria-label*="star" i]',
                           '[aria-label*="Rated" i]',
                           '[aria-label*="star" i]']:
                    se = blk.locator(ss).first
                    if await se.count() > 0:
                        lbl = await get_attr(se, "aria-label")
                        m = re.search(r"([1-5])", lbl)
                        if m: rev_stars = int(m.group(1)); break

                # Reviewer name — try multiple strategies
                reviewer = "Anonymous"
                for ns in [
                    'a[href*="contrib"]',
                    'button[jsaction*="reviewer"]',
                    'button[jsaction*="profile"]',
                    'span[class*="fontBodyMedium"] button',
                    'div.fontBodyMedium span',
                    'button[jsaction]',
                    'div[role="button"]',
                ]:
                    try:
                        ne = blk.locator(ns).first
                        if await ne.count() > 0:
                            t = await get_text(ne)
                            if t and len(t) < 50 and not re.search(r"ago|day|week|month|year|Edited|star|Rated", t, re.I):
                                reviewer = t; break
                    except Exception: pass

                # Review text — try multiple strategies
                rev_text = ""
                for ts2 in [
                    '[class*="wiI7pd"]',
                    '[class*="MyEned"]',
                    'span[class] > span',
                    'div[class] > span',
                ]:
                    try:
                        te = blk.locator(ts2).first
                        if await te.count() > 0:
                            rev_text = await get_text(te)
                            if rev_text and len(rev_text) > 5: break
                            rev_text = ""
                    except Exception: pass

                reviews_found.append({
                    "review_id": rid,
                    "reviewer":  reviewer,
                    "stars":     rev_stars,
                    "text":      rev_text,
                    "date_text": dt,
                    "date":      parsed,
                })
            except Exception: continue

    # Fallback: parse reviews from full page HTML if no data-review-id found
    if not reviews_found:
        try:
            html = await page.content()
            # Try to extract contributor names from HTML
            contributor_names = {}
            for m in re.finditer(r'data-contributor-id="([^"]+)".*?aria-label="([^"]+)"', html, re.S):
                contributor_names[m.group(1)] = m.group(2)
            # Also try profile links pattern
            for m in re.finditer(r'href="/maps/contrib/(\d+)[^"]*"[^>]*>([^<]+)<', html):
                cid = m.group(1)
                name = m.group(2).strip()
                if name and len(name) < 50 and not re.search(r'review|photo|answer', name, re.I):
                    contributor_names[cid] = name

            review_blocks = re.findall(
                r'\["((?:[^"\\]|\\.){10,200})",\s*\[.*?\],\s*"([^"]*?(?:ago|yesterday|day|week|month|year)[^"]*?)"',
                html, re.I
            )
            for idx, (review_text, date_text) in enumerate(review_blocks):
                parsed = parse_relative_date(date_text, today_ist_dt)
                if parsed:
                    # Try to find a reviewer name near this review block
                    rev_name = "Anonymous"
                    for cid, name in contributor_names.items():
                        if name in html[:html.find(review_text)] if review_text in html else "":
                            rev_name = name; break
                    reviews_found.append({
                        "review_id": f"html_{idx}",
                        "reviewer": rev_name,
                        "stars": 0,
                        "text": review_text[:500],
                        "date_text": date_text,
                        "date": parsed,
                    })
        except Exception: pass

    return reviews_found

async def count_reviews_by_scroll(page, today_str):
    """Click Reviews tab, sort newest, scroll and count all reviews from today."""
    today_ist_dt = ist_now()
    seen_ids = set()
    today_count = 0

    try:
        tab_sel = (
            'button[aria-label*="Review" i], '
            'button:has-text("Reviews"), '
            'a[aria-label*="Review" i]'
        )
        if await page.locator(tab_sel).count() > 0:
            await page.locator(tab_sel).first.click(timeout=4000)
            await page.wait_for_timeout(1500)
    except Exception: pass

    try:
        sb_sel = 'button[aria-label*="Sort" i], button[aria-label*="sort" i]'
        if await page.locator(sb_sel).count() > 0:
            await page.locator(sb_sel).first.click(timeout=4000)
            await page.wait_for_timeout(600)
            nw_sel = (
                '[role="menuitemradio"]:has-text("Newest"), '
                'li:has-text("Newest"), '
                '[role="option"]:has-text("Newest")'
            )
            if await page.locator(nw_sel).count() > 0:
                await page.locator(nw_sel).first.click(timeout=4000)
                await page.wait_for_timeout(1500)
    except Exception: pass

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

        try:
            panel_sel = '[tabindex="-1"]'
            if await page.locator(panel_sel).count() > 0:
                await page.locator(panel_sel).first.focus()
            await page.keyboard.press("End")
        except Exception: pass
        await page.wait_for_timeout(800)

    return today_count

async def scrape_branch(browser, branch, today_str):
    url = f"https://www.google.com/maps/place/?q=place_id:{branch['place_id']}"
    result = {"total":0, "stars":0.0, "reviews":[], "today_count":0, "error":None}
    page = None
    try:
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.25 Safari/537.36",
        )
        page = await ctx.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}", lambda r: r.abort())
        # Establish session by loading Google Maps first
        try:
            await page.goto("https://www.google.com/maps", wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)
        except Exception: pass
        await page.goto(url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(5000)

        total = await extract_review_count(page)
        result["total"] = total

        stars = await extract_stars(page)
        result["stars"] = stars

        if total > 0:
            today_count = await count_reviews_by_scroll(page, today_str)
        result["today_count"] = today_count

        if total > 0:
            # Extract review cards (Reviews tab already opened and sorted by count_reviews_by_scroll)
            try:
                panel_sel = '[tabindex="-1"]'
                if await page.locator(panel_sel).count() > 0:
                    await page.locator(panel_sel).first.focus()
                await page.keyboard.press("Home")
                await page.wait_for_timeout(1000)
            except Exception: pass

            reviews = await extract_review_cards(page)
            result["reviews"] = reviews

        await page.close()
        await ctx.close()
    except Exception as e:
        result["error"] = str(e)
        try:
            if page: await page.close()
        except Exception: pass
    return result

async def run_all(today_str):
    from playwright.async_api import async_playwright
    results = {}; success = 0; failed = []
    async with async_playwright() as p:
        # Always launch a local browser — Obscura's Chrome/145 can't render Google Maps JS
        brave = shutil.which("brave") or shutil.which("brave-browser") or shutil.which("google-chrome") or shutil.which("chromium")
        if not brave:
            # Try Playwright's installed chromium as fallback
            import subprocess
            try:
                result = subprocess.run(["playwright", "install", "--dry-run", "chromium"],
                                       capture_output=True, text=True, timeout=5)
            except Exception: pass
            # Playwright stores chromium in ~/.cache/ms-playwright/
            import glob as globmod
            candidates = globmod.glob(str(Path.home() / ".cache" / "ms-playwright" / "chromium-*" / "chrome-linux" / "chrome"))
            if not candidates:
                candidates = globmod.glob(str(Path.home() / ".cache" / "ms-playwright" / "chromium-*" / "chrome-linux" / "chromium"))
            if candidates:
                brave = candidates[0]
        if not brave:
            print("FATAL: No browser found. Install brave, google-chrome, or run: playwright install chromium", flush=True)
            sys.exit(1)
        browser = await p.chromium.launch(
            executable_path=brave, headless=True,
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
                   "--disable-blink-features=AutomationControlled"],
        )
        print(f"  Launched {brave}", flush=True)
        sem = asyncio.Semaphore(CONCURRENCY)
        async def scrape_one(branch):
            nonlocal success
            async with sem:
                bid = str(branch["id"])
                print(f"  [{branch['id']:02}/36] {branch['name']} ...", flush=True)
                res = await scrape_branch(browser, branch, today_str)
                if res["total"] == 0:
                    await asyncio.sleep(3)
                    print(f"  ↻ Retry {branch['name']} ...", flush=True)
                    res = await scrape_branch(browser, branch, today_str)
                if res["total"] == 0:
                    print(f"  ✗ {branch['name']}: err={res['error']}", flush=True)
                    failed.append(branch["name"])
                else:
                    results[bid] = res; success += 1
                    print(f"  ✓ {branch['name']}: total={res['total']} stars={res['stars']} reviews={len(res['reviews'])}", flush=True)
                await asyncio.sleep(0.5)
        await asyncio.gather(*[scrape_one(b) for b in BRANCHES])
        await browser.close()
    return results, success, failed

def save_results(results, success, failed, snap_date, run_time):
    data = load_data()
    prev_dates    = sorted([d for d in data.get("daily",{}) if d < snap_date], reverse=True)
    baseline_date = prev_dates[0] if prev_dates else None
    baseline_snap = data["daily"].get(baseline_date,{}) if baseline_date else {}
    data.setdefault("daily",{}).setdefault(snap_date,{})
    snap_month       = snap_date[:7]
    prev_month_dates = sorted([d for d in data.get("daily",{}) if d.startswith(snap_month) and d < snap_date])
    monthly_snap     = data["daily"].get(prev_month_dates[-1],{}) if prev_month_dates else {}
    all_reviews = []
    for b in BRANCHES:
        bid = str(b["id"])
        if bid not in results: continue
        r = results[bid]
        prev_total = baseline_snap.get(bid,{}).get("total_snap", data.get("branches",{}).get(bid,{}).get("overall",0))
        raw_delta  = r["total"] - prev_total
        daily_count = r.get("today_count", 0)
        monthly    = monthly_snap.get(bid,{}).get("monthly",0) + daily_count
        data["daily"][snap_date][bid] = {
            "total_snap":r["total"], "daily_count":daily_count,
            "raw_delta":raw_delta, "has_deletion":raw_delta<0,
            "monthly":monthly, "star_rating":r["stars"],
            "yesterday_reviews":len(r["reviews"]),
        }
        data["branches"][bid] = {
            "id":b["id"],"name":b["name"],"agm":b["agm"],
            "overall":r["total"],"star_rating":r["stars"],"monthly":monthly,
        }
        for rev in r["reviews"]:
            all_reviews.append({**rev,"branch_id":b["id"],"branch_name":b["name"],"agm":b["agm"]})
    detail_dir = DATA_FILE.parent/"reviews_detail"
    detail_dir.mkdir(parents=True, exist_ok=True)

    # Group reviews by their actual parsed date and save each to correct file
    by_date = {}
    for rv in all_reviews:
        d = rv.get("date", snap_date)
        by_date.setdefault(d, []).append(rv)

    for date_key, revs in by_date.items():
        fpath = detail_dir/f"{date_key}.json"
        existing = []
        if fpath.exists():
            try:
                loaded = json.loads(fpath.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing = [x for x in loaded if isinstance(x, dict)]
            except Exception: pass
        existing_ids = {rv["review_id"] for rv in existing if isinstance(rv, dict)}
        merged = existing + [rv for rv in revs if rv["review_id"] not in existing_ids]
        fpath.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved {len(merged)} reviews -> {fpath}", flush=True)

    # Merge all existing review files into single all_reviews.json for fast frontend loading
    all_reviews_file = detail_dir/"all_reviews.json"
    all_existing = {}
    if all_reviews_file.exists():
        try:
            loaded = json.loads(all_reviews_file.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                for rv in loaded:
                    if isinstance(rv, dict) and "review_id" in rv:
                        all_existing[rv["review_id"]] = rv
            elif isinstance(loaded, dict):
                all_existing = loaded
        except Exception: pass
    for rv in all_reviews:
        if isinstance(rv, dict) and "review_id" in rv:
            all_existing[rv["review_id"]] = rv
    all_reviews_file.write_text(json.dumps(list(all_existing.values()), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved all_reviews.json — {len(all_existing)} total reviews", flush=True)

    data.setdefault("logs",[]).insert(0,{
        "ran_at":run_time,"snap_date":snap_date,
        "baseline_date":baseline_date,"success":success,
        "failed":len(failed),"failed_names":failed,
        "total_reviews":sum(len(v) for v in by_date.values()),
    })
    data["logs"] = data["logs"][:50]
    data["last_updated"] = run_time
    save_data(data)
    print(f"  Saved reviews.json — {success}/36 branches", flush=True)

async def main():
    now_ist   = ist_now()
    snap_date = (now_ist - timedelta(days=1)).date().strftime("%Y-%m-%d")
    today_str = snap_date
    run_time  = datetime.now(timezone.utc).isoformat()
    print("=== Google Reviews Scraper ===")
    print(f"  Run time : {now_ist.strftime('%Y-%m-%d %H:%M IST')}")
    print(f"  Snap date: {snap_date}")
    print()
    results, success, failed = await run_all(today_str)
    print(f"\n=== Results: {success}/36 ===")
    if failed: print(f"  Failed: {', '.join(failed)}")
    if success == 0:
        print("FATAL: 0 branches succeeded.")
        sys.exit(1)
    save_results(results, success, failed, snap_date, run_time)
    print("=== Done ===")

if __name__ == "__main__":
    try: asyncio.run(main())
    except Exception as e:
        print(f"FATAL: {e}"); traceback.print_exc(); sys.exit(1)

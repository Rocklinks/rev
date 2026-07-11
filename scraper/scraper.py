#!/usr/bin/env python3
"""
Google Reviews Scraper — Obscura CDP + Playwright locators only.
NO page.evaluate() — Obscura Chrome/145 returns proper values via locators.
Runs 1:30 AM IST. Scrapes total, stars, yesterday's individual reviews.
"""
import asyncio, traceback, sys, json, re, shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST        = timedelta(hours=5, minutes=30)
DATA_FILE  = Path(__file__).parent / "reviews.json"
BACKUP_DIR = Path(__file__).parent / "backups"
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

def load_data():
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception: pass
    return {"branches":{}, "daily":{}, "logs":[]}

def save_data(data):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(DATA_FILE, BACKUP_DIR/f"reviews_{ts}.json")
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

async def scrape_branch(browser, branch, snap_date, yesterday):
    url = (
        f"https://www.google.com/maps/search/?api=1"
        f"&query={branch['name'].replace(' ','+')}"
        f"&query_place_id={branch['place_id']}"
    )
    result = {"total":0, "stars":0.0, "reviews":[], "error":None}
    page = None
    try:
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
        )
        page = await ctx.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}", lambda r: r.abort())
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # ── Total reviews ─────────────────────────────────────────────────────
        total = 0
        # Try aria-label attrs first — most reliable
        for sel in ['[aria-label*="review" i]', '[aria-label*="Review"]']:
            locs = page.locator(sel)
            n = await locs.count()
            for i in range(min(n, 15)):
                lbl = await get_attr(locs.nth(i), "aria-label")
                m = re.search(r"([\d,]+)\s*review", lbl, re.I)
                if m:
                    total = int(m.group(1).replace(",",""))
                    break
            if total: break

        # Fallback: text content scan
        if not total:
            for sel in ['button', 'span', 'div']:
                locs = page.locator(sel)
                n = await locs.count()
                for i in range(min(n, 100)):
                    txt = await get_text(locs.nth(i))
                    m = re.search(r"^([\d,]+)\s*reviews?$", txt, re.I)
                    if m:
                        total = int(m.group(1).replace(",",""))
                        break
                if total: break

        result["total"] = total

        # ── Stars ─────────────────────────────────────────────────────────────
        stars = 0.0
        for sel in ['[aria-label*="Rated" i]','[aria-label*="star" i]','[aria-label*="rating" i]']:
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
        result["stars"] = stars

        # ── Reviews ───────────────────────────────────────────────────────────
        if total > 0:
            today_ist_dt = ist_now()

            # Click Reviews tab
            try:
                tab = page.locator('button[aria-label*="Review" i], button:has-text("Reviews")').first
                if await tab.count() > 0:
                    await tab.click(timeout=5000)
                    await page.wait_for_timeout(2000)
            except Exception: pass

            # Sort newest
            try:
                sb = page.locator('button[aria-label*="Sort" i]').first
                if await sb.count() > 0:
                    await sb.click(timeout=5000)
                    await page.wait_for_timeout(800)
                    nw = page.locator('[role="menuitemradio"]:has-text("Newest"), li:has-text("Newest")').first
                    if await nw.count() > 0:
                        await nw.click(timeout=5000)
                        await page.wait_for_timeout(2000)
            except Exception: pass

            reviews_found = []
            seen_ids = set()
            stop = False

            for _ in range(60):
                if stop: break
                blocks = page.locator('[data-review-id]')
                n = await blocks.count()

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
                        for j in range(min(sc, 20)):
                            t = await get_text(spans.nth(j))
                            if re.search(r"ago|yesterday|day|week|month|year", t, re.I) and len(t) < 30:
                                dt = t; break
                        if not dt: continue

                        parsed = parse_relative_date(dt, today_ist_dt)
                        if parsed is None: stop = True; break
                        if parsed < yesterday: stop = True; break

                        # Stars
                        rev_stars = 0
                        try:
                            se = blk.locator('[role="img"][aria-label]').first
                            if await se.count() > 0:
                                lbl = await get_attr(se, "aria-label")
                                m = re.search(r"([1-5])", lbl)
                                if m: rev_stars = int(m.group(1))
                        except Exception: pass

                        # Name
                        reviewer = "Anonymous"
                        for ns in ['button[jsaction]','div[class*="d4r55"]','a[href*="contrib"]']:
                            try:
                                ne = blk.locator(ns).first
                                if await ne.count() > 0:
                                    t = await get_text(ne)
                                    if t: reviewer = t; break
                            except Exception: pass

                        # Text
                        rev_text = ""
                        for ts2 in ['[class*="wiI7pd"]','[class*="MyEned"] span']:
                            try:
                                te = blk.locator(ts2).first
                                if await te.count() > 0:
                                    rev_text = await get_text(te)
                                    if rev_text: break
                            except Exception: pass

                        if parsed in (yesterday, snap_date):
                            reviews_found.append({
                                "review_id": rid,
                                "reviewer":  reviewer,
                                "stars":     rev_stars,
                                "text":      rev_text,
                                "date_text": dt,
                                "date":      parsed,
                            })
                    except Exception: continue

                if stop: break

                # Scroll via keyboard — no JS eval
                try:
                    panel = page.locator('[tabindex="-1"]').first
                    if await panel.count() > 0:
                        await panel.focus()
                    await page.keyboard.press("End")
                except Exception: pass
                await page.wait_for_timeout(1300)

            result["reviews"] = reviews_found

        await page.close()
        await ctx.close()
    except Exception as e:
        result["error"] = str(e)
        try:
            if page: await page.close()
        except Exception: pass
    return result

async def run_all(snap_date, yesterday):
    from playwright.async_api import async_playwright
    results = {}; success = 0; failed = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        sem = asyncio.Semaphore(CONCURRENCY)
        async def scrape_one(branch):
            nonlocal success
            async with sem:
                bid = str(branch["id"])
                print(f"  [{branch['id']:02}/36] {branch['name']} ...", flush=True)
                res = await scrape_branch(browser, branch, snap_date, yesterday)
                if res["total"] == 0:
                    await asyncio.sleep(3)
                    print(f"  ↻ Retry {branch['name']} ...", flush=True)
                    res = await scrape_branch(browser, branch, snap_date, yesterday)
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

def save_results(results, success, failed, snap_date, yesterday, run_time):
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
        monthly    = monthly_snap.get(bid,{}).get("monthly",0) + max(raw_delta,0)
        data["daily"][snap_date][bid] = {
            "total_snap":r["total"], "daily_count":max(raw_delta,0),
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
    detail_path = detail_dir/f"{yesterday}.json"
    existing = []
    if detail_path.exists():
        try: existing = json.loads(detail_path.read_text(encoding="utf-8"))
        except Exception: pass
    existing_ids = {rv["review_id"] for rv in existing}
    merged = existing + [rv for rv in all_reviews if rv["review_id"] not in existing_ids]
    detail_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved {len(merged)} reviews -> {detail_path}", flush=True)
    data.setdefault("logs",[]).insert(0,{
        "ran_at":run_time,"snap_date":snap_date,"yesterday":yesterday,
        "baseline_date":baseline_date,"success":success,
        "failed":len(failed),"failed_names":failed,
        "total_yesterday_reviews":len(merged),
    })
    data["logs"] = data["logs"][:50]
    data["last_updated"] = run_time
    save_data(data)
    print(f"  Saved reviews.json — {success}/36 branches", flush=True)

async def main():
    now_ist   = ist_now()
    snap_date = now_ist.date().strftime("%Y-%m-%d")
    yesterday = (now_ist - timedelta(days=1)).date().strftime("%Y-%m-%d")
    run_time  = datetime.now(timezone.utc).isoformat()
    print("=== Google Reviews Scraper ===")
    print(f"  Run time : {now_ist.strftime('%Y-%m-%d %H:%M IST')}")
    print(f"  Snap date: {snap_date}")
    print(f"  Yesterday: {yesterday}")
    print()
    results, success, failed = await run_all(snap_date, yesterday)
    print(f"\n=== Results: {success}/36 ===")
    if failed: print(f"  Failed: {', '.join(failed)}")
    if success == 0:
        print("FATAL: 0 branches succeeded.")
        sys.exit(1)
    save_results(results, success, failed, snap_date, yesterday, run_time)
    print("=== Done ===")

if __name__ == "__main__":
    try: asyncio.run(main())
    except Exception as e:
        print(f"FATAL: {e}"); traceback.print_exc(); sys.exit(1)

#!/usr/bin/env python3
"""
Live Tracker — fetches current review counts via Obscura CDP.
Saves live_data.json. Run via GitHub Actions workflow_dispatch.
"""
import asyncio, traceback, sys, json, re, shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST       = timedelta(hours=5, minutes=30)
DATA_FILE = Path(__file__).parent / "reviews.json"
LIVE_FILE = Path(__file__).parent / "live_data.json"
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

async def fetch_total(browser, branch):
    url = (
        f"https://www.google.com/maps/search/?api=1"
        f"&query={branch['name'].replace(' ','+')}"
        f"&query_place_id={branch['place_id']}"
    )
    page = None
    try:
        ctx = await browser.new_context(
            locale="en-IN", viewport={"width":1366,"height":768},
            extra_http_headers={"Accept-Language":"en-IN,en;q=0.9"},
        )
        page = await ctx.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}", lambda r: r.abort())
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2500)

        total = 0
        for sel in ['[aria-label*="review" i]','[aria-label*="Review"]']:
            locs = page.locator(sel)
            n = await locs.count()
            for i in range(min(n,15)):
                lbl = await get_attr(locs.nth(i), "aria-label")
                m = re.search(r"([\d,]+)\s*review", lbl, re.I)
                if m: total = int(m.group(1).replace(",","")); break
            if total: break

        if not total:
            for sel in ['button','span','div']:
                locs = page.locator(sel)
                n = await locs.count()
                for i in range(min(n,100)):
                    txt = await get_text(locs.nth(i))
                    m = re.search(r"^([\d,]+)\s*reviews?$", txt, re.I)
                    if m: total = int(m.group(1).replace(",","")); break
                if total: break

        stars = 0.0
        for sel in ['[aria-label*="Rated" i]','[aria-label*="star" i]']:
            locs = page.locator(sel)
            n = await locs.count()
            for i in range(min(n,10)):
                lbl = await get_attr(locs.nth(i), "aria-label")
                m = re.search(r"([1-5][.,]\d)", lbl)
                if m:
                    v = float(m.group(1).replace(",","."))
                    if 1.0 <= v <= 5.0: stars = v; break
            if stars: break

        await page.close(); await ctx.close()
        return total, stars
    except Exception as e:
        try:
            if page: await page.close()
        except Exception: pass
        return 0, 0.0

async def run_live():
    from playwright.async_api import async_playwright
    now_ist  = ist_now()
    run_time = now_ist.isoformat()
    today    = now_ist.date().strftime("%Y-%m-%d")

    base = {}
    if DATA_FILE.exists():
        try:
            d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            dates = sorted([x for x in d.get("daily",{}) if x <= today], reverse=True)
            base = d["daily"].get(dates[0],{}) if dates else {}
        except Exception: pass

    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        sem = asyncio.Semaphore(CONCURRENCY)

        async def fetch_one(branch):
            async with sem:
                bid = str(branch["id"])
                print(f"  [{branch['id']:02}/36] {branch['name']} ...", flush=True)
                total, stars = await fetch_total(browser, branch)
                if total == 0:
                    await asyncio.sleep(2)
                    total, stars = await fetch_total(browser, branch)
                baseline = base.get(bid,{}).get("total_snap",0)
                live_new = max(total - baseline, 0)
                results[bid] = {
                    "id":branch["id"],"name":branch["name"],"agm":branch["agm"],
                    "total":total,"stars":stars,"baseline":baseline,"live_new":live_new,
                }
                print(f"  {'✓' if total else '✗'} {branch['name']}: total={total} +{live_new} new", flush=True)
                await asyncio.sleep(0.3)

        await asyncio.gather(*[fetch_one(b) for b in BRANCHES])
        await browser.close()

    agm_summary = {}
    for bid, r in results.items():
        agm = r["agm"]
        if agm not in agm_summary:
            agm_summary[agm] = {"total_new":0,"branches":[]}
        agm_summary[agm]["total_new"] += r["live_new"]
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

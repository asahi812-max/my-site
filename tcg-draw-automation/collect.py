#!/usr/bin/env python3
"""Collect recent public-news candidates for TCG lottery announcements only."""
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "collected.json"
QUERIES = [
    'ポケカ 抽選 札幌',
    'ポケモンカード 抽選 北海道',
    'ワンピースカード 抽選 札幌',
    'ワンピカード 抽選 北海道',
    'ポケモンカード 抽選 応募締切',
    'ワンピースカード 抽選 応募締切',
]
CARD_TERMS = ("ポケモンカード", "ポケカ", "ポケットモンスター", "ONE PIECEカード", "ワンピースカード", "ワンピカード")
LOTTERY_TERMS = ("抽選", "応募", "当選", "予約", "販売方法", "受付")
HEADERS = {"User-Agent": "tcg-draw-candidate-collector/1.1 (+public RSS only)"}
MAX_AGE_DAYS = 60

def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()

def parse_date(value):
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def fetch(query):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "ja", "gl": "JP", "ceid": "JP:ja"
    })
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    root = ET.fromstring(data)
    rows = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        link = clean(item.findtext("link"))
        pubdate = clean(item.findtext("pubDate"))
        source = clean(item.findtext("source"))
        published_dt = parse_date(pubdate)
        if not title or not link or not published_dt:
            continue
        if published_dt < cutoff or published_dt > now + timedelta(days=1):
            continue
        if not any(term.lower() in title.lower() for term in CARD_TERMS):
            continue
        if not any(term in title for term in LOTTERY_TERMS):
            continue
        if "game" in query.lower() or "ポケ" in query:
            game = "pokemon"
        elif "ワンピ" in query:
            game = "onepiece"
        else:
            game = "未判定"
        # Prefer title evidence over the query when titles mention both games.
        has_pokemon = any(term.lower() in title.lower() for term in ("ポケモンカード", "ポケカ", "ポケットモンスター"))
        has_onepiece = any(term.lower() in title.lower() for term in ("one pieceカード", "ワンピースカード", "ワンピカード"))
        if has_pokemon and not has_onepiece:
            game = "pokemon"
        elif has_onepiece and not has_pokemon:
            game = "onepiece"
        elif has_pokemon and has_onepiece:
            game = "未判定"
        rows.append({
            "title": title,
            "url": link,
            "published": published_dt.isoformat(),
            "publisher": source or "未確認",
            "query": query,
            "game": game,
            "region_priority": "札幌・北海道関連候補" if ("札幌" in title or "北海道" in title) else "地域未確認",
            "deadline": "未確認",
            "announce": "未確認",
            "requirements": "元の告知で要確認（本人確認・名義条件・購入期限・応募対象地域）",
            "verification": "未確認：公式告知を開いて募集状況を確認",
            "collected_at": now.isoformat(),
        })
    return rows

def main():
    all_rows = {}
    errors = []
    for query in QUERIES:
        try:
            for row in fetch(query):
                all_rows[row["url"]] = row
        except Exception as exc:
            errors.append({"query": query, "error": str(exc)})
    rows = sorted(all_rows.values(), key=lambda x: (
        x["region_priority"] != "札幌・北海道関連候補",
        -(parse_date(x["published"]).timestamp() if parse_date(x["published"]) else 0),
    ))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "method": "Google News public RSS candidate search; recent title-filtered results",
        "note": "候補一覧です。募集の有効性・公式性・締切は保証しません。掲載日から60日以内の記事に限定しています。応募前に元の公式告知で確認してください。",
        "count": len(rows),
        "errors": errors,
        "items": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} recent candidates to {OUT}; {len(errors)} query errors.")

if __name__ == "__main__":
    main()

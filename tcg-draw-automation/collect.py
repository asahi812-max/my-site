#!/usr/bin/env python3
"""Collect public news RSS candidates; never submits lottery applications."""
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
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
TERMS = ("抽選", "応募", "当選", "販売", "ポケモンカード", "ポケカ", "ワンピースカード", "ワンピカード")
HEADERS = {"User-Agent": "tcg-draw-candidate-collector/1.0 (+public RSS only)"}

def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()

def fetch(query):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "ja", "gl": "JP", "ceid": "JP:ja"
    })
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    root = ET.fromstring(data)
    rows = []
    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        link = clean(item.findtext("link"))
        pubdate = clean(item.findtext("pubDate"))
        source = clean(item.findtext("source"))
        if not title or not link:
            continue
        if not any(term in title for term in TERMS):
            continue
        rows.append({
            "title": title,
            "url": link,
            "published": pubdate or "未確認",
            "publisher": source or "未確認",
            "query": query,
            "game": "pokemon" if ("ポケカ" in title or "ポケモンカード" in title) else ("onepiece" if ("ワンピ" in title or "ワンピースカード" in title) else "未判定"),
            "region_priority": "札幌・北海道関連候補" if ("札幌" in title or "北海道" in title) else "地域未確認",
            "deadline": "未確認",
            "announce": "未確認",
            "requirements": "元の告知で要確認（本人確認・名義条件・購入期限・応募対象地域）",
            "verification": "未確認：公式告知を開いて募集状況を確認",
            "collected_at": datetime.now(timezone.utc).isoformat(),
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
        0 if x["region_priority"] == "札幌・北海道関連候補" else 1,
        x["published"], x["title"]
    ), reverse=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "method": "Google News public RSS candidate search",
        "note": "候補一覧であり、募集の有効性・公式性・締切は保証しません。応募前に元の告知で確認してください。",
        "count": len(rows),
        "errors": errors,
        "items": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} unique candidates to {OUT}; {len(errors)} query errors.")

if __name__ == "__main__":
    main()

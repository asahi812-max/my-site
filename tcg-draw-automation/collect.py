#!/usr/bin/env python3
"""Collect recent, actionable TCG lottery announcement candidates from public RSS."""
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
    '"ポケモンカード" "抽選販売" 受付',
    '"ポケカ" "抽選応募" 受付',
    '"ポケモンカード" "応募締切" 抽選',
    '"ワンピースカード" "抽選販売" 受付',
    '"ワンピカード" "抽選応募" 受付',
    '"ワンピースカード" "応募締切" 抽選',
    'ポケカ 抽選 札幌 店舗',
    'ワンピースカード 抽選 北海道 店舗',
]
CARD_TERMS = ("ポケモンカード", "ポケカ", "ポケットモンスター", "ONE PIECEカード", "ワンピースカード", "ワンピカード")
LOTTERY_TERMS = ("抽選", "応募", "予約", "受付")
# Exclude guides, roundups, retrospective news and result articles rather than treating them as opportunities.
SUMMARY_TERMS = ("まとめ", "やり方", "方法", "探し方", "当選率", "当選確率", "結果発表", "当選結果", "再販情報", "攻略", "いつ？", "いつ？", "当選されたお客様", "発売日までに", "ランキング", "比較")
SUMMARY_PUBLISHERS = ("キャラグー", "SNKRDUNK", "スニーカーダンク", "シブヤ経済新聞", "Infoseek", "毎日新聞", "PR TIMES")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TCGDrawCandidateCollector/2.0)"}
MAX_AGE_DAYS = 14

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

def game_for(title, query):
    lower = title.lower()
    pokemon = any(t.lower() in lower for t in ("ポケモンカード", "ポケカ", "ポケットモンスター"))
    onepiece = any(t.lower() in lower for t in ("one pieceカード", "ワンピースカード", "ワンピカード"))
    if pokemon and not onepiece:
        return "pokemon"
    if onepiece and not pokemon:
        return "onepiece"
    if pokemon and onepiece:
        return "未判定"
    return "onepiece" if "ワンピ" in query else "pokemon"

def fetch(query):
    rss_url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "ja", "gl": "JP", "ceid": "JP:ja"
    })
    req = urllib.request.Request(rss_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        root = ET.fromstring(response.read())
    rows = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        link = clean(item.findtext("link"))
        published_dt = parse_date(clean(item.findtext("pubDate")))
        source = clean(item.findtext("source"))
        if not title or not link or not published_dt:
            continue
        if published_dt < cutoff or published_dt > now + timedelta(days=1):
            continue
        if not any(term.lower() in title.lower() for term in CARD_TERMS):
            continue
        if not any(term in title for term in LOTTERY_TERMS):
            continue
        if any(term in title for term in SUMMARY_TERMS):
            continue
        if any(term.lower() in source.lower() for term in SUMMARY_PUBLISHERS):
            continue
        # Do not present a result or post-purchase announcement as an application opportunity.
        if any(term in title for term in ("当選者", "ご当選", "購入期限", "お受け取り", "受け取り方法")):
            continue
        rows.append({
            "title": title,
            "url": link,
            "published": published_dt.isoformat(),
            "publisher": source or "未確認",
            "query": query,
            "game": game_for(title, query),
            "region_priority": "札幌・北海道関連候補" if ("札幌" in title or "北海道" in title) else "地域未確認",
            "deadline": "未確認",
            "announce": "未確認",
            "requirements": "申込ページ・応募期間・本人確認・名義条件・購入期限をリンク先で要確認",
            "verification": "未確認：リンク先で現在の受付状況を確認",
            "page_type": "公式・店舗告知候補" if any(x in source for x in ("オフィシャルサイト", "ポケモンセンター", "TSUTAYA", "ヨドバシ", "ビックカメラ", "ヤマダ", "イオン", "駿河屋", "カードラボ", "トレカ")) else "応募ページ未確認",
            "collected_at": now.isoformat(),
        })
    return rows

def main():
    all_rows = {}
    errors = []
    for query in QUERIES:
        try:
            for row in fetch(query):
                # Keep one copy per title so Google News variants of the same article do not multiply.
                key = re.sub(r"\W+", "", row["title"].lower())
                if key not in all_rows or row["published"] > all_rows[key]["published"]:
                    all_rows[key] = row
        except Exception as exc:
            errors.append({"query": query, "error": str(exc)})
    rows = sorted(all_rows.values(), key=lambda x: (
        x["region_priority"] != "札幌・北海道関連候補",
        x["page_type"] != "公式・店舗告知候補",
        -(parse_date(x["published"]).timestamp() if parse_date(x["published"]) else 0),
    ))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "method": "Google News RSS; 14-day recency limit; roundup/result-title exclusion",
        "note": "まとめ記事・結果記事を除外し、最近の公式・店舗告知候補を優先します。RSSのタイトルだけでは現在の受付中・締切日・申込フォーム直リンクを確定できないため、未確認の候補は応募前にリンク先で確認してください。",
        "count": len(rows),
        "errors": errors,
        "items": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} filtered candidates to {OUT}; {len(errors)} query errors.")

if __name__ == "__main__":
    main()

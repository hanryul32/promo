#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_update_ichannels.py

自動檢查 life/index.html 內通路王重點活動連結是否可達，
並依優先順序替換為可用連結，降低 404 風險。
"""

from __future__ import annotations

import argparse
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIFE_HTML = os.path.join(ROOT, "life", "index.html")


@dataclass
class Campaign:
    name: str
    audience_score: int
    candidates: list[str]
    known_urls: list[str]


CAMPAIGNS: list[Campaign] = [
    Campaign(
        name="奕心生醫科技",
        audience_score=95,
        candidates=[
            "https://www.ichannels.com.tw/ch-trueheartbio?ic=af000094185&uid=ich-9495&utm_source=line_group&utm_medium=owned_media&utm_campaign=ich-9495_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
            "https://www.trueheartbio.com.tw/?utm_source=hanryul32&utm_medium=referral&utm_campaign=promo_life_temp",
        ],
        known_urls=[
            "https://www.ichannels.com.tw/ch-trueheartbio?ic=af000094185&uid=ich-9495&utm_source=line_group&utm_medium=owned_media&utm_campaign=ich-9495_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
            "https://www.trueheartbio.com.tw/?utm_source=hanryul32&utm_medium=referral&utm_campaign=promo_life_temp",
        ],
    ),
    Campaign(
        name="佳瑪大罩杯內衣",
        audience_score=78,
        candidates=[
            "https://www.ichannels.com.tw/ch-jama?ic=af000094185&uid=ich-9848&utm_source=facebook_page&utm_medium=owned_media&utm_campaign=ich-9848_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
        known_urls=[
            "https://www.ichannels.com.tw/ch-jama?ic=af000094185&uid=ich-9848&utm_source=facebook_page&utm_medium=owned_media&utm_campaign=ich-9848_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
    ),
    Campaign(
        name="潮霖資產",
        audience_score=58,
        candidates=[
            "https://www.ichannels.com.tw/ch-chaolin?ic=af000094185&uid=ich-7744&utm_source=seo_blog&utm_medium=owned_media&utm_campaign=ich-7744_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
        known_urls=[
            "https://www.ichannels.com.tw/ch-chaolin?ic=af000094185&uid=ich-7744&utm_source=seo_blog&utm_medium=owned_media&utm_campaign=ich-7744_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
    ),
    Campaign(
        name="酷澎 Coupang",
        audience_score=88,
        candidates=[
            "https://www.ichannels.com.tw/ch-coupang?ic=af000094185&uid=ich-9611&utm_source=facebook_page&utm_medium=owned_media&utm_campaign=ich-9611_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
        known_urls=[
            "https://www.ichannels.com.tw/ch-coupang?ic=af000094185&uid=ich-9611&utm_source=facebook_page&utm_medium=owned_media&utm_campaign=ich-9611_%E9%80%A3%E5%81%87%E5%87%BA%E9%81%8A%E8%88%87%E6%98%A5%E5%AD%A3%E4%BF%9D%E9%A4%8A",
        ],
    ),
]


def check_url(url: str, timeout: float = 10.0) -> tuple[bool, int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = int(getattr(resp, "status", 200))
            final_url = resp.geturl()
            return code < 400, code, final_url
    except urllib.error.HTTPError as e:
        return False, int(e.code), url
    except Exception:
        return False, 0, url


def choose_best_url(campaign: Campaign) -> tuple[str, bool, int, str]:
    for u in campaign.candidates:
        ok, code, final_url = check_url(u)
        if ok:
            return u, True, code, final_url
    fallback = campaign.candidates[-1]
    ok, code, final_url = check_url(fallback)
    return fallback, ok, code, final_url


def replace_known_urls(html: str, old_urls: list[str], new_url: str) -> tuple[str, int]:
    replaced = 0
    for old in old_urls:
        count = html.count(old)
        if count:
            html = html.replace(old, new_url)
            replaced += count
    return html, replaced


def rank_campaigns(results: list[tuple[Campaign, str, bool, int, str]]) -> list[tuple[int, Campaign, str, int]]:
    ranked: list[tuple[int, Campaign, str, int]] = []
    for camp, selected, ok, code, _ in results:
        status_bonus = 30 if ok else -30
        ich_bonus = 20 if "ichannels.com.tw" in selected else 0
        score = camp.audience_score + status_bonus + ich_bonus
        ranked.append((score, camp, selected, code))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto refresh iChannels links in life/index.html")
    parser.add_argument("--dry-run", action="store_true", help="Only print decisions without writing file")
    args = parser.parse_args()

    if not os.path.exists(LIFE_HTML):
        print("[ERR] life/index.html not found")
        return 1

    with open(LIFE_HTML, encoding="utf-8") as f:
        html = f.read()

    results: list[tuple[Campaign, str, bool, int, str]] = []
    total_replaced = 0

    for camp in CAMPAIGNS:
        selected, ok, code, final_url = choose_best_url(camp)
        html, replaced = replace_known_urls(html, camp.known_urls, selected)
        total_replaced += replaced
        results.append((camp, selected, ok, code, final_url))
        print(f"[CHK] {camp.name}: status={code} ok={ok} selected={selected}")

    ranked = rank_campaigns(results)
    print("\n[TOP] Current best-fit campaigns")
    for i, (score, camp, selected, code) in enumerate(ranked[:5], start=1):
        print(f"  {i}. {camp.name} | score={score} | http={code} | {selected}")

    if args.dry_run:
        print(f"\n[DRY] replacements planned: {total_replaced}")
        return 0

    with open(LIFE_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[OK] written: {LIFE_HTML}")
    print(f"[OK] total replacements: {total_replaced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
将 adblock.json 转换为 Clash 规则格式的 reject.list

源文件结构:
{
  "version": 3,
  "rules": [
    {
      "domain_suffix": ["a.com", "b.com", ...],
      "domain": ["c.com", "d.com", ...]
    }
  ]
}

domain_suffix -> DOMAIN-SUFFIX,xxx
domain        -> DOMAIN,xxx

同一个键内部按源文件原始顺序输出；先输出 domain_suffix 全部条目，
再输出 domain 全部条目（如需调整顺序可修改 KEY_ORDER）。
"""

import json
import sys
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/jackszb/Ads-rule/main/rules/adblock.json"
OUTPUT_FILE = "reject.list"

# JSON 键 -> Clash 规则前缀 的映射，按此顺序写入输出文件
KEY_ORDER = [
    ("domain_suffix", "DOMAIN-SUFFIX"),
    ("domain", "DOMAIN"),
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "reject-list-builder"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_lines(data: dict) -> list[str]:
    lines: list[str] = []
    rules = data.get("rules", [])
    for rule in rules:
        for json_key, prefix in KEY_ORDER:
            values = rule.get(json_key)
            if not values:
                continue
            for domain in values:
                domain = domain.strip()
                if domain:
                    lines.append(f"{prefix},{domain}")
    return lines


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else SOURCE_URL
    print(f"Fetching source: {url}", file=sys.stderr)
    data = fetch_json(url)

    lines = build_lines(data)
    if not lines:
        print("No rules generated, aborting to avoid overwriting with empty file.", file=sys.stderr)
        return 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} rules to {OUTPUT_FILE}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

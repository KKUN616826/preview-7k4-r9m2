#!/usr/bin/env python3
"""Embed data/hero-demo.json into index.html's #heroDemoData script.

Run after scripts/export_hero_demo.py. The page needs no runtime JSON request;
the escaping matches what the former hero builder produced.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / 'data/hero-demo.json').read_text())
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    for char, escaped in [('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026')]:
        payload = payload.replace(char, escaped)
    page = ROOT / 'index.html'
    source = page.read_bytes().decode()
    source, count = re.subn(r'(<script id="heroDemoData" type="application/json">).*?(</script>)',
                            lambda m: m[1] + payload + m[2], source, count=1, flags=re.S)
    assert count == 1, 'index.html has no #heroDemoData script'
    page.write_bytes(source.encode())
    print('Embedded hero demo data.')


if __name__ == '__main__':
    main()

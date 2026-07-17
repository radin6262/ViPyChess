"""
Downloads the Wikipedia SVG chess pieces into:
assets/pieces/

Requires:
    pip install requests
"""

from pathlib import Path
import requests

import time

OUTPUT_DIR = Path("assets") / "pieces"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PIECES = {
    "wk.svg": "https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg",
    "wq.svg": "https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg",
    "wr.svg": "https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg",
    "wb.svg": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg",
    "wn.svg": "https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg",
    "wp.svg": "https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg",

    "bk.svg": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg",
    "bq.svg": "https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg",
    "br.svg": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg",
    "bb.svg": "https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg",
    "bn.svg": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg",
    "bp.svg": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg",
}
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}

def download_file(filename, url):
    path = OUTPUT_DIR / filename

    for attempt in range(5):
        try:
            print(f"Downloading {filename}...")

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=20,
            )

            if r.status_code == 429:
                wait = (attempt + 1) * 5
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue

            r.raise_for_status()

            path.write_bytes(r.content)

            print(f"✓ Saved -> {path}")

            time.sleep(2)          # <- delay every request
            return

        except Exception as e:
            print(e)
            time.sleep(3)

    print(f"✗ Failed: {filename}")

def main():
    print("Downloading chess SVGs...\n")

    for filename, url in PIECES.items():
        download_file(filename, url)

    print("\nDone!")


if __name__ == "__main__":
    main()
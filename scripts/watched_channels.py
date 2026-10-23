"""Record which channels Irek has watched recently, from a Google Takeout export.

Usage: python3 scripts/watched_channels.py <takeout zip(s) or watch-history.json> [--days N]

Reads YouTube watch history (JSON or HTML format) and writes the IDs of channels watched
in the last N days (default 90) to "watched" in youtube-channels.json.
update_youtube.py then shows only subscriptions on that list.

youtube-channels.json is public, so only channels the page could show anyway are
kept: subscriptions that match a topic and aren't excluded. Everything else in
the history stays on this machine. Reading subscriptions needs the API key, from
YT_API_KEY or ~/.config/irekromaniuk/yt_api_key (never stored in this repository).
"""
import html
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_youtube  # noqa: E402

CONFIG = Path(__file__).resolve().parent.parent / "youtube-channels.json"
KEY_FILE = Path.home() / ".config" / "irekromaniuk" / "yt_api_key"
CHANNEL = re.compile(r"youtube\.com/channel/(UC[\w-]{22})")


def parse_html(text):
    """Turn Takeout's HTML history into the same shape as its JSON history."""
    entries = []
    for cell in text.split('<div class="outer-cell')[1:]:
        m = re.search(r'youtube\.com/channel/(UC[\w-]{22})">[^<]*</a><br>([^<]+)<br>', cell)
        if not m:
            continue
        # e.g. "Oct 23, 2026, 12:16:43 PM EDT"; the time zone is dropped, which is close enough for a 90-day window.
        stamp = " ".join(html.unescape(m.group(2)).replace("\u202f", " ").split()[:5])
        try:
            when = datetime.strptime(stamp, "%b %d, %Y, %I:%M:%S %p").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        entries.append({
            "time": when.isoformat(),
            "subtitles": [{"url": "https://www.youtube.com/channel/" + m.group(1)}],
            "details": [{"name": "From Google Ads"}] if "From Google Ads" in cell else [],
        })
    return entries


def read(name, data):
    return parse_html(data.decode("utf-8")) if name.endswith(".html") else json.loads(data)


def load_history(paths):
    """A large export is split into several zips; the history is in one of them."""
    for path in paths:
        if not zipfile.is_zipfile(path):
            return read(path, Path(path).read_bytes())
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if re.search(r"/watch-history\.(json|html)$", n)]
            if names:
                return read(names[0], z.read(names[0]))
    sys.exit("No watch-history.json or watch-history.html in this export.")


def main():
    args = sys.argv[1:]
    days = 90
    if "--days" in args:
        i = args.index("--days")
        days = int(args[i + 1])
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    watched = {}
    for entry in load_history(args):
        if any(d.get("name") == "From Google Ads" for d in entry.get("details", [])):
            continue
        when = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
        if when < cutoff:
            continue
        for sub in entry.get("subtitles", []):
            m = CHANNEL.search(sub.get("url", ""))
            if m:
                watched[m.group(1)] = watched.get(m.group(1), 0) + 1

    cfg = json.loads(CONFIG.read_text())
    if not os.environ.get("YT_API_KEY") and KEY_FILE.exists():
        os.environ["YT_API_KEY"] = KEY_FILE.read_text().strip()
    include, exclude = cfg.get("include", {}), set(cfg.get("exclude", []))
    keep = sorted(
        ch["id"] for ch in update_youtube.subscriptions(cfg["channel_id"])
        if ch["id"] in watched and ch["id"] not in exclude
        and (ch["id"] in include or update_youtube.topic_for(ch, cfg["topics"])))
    cfg["watched"] = {"days": days, "updated": datetime.now(timezone.utc).date().isoformat(), "channels": keep}
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(watched)} channels watched in the last {days} days; "
          f"{len(keep)} of them are topic-matching subscriptions, written to {CONFIG.name}.")


if __name__ == "__main__":
    main()

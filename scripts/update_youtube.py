"""Refresh the "Channels I learn from" section of index.html.

Lists Irek's YouTube subscriptions, keeps channels whose title or description
matches a topic in youtube-channels.json, and writes each one's latest video
into index.html between the youtube:start and youtube:end markers.

Credentials come from the environment (never from this repository):
  YT_API_KEY                                  works when subscriptions are public
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN   OAuth, youtube.readonly scope

The latest video per channel comes from the channel's public RSS feed, which
uses no API quota. Standard library only.
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "youtube-channels.json"
PAGE = ROOT / "index.html"
START, END = "<!-- youtube:start -->", "<!-- youtube:end -->"
LIST_START, LIST_END = "<!-- youtube-list:start -->", "<!-- youtube-list:end -->"
NOTE_START, NOTE_END = "<!-- youtube-note:start -->", "<!-- youtube-note:end -->"
API = "https://www.googleapis.com/youtube/v3/"
FEED = "https://www.youtube.com/feeds/videos.xml?channel_id="
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}


def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        # Report the API's reason (e.g. subscriptionForbidden) without printing the URL, which holds the key.
        raise RuntimeError(f"{url.split('?')[0]}: HTTP {e.code}: {e.read().decode(errors='replace')[:500]}") from None


def auth(channel_id):
    """Return (extra query params, headers) for subscriptions.list."""
    if os.environ.get("YT_REFRESH_TOKEN"):
        body = urllib.parse.urlencode({
            "client_id": os.environ["YT_CLIENT_ID"],
            "client_secret": os.environ["YT_CLIENT_SECRET"],
            "refresh_token": os.environ["YT_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        }).encode()
        token = json.loads(fetch("https://oauth2.googleapis.com/token", body))["access_token"]
        return {"mine": "true"}, {"Authorization": "Bearer " + token}
    if os.environ.get("YT_API_KEY"):
        return {"channelId": channel_id, "key": os.environ["YT_API_KEY"]}, {}
    sys.exit("Set YT_API_KEY, or YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN.")


def subscriptions(channel_id):
    params, headers = auth(channel_id)
    subs, page = [], None
    while True:
        q = dict(params, part="snippet", maxResults=50, order="alphabetical")
        if page:
            q["pageToken"] = page
        data = json.loads(fetch(API + "subscriptions?" + urllib.parse.urlencode(q), headers=headers))
        for item in data["items"]:
            s = item["snippet"]
            if re.fullmatch(r"UC[\w-]{22}", s["resourceId"]["channelId"]):
                subs.append({"id": s["resourceId"]["channelId"], "title": s["title"], "description": s["description"]})
        page = data.get("nextPageToken")
        if not page:
            return subs


def topic_for(channel, topics):
    text = channel["title"] + " " + channel["description"]
    for topic, words in topics.items():
        if re.search(r"\b(" + "|".join(map(re.escape, words)) + r")\b", text, re.IGNORECASE):
            return topic
    return None


def latest_video(channel_id):
    """Newest non-Short upload from the channel's RSS feed, or None."""
    feed = ET.fromstring(fetch(FEED + channel_id))
    for entry in feed.findall("a:entry", NS):
        link = entry.find("a:link", NS).get("href", "")
        video_id = entry.find("yt:videoId", NS).text or ""
        if "/shorts/" in link or not re.fullmatch(r"[\w-]{11}", video_id):
            continue
        return {
            "id": video_id,
            "title": entry.find("a:title", NS).text,
            "published": entry.find("a:published", NS).text,
        }
    return None


def card(ch):
    v = ch["video"]
    title, name = html.escape(v["title"]), html.escape(ch["title"])
    return f"""          <article class="channel">
            <button class="yt-embed" type="button" data-video="{v['id']}" data-title="{title}" aria-label="Play: {title}">
              <img src="https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg" alt="" loading="lazy" width="320" height="180">
              <span class="yt-play" aria-hidden="true">▶</span>
            </button>
            <div class="channel-copy">
              <div class="project-meta"><span>{html.escape(ch['topic'])}</span><time datetime="{v['published'][:10]}">{v['published'][:10]}</time></div>
              <h3>{title}</h3>
              <a class="project-link" href="https://www.youtube.com/channel/{ch['id']}" target="_blank" rel="noreferrer">{name} <span aria-hidden="true">↗</span></a>
            </div>
          </article>"""


def channel_list(channels, topics):
    """Every matching channel, grouped by topic in config order, A–Z within each."""
    groups = []
    for topic in list(topics) + sorted({c["topic"] for c in channels} - set(topics)):
        names = sorted((c for c in channels if c["topic"] == topic), key=lambda c: c["title"].lower())
        if not names:
            continue
        links = "".join(
            f'<a href="https://www.youtube.com/channel/{c["id"]}" target="_blank" rel="noreferrer">{html.escape(c["title"].strip())}</a>'
            for c in names)
        groups.append(f'            <div class="channel-group"><h3>{html.escape(topic)} <span>{len(names)}</span></h3><p>{links}</p></div>')
    return "\n" + "\n".join(groups) + "\n          "


def replace_between(page, start, end, block):
    a, b = page.index(start) + len(start), page.index(end)
    return page[:a] + block + page[b:]


def main():
    cfg = json.loads(CONFIG.read_text())
    include, exclude = cfg.get("include", {}), set(cfg.get("exclude", []))
    # Set by watched_channels.py from a Takeout export; without it, all subscriptions are considered.
    watched = set(cfg["watched"]["channels"]) if cfg.get("watched") else None
    picked, matched = [], []
    for ch in subscriptions(cfg["channel_id"]):
        if ch["id"] in exclude or (watched is not None and ch["id"] not in watched):
            continue
        ch["topic"] = include.get(ch["id"]) or topic_for(ch, cfg["topics"])
        if not ch["topic"]:
            continue
        matched.append(ch)
        try:
            ch["video"] = latest_video(ch["id"])
        except Exception as e:  # one broken feed shouldn't drop the whole list
            print(f"skip {ch['title']}: {e}", file=sys.stderr)
            continue
        if ch["video"]:
            picked.append(ch)
    if not picked:
        sys.exit("No matching channels found; leaving index.html unchanged.")
    # Take turns between topics (newest first within each), so frequent AI posters
    # don't crowd out the security and networking channels.
    # Inactive channels stay in the full list but don't get a video card.
    cutoff = (datetime.now(timezone.utc) - timedelta(days=cfg.get("max_video_age_days", 365))).isoformat()
    picked = [c for c in picked if c["video"]["published"] >= cutoff]
    picked.sort(key=lambda c: c["video"]["published"], reverse=True)
    by_topic = {}
    for c in picked:
        by_topic.setdefault(c["topic"], []).append(c)
    rounds = [c for group in zip_longest(*by_topic.values()) for c in group if c]
    picked = rounds[: cfg.get("max_channels", 12)]

    page = PAGE.read_text()
    page = replace_between(page, START, END, "\n" + "\n".join(card(c) for c in picked) + "\n          ")
    page = replace_between(page, LIST_START, LIST_END, channel_list(matched, cfg["topics"]))
    # Name only the topics that have channels, e.g. "AI and security".
    names = {"AI": "AI", "Security": "security", "Network": "networking"}
    shown = [names.get(tp, tp) for tp in cfg["topics"] if any(c["topic"] == tp for c in matched)]
    topics = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + (", and " if len(shown) > 2 else " and ") + shown[-1]
    if cfg.get("watched"):
        note = (f"YouTube channels on {topics} that I subscribe to and have watched in the last "
                f"{cfg['watched']['days']} days, with a recent video from each topic and the full list below. "
                f"It updates automatically every week.")
    else:
        note = (f"YouTube channels I subscribe to on {topics}, with a recent video from each topic "
                "and the full list below. It updates automatically every week.")
    page = replace_between(page, NOTE_START, NOTE_END, note)
    PAGE.write_text(page)
    for c in picked:
        print(f"{c['topic']:9} {c['title']} — {c['video']['title']}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))

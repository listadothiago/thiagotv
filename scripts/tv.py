#!/usr/bin/env python3
"""ThiagoTV playlist manager.

The playlist is a plain JSON file, so it can always be edited by hand. This
script exists so the common operations (add a video, retag it, reorder the
schedule) don't require getting the JSON right by hand every time.

Usage:
    tv.py add <url-or-id> [--title TITLE] [--tags music,film] [--date YYYY-MM-DD]
    tv.py list [--tag TAG]
    tv.py tag <url-or-id> --tags music,film      # replace tags
    tv.py tag <url-or-id> --add-tags vignette    # append tags
    tv.py rm <url-or-id>
    tv.py date <url-or-id> <YYYY-MM-DD>          # change schedule position
"""

import argparse
import datetime as dt
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

PLAYLIST = Path(__file__).resolve().parent.parent / "playlist.json"

# Every shape of YouTube link worth pasting: watch URLs, share links, shorts,
# embeds, and a bare 11-character id.
ID_PATTERNS = [
    r"(?:youtube\.com/watch\?(?:.*&)?v=)([A-Za-z0-9_-]{11})",
    r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
    r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
    r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
    r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
    r"^([A-Za-z0-9_-]{11})$",
]


def extract_id(text):
    text = text.strip()
    for pattern in ID_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    raise SystemExit(
        f"Could not find a YouTube video id in: {text!r}\n"
        "Expected something like https://www.youtube.com/watch?v=dQw4w9WgXcQ "
        "or just the 11-character id."
    )


def fetch_title(video_id):
    """Ask YouTube for the video's own title via oEmbed.

    oEmbed needs no API key, which keeps the whole project deployable as static
    files. A failure here is not fatal -- the caller falls back to asking for a
    title -- but it also tells us something useful: oEmbed returning 401/404 is
    a strong hint the video is private or deleted and would not play anyway.
    """
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.load(response)["title"], None
    except urllib.error.HTTPError as exc:
        reason = {401: "private or embedding-disabled", 404: "not found"}.get(
            exc.code, f"HTTP {exc.code}"
        )
        return None, reason
    except Exception as exc:  # network hiccup, DNS, timeout
        return None, str(exc)


def load():
    if not PLAYLIST.exists():
        return {"playlist": []}
    try:
        data = json.loads(PLAYLIST.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{PLAYLIST} is not valid JSON ({exc}). Fix it by hand first.")
    data.setdefault("playlist", [])
    return data


def save(data):
    PLAYLIST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def find(data, video_id):
    for entry in data["playlist"]:
        if entry.get("videoId") == video_id:
            return entry
    return None


def split_tags(raw):
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def cmd_add(args):
    video_id = extract_id(args.target)
    data = load()

    if find(data, video_id):
        raise SystemExit(f"{video_id} is already in the playlist. Use `tag` or `rm` instead.")

    title = args.title
    if not title:
        title, problem = fetch_title(video_id)
        if not title:
            raise SystemExit(
                f"Could not fetch a title for {video_id} ({problem}).\n"
                "Pass one explicitly with --title, or double-check the video is public."
            )

    entry = {
        "videoId": video_id,
        "title": title,
        "tags": split_tags(args.tags),
        "addedAt": args.date or dt.date.today().isoformat(),
    }
    data["playlist"].append(entry)
    save(data)
    print(f"Added: {entry['title']}")
    print(f"  id   {entry['videoId']}")
    print(f"  tags {', '.join(entry['tags']) or '(none)'}")
    print(f"  date {entry['addedAt']}")


def cmd_list(args):
    data = load()
    items = data["playlist"]
    if args.tag:
        items = [v for v in items if args.tag.lower() in [t.lower() for t in v.get("tags", [])]]
    if not items:
        print("(nothing matches)")
        return
    for entry in sorted(items, key=lambda v: v.get("addedAt", ""), reverse=True):
        tags = ", ".join(entry.get("tags", [])) or "-"
        print(f"{entry.get('addedAt', '?'):<12} {entry.get('title', '?'):<45} [{tags}]")


def cmd_tag(args):
    video_id = extract_id(args.target)
    data = load()
    entry = find(data, video_id)
    if not entry:
        raise SystemExit(f"{video_id} is not in the playlist.")

    if args.add_tags:
        existing = entry.get("tags", [])
        for tag in split_tags(args.add_tags):
            if tag not in existing:
                existing.append(tag)
        entry["tags"] = existing
    elif args.tags is not None:
        entry["tags"] = split_tags(args.tags)
    else:
        raise SystemExit("Pass --tags to replace tags, or --add-tags to append.")

    save(data)
    print(f"{entry['title']} -> [{', '.join(entry['tags']) or 'none'}]")


def cmd_rm(args):
    video_id = extract_id(args.target)
    data = load()
    entry = find(data, video_id)
    if not entry:
        raise SystemExit(f"{video_id} is not in the playlist.")
    data["playlist"] = [v for v in data["playlist"] if v.get("videoId") != video_id]
    save(data)
    print(f"Removed: {entry.get('title', video_id)}")


def cmd_date(args):
    video_id = extract_id(args.target)
    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        raise SystemExit(f"{args.date!r} is not a YYYY-MM-DD date.")
    data = load()
    entry = find(data, video_id)
    if not entry:
        raise SystemExit(f"{video_id} is not in the playlist.")
    entry["addedAt"] = args.date
    save(data)
    print(f"{entry['title']} now scheduled {args.date}")


def main():
    parser = argparse.ArgumentParser(description="Manage the ThiagoTV playlist.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add a video")
    p.add_argument("target", help="YouTube URL or 11-character video id")
    p.add_argument("--title", help="override the title (default: fetched from YouTube)")
    p.add_argument("--tags", help="comma-separated channel tags, e.g. music,vignette")
    p.add_argument("--date", help="schedule date YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="show the playlist")
    p.add_argument("--tag", help="only show videos with this tag")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("tag", help="change a video's channel tags")
    p.add_argument("target")
    p.add_argument("--tags", help="replace all tags with this comma-separated list")
    p.add_argument("--add-tags", help="append these tags")
    p.set_defaults(func=cmd_tag)

    p = sub.add_parser("rm", help="remove a video")
    p.add_argument("target")
    p.set_defaults(func=cmd_rm)

    p = sub.add_parser("date", help="change a video's schedule date")
    p.add_argument("target")
    p.add_argument("date")
    p.set_defaults(func=cmd_date)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

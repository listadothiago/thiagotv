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

    tv.py psa set "text"  [--hours N]            # post to the PSA channel
    tv.py psa show                               # what's on air, and for how long
    tv.py psa clear                              # pull it early
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


DOSSIER_FIELDS = ("summary", "relevance", "controversy")


def cmd_doc(args):
    video_id = extract_id(args.target)
    data = load()
    entry = find(data, video_id)
    if not entry:
        raise SystemExit(f"{video_id} is not in the playlist.")

    given = {f: getattr(args, f) for f in DOSSIER_FIELDS if getattr(args, f) is not None}

    if args.clear:
        entry.pop("dossier", None)
        save(data)
        print(f"Cleared notes for: {entry['title']}")
        return

    if not given:
        doc = entry.get("dossier") or {}
        print(entry["title"])
        if not doc:
            print("  (no notes on file)")
            return
        for field in DOSSIER_FIELDS:
            if doc.get(field):
                print(f"\n  [{field}]")
                for line in doc[field].splitlines():
                    print(f"  {line}")
        return

    doc = entry.get("dossier") or {}
    for field, value in given.items():
        value = value.strip()
        if value:
            doc[field] = value
        else:
            doc.pop(field, None)
    entry["dossier"] = doc
    save(data)
    print(f"Notes updated for: {entry['title']}")
    print(f"  sections on file: {', '.join(f for f in DOSSIER_FIELDS if doc.get(f)) or '(none)'}")


DEFAULT_PSA_HOURS = 24


def psa_status(psa):
    """Return (is_live, hours_remaining) for a PSA record."""
    if not psa or not psa.get("text"):
        return False, 0.0
    try:
        posted = dt.datetime.fromisoformat(psa["postedAt"].replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return False, 0.0
    hours = float(psa.get("hours", DEFAULT_PSA_HOURS))
    age = (dt.datetime.now(dt.timezone.utc) - posted).total_seconds() / 3600
    return age < hours, max(0.0, hours - age)


def cmd_psa_set(args):
    text = args.text.strip()
    if not text:
        raise SystemExit("The bulletin is empty.")
    if args.hours <= 0:
        raise SystemExit("--hours must be positive.")

    data = load()
    data["psa"] = {
        "text": text,
        "postedAt": dt.datetime.now(dt.timezone.utc)
                      .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "hours": args.hours,
    }
    save(data)
    print(f"On air for the next {args.hours}h:")
    print(f"  {text}")


def cmd_psa_show(args):
    data = load()
    psa = data.get("psa")
    if not psa or not psa.get("text"):
        print("Nothing on the PSA channel.")
        return
    live, remaining = psa_status(psa)
    print(f'"{psa["text"]}"')
    if live:
        print(f"  on air, {remaining:.1f}h remaining (posted {psa['postedAt']})")
    else:
        print(f"  expired -- no longer shown (posted {psa['postedAt']})")


def cmd_psa_clear(args):
    data = load()
    psa = data.get("psa")
    if not psa or not psa.get("text"):
        print("Nothing to clear.")
        return
    data.pop("psa", None)
    save(data)
    print(f'Pulled: "{psa["text"]}"')


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

    p = sub.add_parser("doc", help="programme notes shown under the set")
    p.add_argument("target")
    p.add_argument("--summary", help="what the video is")
    p.add_argument("--relevance", help="why it matters culturally")
    p.add_argument("--controversy", help="disputes or criticism, if any")
    p.add_argument("--clear", action="store_true", help="remove all notes")
    p.set_defaults(func=cmd_doc)

    p = sub.add_parser("psa", help="the text-only announcement channel")
    psa_sub = p.add_subparsers(dest="psa_command", required=True)

    q = psa_sub.add_parser("set", help="post a bulletin (replaces any current one)")
    q.add_argument("text", help="the paragraph to display")
    q.add_argument("--hours", type=float, default=DEFAULT_PSA_HOURS,
                   help=f"how long it stays on air (default {DEFAULT_PSA_HOURS})")
    q.set_defaults(func=cmd_psa_set)

    q = psa_sub.add_parser("show", help="what's on air and for how long")
    q.set_defaults(func=cmd_psa_show)

    q = psa_sub.add_parser("clear", help="pull the bulletin early")
    q.set_defaults(func=cmd_psa_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

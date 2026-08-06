---
name: thiagotv
description: Manage the ThiagoTV playlist and its channel lineup — add YouTube videos, tag them onto channels (music, film, vignette), schedule what airs when, remove videos, or audit the lineup. Use this skill whenever the user mentions ThiagoTV, adding or scheduling a video, tagging or labelling videos, channels, or the playlist, even in passing and even if they don't name the file — for example "add this to the TV", "put this on the film channel", "what's airing Friday", "tag that one as a vignette", or when they paste a bare YouTube link into a conversation about the TV.
---

# ThiagoTV playlist

ThiagoTV is a static retro-TV page that plays a YouTube playlist. Everything it
shows comes from `playlist.json` at the project root. There is no database and no
YouTube API key — the file *is* the schedule.

## The mental model: it's a TV station, not a playlist

The reason the data looks the way it does is that the user runs this like a small
broadcaster. Two fields carry that:

- **`tags`** decide which channels a video appears on. A video can be on several.
- **`addedAt`** decides where it sits in the running order on the default *Latest*
  channel, which sorts newest first.

So `addedAt` is really an airdate, not a bookkeeping timestamp. If the user says
"this goes out Friday night", set `addedAt` to that Friday — the video then leads
the Latest channel from that day. Backdating and post-dating are both legitimate
and normal here; don't quietly default to today when the user has described a
slot.

The channels wired into the page are `latest`, `random`, `music`, `films`,
`nature`, `comedy`, and `vignette`. Latest and random draw on everything; the
rest filter by the matching tag. Check the `CHANNELS` array in `index.html` for
the live list rather than trusting this sentence — it's the kind of thing that
drifts.

## Use the script

`scripts/tv.py` handles the JSON so you don't have to hand-edit it. Run it from
the project root.

```
python3 scripts/tv.py add <url-or-id> [--title T] [--tags music,film] [--date YYYY-MM-DD]
python3 scripts/tv.py list [--tag TAG]
python3 scripts/tv.py tag <url-or-id> --tags music,film      # replace
python3 scripts/tv.py tag <url-or-id> --add-tags vignette    # append
python3 scripts/tv.py rm <url-or-id>
python3 scripts/tv.py date <url-or-id> <YYYY-MM-DD>
```

`add` accepts any YouTube link shape (watch, youtu.be, shorts, embed) or a bare
11-character id, and fetches the real title from YouTube automatically. Only pass
`--title` when the user wants something different from the official title — a
station-style name like "Friday Night Sci-Fi: Solaris" is often what they're
after, so offer it when the context suggests a themed slot.

## Working with the user

**Don't interrogate them.** A link plus "add this" is enough to act on. Infer tags
from what the video obviously is and from how they described it, apply them, and
say what you chose — it's one command to change. Asking a question per field turns
a five-second task into a form.

**Do ask when the airdate is genuinely ambiguous** and the stakes are real: "put
this on for Friday" is clear, but if they describe a scheduling intent you can't
map to a date, check rather than guess, because a wrong `addedAt` silently changes
what the front page shows.

**New tag, new channel.** Tags are free-form in the data, but a tag only becomes a
watchable channel once it's in the `CHANNELS` array in `index.html`. If the
user introduces a tag that isn't there yet (say `documentary`), add the entry to
that array too, otherwise they'll tag videos that nothing can tune to. New
channels other than Latest should use `order: 'shuffle'`.

**Adding several at once** is fine — loop the `add` command. Report them as a
short list at the end rather than narrating each one.

## Availability is the page's problem, not yours

Don't try to verify that a video will play before adding it. The player already
handles this: it watches whether each video actually starts, and silently skips
any that don't — removed, private, embedding-disabled, or region-blocked. That
check has to live at playback time because a video that works today can break
next month.

The one signal worth passing on: if `add` fails because YouTube's oEmbed lookup
returned "private or embedding-disabled" or "not found", the video probably won't
play on the site either. Tell the user that rather than working around it with a
manual `--title`.

## After changing the playlist

The page reads `playlist.json` with `cache: 'no-store'`, so a browser refresh is
all that's needed locally — no rebuild, no restart. If the user is running the
local server (`python3 -m http.server 8000` in the project root), tell them to
refresh `http://localhost:8000`.

## Publishing

The site is hosted on GitHub Pages off the `main` branch, so a playlist change
isn't live until it's pushed:

```
./scripts/publish.sh "add a banger to the music channel"
```

Offer to publish after making changes, but don't do it unprompted — pushing is
what makes the change public, and the user may be queuing up several edits
before they want any of it to go out.

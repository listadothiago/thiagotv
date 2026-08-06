# ThiagoTV

A retro television set that broadcasts a YouTube playlist. Two static files, no
build step, no backend, no API key.

- `index.html` — the set itself: player, channel dial, off-air cards
- `playlist.json` — the schedule

Everything else in this repo is for running the station, not serving it.

## Watching it locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. The plain `file://` route does not work —
YouTube's player needs a real origin.

## Running the station

`scripts/tv.py` edits `playlist.json` so you don't have to.

```bash
python3 scripts/tv.py add <url-or-id> [--title T] [--tags music,films] [--date YYYY-MM-DD]
python3 scripts/tv.py list [--tag TAG]
python3 scripts/tv.py tag <url-or-id> --tags music        # replace tags
python3 scripts/tv.py tag <url-or-id> --add-tags vignette # append
python3 scripts/tv.py rm <url-or-id>
python3 scripts/tv.py date <url-or-id> <YYYY-MM-DD>
```

Titles are fetched from YouTube automatically. Any link shape works — watch,
youtu.be, shorts, embed — or a bare video id.

## The Bulletin channel

One channel carries text instead of video — a short announcement that expires on
its own.

```bash
python3 scripts/tv.py psa set "Friday sci-fi starts at 9." --hours 24
python3 scripts/tv.py psa show
python3 scripts/tv.py psa clear
```

Expiry is evaluated in the viewer's browser, so a bulletin ages out with nothing
running server-side. The text stays in `playlist.json` until cleared; it just
stops being broadcast.

## How the station works

**Tags are channels.** A video's `tags` decide which channels carry it. A tag
only becomes a watchable channel once it also appears in the `CHANNELS` array in
`index.html`; a tag without a channel entry is invisible.

**`addedAt` is an airdate.** The default *Latest* channel sorts newest first, so
whatever you posted most recently is what a visitor sees when the set switches
on. Backdate or post-date freely — it's a schedule, not a timestamp.

**Channels remember where you were.** Each channel keeps its own running order
and cursor for the session. Tuning away burns the video you were on, so coming
back lands on the next one: the channel behaves as though it kept broadcasting
while you were elsewhere. Once a channel has played everything it carries it
signs off, and starts a fresh shuffle next time you tune in.

**Broken videos are skipped automatically.** The player judges a video by whether
it actually starts, not by the error code YouTube reports — YouTube fires error
153 on perfectly healthy videos, so trusting codes would blank the whole
playlist. Anything that never starts (deleted, private, embedding-disabled,
region-blocked) is dropped from every channel for that session. This has to
happen at playback time because a video that works today can break next month.

## Publishing

The site is `index.html` and `playlist.json`. Push to the `main` branch and
GitHub Pages serves them.

```bash
python3 scripts/tv.py add "https://youtu.be/..." --tags music
./scripts/publish.sh "add a banger to the music channel"
```

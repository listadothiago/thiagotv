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

Two flags are worth setting deliberately when adding a channel:

- `repeat: false` — the channel carries only what this viewer hasn't seen and
  goes to a card when they're caught up. Right for a channel whose promise is
  newness; wrong for a genre channel, which would switch itself off.
- `resume: true` — the channel remembers how far into a video the viewer got
  and picks it up there, capped at six resumes. Worth setting for anything
  long-form (films, documentaries, full concerts); pointless for short clips.

**Adding several at once** is fine — loop the `add` command. Report them as a
short list at the end rather than narrating each one.

## Programme notes

Each video can carry notes: what it is, why it matters, and any documented
controversy. They don't appear on the front page — the television is the whole
of the front page — but they are published as `v/<id>.html`, one page per video,
linked from the programme guide. Those pages are what search engines and LLM
crawlers actually read, so the notes are the site's entire text presence.

```
python3 scripts/tv.py doc <url-or-id> --summary "..." --relevance "..." --controversy "..."
python3 scripts/tv.py doc <url-or-id>            # print what's on file
python3 scripts/tv.py doc <url-or-id> --clear
```

All three sections are optional and can be written separately; passing one leaves
the others alone. Use `\n\n` inside a value for paragraph breaks.

**Writing these is the actual work, and it's yours.** When the user adds a video,
offer to write its notes. What makes them worth reading:

- **Summary**: what the thing *is*, concretely — who made it, when, what it
  sounds or looks like. Not a plot recap and not marketing copy.
- **Why it matters**: the honest cultural claim. If a video is simply a fun
  video with no wider significance, say nothing rather than inflating it; an
  empty section is better than a manufactured one.
- **Controversy**: only if something real and documented happened. Leave it out
  otherwise. This section is rendered with a marked margin, so it reads as a
  flagged note and shouldn't be used for trivia.

**Don't invent facts.** These notes are published under the user's name on a
public site. If you aren't confident about a date, a chart position, or who did
what, either leave it out or say plainly that you're unsure and let the user
confirm. A vague sentence that's true beats a specific one that's wrong. If you
genuinely don't know a video, say so and ask rather than producing
authoritative-sounding filler.

## The Bulletin channel

One channel carries no video: **Bulletin** shows a paragraph of text the user
posts, and it expires on its own.

```
python3 scripts/tv.py psa set "text" [--hours N]   # default 24h
python3 scripts/tv.py psa show                     # what's on air, time left
python3 scripts/tv.py psa clear                    # pull it early
```

There is only ever one bulletin — `set` replaces whatever was there. When the
user asks to change or correct a bulletin, just `set` the new text.

**Expiry is decided in the viewer's browser**, not by anything deleting the
record. The text stays in `playlist.json` until cleared but stops broadcasting
once it's older than its window, which is how a bulletin can age out on a site
with nothing running server-side. So an expired bulletin sitting in the file is
normal, not a bug — though `psa clear` is worth running if the text is stale
enough to be confusing to anyone reading the repo.

**Write it as broadcast copy.** It appears as a caption slide on a TV, not as a
web page: a few sentences at most, no markdown, no links (they aren't
clickable), no headings. If the user gives you something long or link-heavy,
say so and offer a trimmed version rather than posting something that overflows
the screen.

**Watch the tone.** The user talks about this project playfully, and the
bulletin is the station's voice. Match how they phrased the request rather than
formalising it.

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

## Publishing is part of the job

The site is hosted on GitHub Pages off the `main` branch, so a change that isn't
pushed isn't real — it only exists on this machine. The user has asked for
publishing to be automatic, so **finish every playlist or channel change by
running the publish script**:

```
./scripts/publish.sh "add a banger to the music channel"
```

Write the message as a short description of what actually changed, the way a
station log would read — "add two nature shorts", "retire the starter videos",
"new comedy channel". It becomes the commit message and is the only history of
how the schedule evolved.

Batch first, publish once. If the user is adding several videos across a few
messages, it's fine to publish after each — but when you're handling several in
one go, make all the edits and then publish a single time rather than pushing
per video.

Two things to still stop for:

- **Deletions.** Removing videos is easy to publish and awkward to walk back.
  Make the removal, say what went, and confirm before pushing that one.
- **A failed push.** Don't retry blindly or force. Report what git said — an
  auth failure, a rejected non-fast-forward, or no network are all different
  problems with different fixes, and guessing makes it worse.

Tell the user the change is live and that Pages takes a minute or so to rebuild.

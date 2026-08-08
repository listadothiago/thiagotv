# ThiagoTV — pending

Things waiting on a decision or on an account only Thiago has. Kept here so they
survive between sessions. Detail on the SEO side lives in [SEO-PLAN.md](SEO-PLAN.md).

## Needs Thiago — blocked, nothing can proceed without it

- [ ] **Analytics: pick one.** Recommendation is Vercel Analytics — free on the
      Hobby plan, one line, sets no cookies, so no consent banner on a site that
      currently sets none at all. Google Analytics 4 is deeper but brings cookies
      and, realistically in the EU, a banner. If GA anyway: need the measurement
      ID (`G-XXXXXXX`), and it goes in **both** `index.html` and
      `scripts/build.py` so the generated pages carry it too.
- [ ] **Google Search Console.** Verify ownership, then submit
      `https://thiagotv.vercel.app/sitemap.xml`. Highest-value single action for
      getting indexed; roughly ten minutes. Needs Thiago's Google account.
- [ ] **Bing Webmaster Tools.** Same again. Feeds several other engines and some
      AI products.
- [ ] **Custom domain: yes or no, and which.** Free to attach on Vercel. A real
      domain is worth more for trust than `thiagotv.vercel.app`.

## Needs Thiago — facts I can't confirm

Notes are deliberately left blank rather than filled with plausible invention.
Give me a line on any of these and I'll write them properly.

- [ ] **Films (9 without notes):** Crossworlds, The 13th Floor, Cyborg 2087,
      The Day Time Ended, The Langoliers, The Bat, Hercules in New York,
      Alien Vessel, St. Elmo's Fire is done.
- [ ] **Music:** Fadinha do Brasil feat. Robotron — don't know it.

Resolved: Carnival of Souls now has a full article, and it addresses the
suspect "Wes Craven" credit on the upload rather than picking a side silently.

## Decided, not yet built

- [ ] **Channel pages should be able to carry their own article.** They only
      list programmes today. This is the right answer for Ads, Cartoon and Drag
      (344 videos): one substantial piece per channel beats 344 thin pages about
      individual commercials, Jem episodes and lip syncs.
- [ ] **`llms.txt`** — emerging convention, cheap to generate from
      `playlist.json` in `build.py`. Low certainty of payoff, low cost.
- [ ] **Notes backlog, in priority order:** finish films → music Tier A
      (canonical records with real history) → history (25, individually
      substantial) → comedy/nature/vignette (small) → channel-level articles for
      ads/cartoon/drag. Do **not** attempt all 500+; thin or invented pages are
      worse than none.

## Known limits — not fixable, recorded so they aren't re-litigated

- **No in-page Chromecast button.** Screen and tab mirroring are browser-level;
  no web API lets a page start them. The Presentation API only reaches a
  Chromecast through a registered receiver app and has no mobile browser
  support. Desktop Chrome users can cast the tab from the browser's own menu.
- **Autoplay with sound** requires a user gesture. Solved by the power switch:
  the set starts off, and switching it on is the gesture that earns the audio.

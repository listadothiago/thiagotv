# ThiagoTV — SEO, analytics and content plan

Working document. Update it as things get done; it exists so the plan survives
between sessions.

- Live: <https://thiagotv.vercel.app>
- Repo: <https://github.com/listadothiago/thiagotv>

## Where things stand

Measured 2026-08-07, not estimated:

| Channel | Videos | With notes | Gap |
|---|---:|---:|---:|
| music | 141 | 18 | **123** |
| ads | 127 | 0 | 127 |
| cartoon | 119 | 2 | 117 |
| drag | 101 | 1 | 100 |
| history | 25 | 0 | 25 |
| films | 19 | 9 | **10** |
| comedy | 9 | 1 | 8 |
| nature | 5 | 0 | 5 |
| vignette | 4 | 1 | 3 |
| **Total** | **547** | **30** | **517** |

**Films is not finished** — 9 of 19. The ten without notes are the ones whose
titles are ambiguous or whose details I could not confirm (see "Blocked" below).

What already exists and works:

- `v/<id>.html` — a page per video, all 547, with `<title>`, meta description,
  OpenGraph, Twitter card, schema.org `VideoObject`, and now the video embedded
- `c/<tag>.html` — a page per channel, 9 of them
- `guide.html` — calendar archive, links to everything
- `sitemap.xml` — every URL, regenerated on each publish
- `robots.txt` — allows everyone, names GPTBot / ClaudeBot / PerplexityBot
- Canonical URLs, absolute, pointing at the Vercel domain

## 1. Analytics — decision needed

Google Analytics is not the obvious choice here and this should be decided
deliberately, because it is the first third-party script the site would carry.

| | Google Analytics 4 | Vercel Analytics | Plausible / Fathom |
|---|---|---|---|
| Cost | free | free on Hobby | paid (~$9/mo) |
| Setup | script + measurement ID | one line, same platform | script + account |
| Cookies | yes | no | no |
| Consent banner needed in EU | yes, realistically | no | no |
| Data detail | very deep | basic (views, referrers, paths) | middle |
| Blocked by ad-blockers | often | less | less |

**Recommendation: start with Vercel Analytics**, and add GA only if a specific
question comes up that it can't answer. Reasons: the site currently sets no
cookies at all, and adding GA means either a consent banner on a page that is
otherwise just a television, or a compliance problem. Vercel Analytics answers
the only questions that matter right now — is anyone arriving, and from where.

If GA is wanted anyway, it needs: a GA4 property, the measurement ID (`G-XXXX`),
the gtag snippet in `index.html` **and** in `scripts/build.py` so the generated
pages carry it too, plus a consent decision.

**Blocked on:** which one, and the measurement ID if GA.

## 2. Getting crawled

Ordered by effort-to-effect.

1. **Google Search Console** — verify ownership (DNS record or an HTML file at
   the root; Vercel makes the file route trivial), then submit
   `https://thiagotv.vercel.app/sitemap.xml`. This is the single highest-value
   action and takes about ten minutes. **Blocked on:** Thiago's Google account.
2. **Bing Webmaster Tools** — same again; it also feeds several other engines
   and some AI products.
3. **Check indexing after a week or two.** `site:thiagotv.vercel.app` in Google
   shows what has actually been picked up.
4. **Custom domain.** A `.vercel.app` subdomain is fine but a real domain is
   worth more for trust and is free to attach on Vercel. **Decision needed.**
5. **Internal linking is already decent** — guide links every video, channel
   pages group them, video pages link back. No orphans.

## 3. LLM crawlers

- `robots.txt` already names GPTBot, ClaudeBot and PerplexityBot explicitly.
- Consider adding `/llms.txt` — an emerging convention: a plain-text index of
  what the site is and where its content lives. Cheap to generate from
  `playlist.json` in `build.py`. Low certainty of payoff, low cost.
- The thing that actually gets cited is **substantive, specific text**. A page
  with three paragraphs of real context beats a hundred thin pages.

## 4. The content backlog — strategy

**Do not attempt all 517.** Publishing hundreds of pages of thin or invented
text is actively harmful: it looks like generated filler to search engines, and
inventing facts on a site meant to be cited is worse than saying nothing.

Priority order, with reasoning:

1. **Finish films (10 left).** Smallest gap, highest per-page value — full
   feature films are what someone actually searches for by name.
2. **Music, selectively (123 left).** Thiago's instinct is right that this is
   next, but not all 141 deserve equal treatment. Split it:
   - **Tier A** — canonical records with real cultural history (Ramones, Clash,
     Sex Pistols, Grace Jones, Madonna, Outkast, Notorious B.I.G., Pulp…).
     These get the full treatment and are where the traffic is.
   - **Tier B** — solid but less-documented tracks: two honest paragraphs.
   - **Tier C** — compilations, unofficial uploads, things neither of us can
     source. Leave blank rather than pad.
3. **History (25).** Fall of Civilizations episodes are individually
   substantial and searchable by subject. Good value per article.
4. **Comedy, nature, vignette (16 total).** Small, quick wins.
5. **Cartoon / ads / drag (344).** Deliberately last. Individual episodes of a
   1985 cartoon, single vintage commercials and individual lip syncs mostly
   cannot support a real article each. Better approach: write **strong channel
   pages** for these instead — one substantial piece about the Jem series, about
   the vintage advertising archive, about Drag Race lip syncs as a form — and
   leave the individual episodes thin.

**That last point is a change worth making to the build:** channel pages
currently only list programmes. They should be able to carry an article of
their own.

## 5. Blocked / needs Thiago

- Analytics choice (and GA measurement ID if that route)
- Google Search Console verification
- Custom domain: yes/no, and which
- **Carnival of Souls** (`A-L3Pe7JGck`) — the upload credits Wes Craven, but
  the well-known film is Herk Harvey's from 1962; there is also a 1998 remake
  carrying Craven's name as producer. They are different films and the notes
  would differ completely. Which is it?
- Nine other films whose details couldn't be confirmed: Crossworlds, The 13th
  Floor, Cyborg 2087, The Day Time Ended, The Langoliers, The Bat, Hercules in
  New York, Alien Vessel, plus Fadinha do Brasil in music.

## 6. Done

- [x] Per-video pages with structured data
- [x] Channel archive pages, tags clickable from the guide
- [x] Calendar archive in the guide
- [x] Sitemap + robots naming LLM crawlers
- [x] Video embedded on each programme page
- [x] Skill now writes deep notes by default on every add

---

# Ranking de oportunidade — onde escrever primeiro

Guesstimate honesto: sem ferramenta de keyword, isto é julgamento, não dado. Mas
o critério importa mais que a precisão, e o critério é **demanda ÷ concorrência**,
não demanda pura. Um site novo não vence Wikipedia, IMDb ou Genius em nada. Ele
vence onde quase ninguém escreveu.

## Alta oportunidade

**1. Lip syncs do Drag Race — 100 páginas sem artigo**
A melhor razão do catálogo. As buscas são hiper-específicas ("Geneva Karr
Hershii lip sync", "Sam Star Kennedy Davenport Rihanna"), o público é fervoroso
e busca constantemente, e quase ninguém escreve texto sobre um lip sync
individual — os wikis de fandom são finos nisso. Cada página é um evento
datável, com duas pessoas nomeadas e uma música nomeada. É o tipo de long tail
que um site pequeno consegue dominar.
Custo: alto por página (exige pesquisa real de quem são e onde estavam na
competição), mas o artigo do Geneva Karr provou que rende 600 palavras boas.

**2. Fall of Civilizations — 25 páginas, todas sem artigo**
Cada episódio é um assunto histórico distinto e realmente buscado. A
concorrência no assunto em si é Wikipedia, mas o long tail ("Fall of
Civilizations Bronze Age Collapse", "Songhai Empire documentary") é vencível, e
o público dessa série procura companhia em texto. Documentários longos também
casam com o canal History, que retoma de onde parou.

**3. Filmes obscuros e de domínio público — 11 sem artigo**
Cyborg 2087, The Day Time Ended, The Bat, Crossworlds, The 13th Floor. A
intenção de busca aqui é *assistir*, e nossa página tem o vídeo embutido mais
contexto. Poucos escrevem sobre eles. Paris Is Burning e The Times of Harvey
Milk são exceções de alta demanda **e** alta concorrência — valem pelo prestígio
do conteúdo, não pelo tráfego.
Bloqueio: de vários eu não sei os fatos. Precisa de pesquisa ou do Thiago.

**4. Comerciais brasileiros — 129, um artigo de canal, não 129 artigos**
"Grupo Imagem Teleshop", "Facas Ginsu 2000", "comercial anos 80" têm demanda
nostálgica real e concorrência quase nula. Mas individualmente são finos demais
para sustentar uma página cada. O certo é **um artigo forte na página do canal
Ads** sobre o arquivo, mais talvez cinco comerciais icônicos com página própria.

## Baixa oportunidade — não vale o esforço agora

- **Videoclipes famosos** (Deee-Lite, Janelle Monáe, Busta Rhymes, Britpop
  canônico): Wikipedia, Genius e os canais oficiais dominam. Perdemos.
- **Honest Trailers / Pitch Meetings**: Screen Junkies e ScreenRant são donos
  desses termos.
- **Clipes de SNL**: a NBC é dona.
- **Episódios de Jem** (65): demanda moderada, mas fandom e Hasbro competem, e
  65 páginas quase idênticas correm risco de parecer conteúdo gerado.

## Recomendação: os 5 primeiros

Escolhidos por razão demanda/concorrência, não por fama:

1. Um lip sync do Drag Race de temporada recente e muito comentado
2. Fall of Civilizations — Bronze Age Collapse (o episódio mais buscado da série)
3. Fall of Civilizations — The Mayans
4. Carnival of Souls (feito) → próximo: Cyborg 2087 ou The Day Time Ended
5. Artigo de canal para Ads (exige o recurso de artigo por canal, ainda não feito)

Reavaliar depois de 4–6 semanas com dados reais do Search Console. Aí para de
ser chute: dá para ver o que já recebe impressões e escrever mais daquilo.

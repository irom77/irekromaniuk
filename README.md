# Irek Romaniuk — Portfolio

Public portfolio for sharing professional experience, selected independent projects, and personal interests with recruiters and hiring teams.

**Live site:** [irek.romaniuk.us](https://irek.romaniuk.us/)

## Contents

- `index.html` — the responsive, single-page portfolio.
- `analytics.js` — GoatCounter events for outbound link clicks and opened interview answers.
- `og-image.png`, `robots.txt`, `sitemap.xml` — social preview image and search engine files. `docs/og-image.html` is the source for the image.
- `.github/workflows/deploy-pages.yml` — publishes the site to GitHub Pages.
- `AGENTS.md` — guidance for future edits to this repository.
- `.agents/skills/portfolio-interview/` — the interview skill that produces the reviewed answers for `interview.html` (linked for Claude Code from `.claude/skills/portfolio-interview`).

## Publishing

The site is deployed with GitHub Actions. Push changes to `main`, or run the **Deploy to GitHub Pages** workflow manually from the repository’s Actions tab. The workflow uploads the repository contents as the Pages site.

## Interview answers

The `portfolio-interview` skill interviews Irek about his security engineering experience and turns his answers into reviewed, public interview answers for `interview.html`. It works in Claude Code and Codex. Run it from the repository folder.

| Step | Claude Code | Codex |
| --- | --- | --- |
| Start or continue an interview | `/portfolio-interview security automation` | `$portfolio-interview security automation` |
| Review drafts | `/portfolio-interview review` | `$portfolio-interview review` |
| Publish approved answers | `/portfolio-interview publish` | `$portfolio-interview publish` |
| Re-review published answers | `/portfolio-interview re-review` | `$portfolio-interview re-review` |

Tracks: `security automation`, `incident response`, `applied AI`, `network cloud audit`, or `core`. With no track, the skill continues where the last session stopped.

**Interview.** The skill asks one question at a time, with follow-ups until an answer has a situation, Irek's own actions, a result, and a public source (or none). It then asks Irek to mark each concrete detail **public**, **generalize**, or **omit**, and writes a draft. Employers are never named.

**Stop at any point.** Say "stop" before answering the next question. The skill saves what has been said, records the unanswered question as next in its private state, and asks nothing more. Run the interview command again to resume from that question.

**Review.** The skill checks each draft against its review checklist and resolves open items one question at a time. It shows the final text, then asks Irek to approve, edit, or reject it. Only approved answers can be published.

**Publish.** The skill creates `interview.html` on the first publish, adds the approved answers, updates the "Last reviewed" date, and links the page from `index.html`. It shows the diff and doesn't commit. Check the page locally, then commit and push to deploy.

**Privacy.** Notes, drafts, and session state are kept in `~/portfolio-interview/`, outside this repository. Everything in this repository is published by GitHub Pages and stays in git history, so only approved answers are committed.

**Where answers live before publishing.** Until an answer is published, it exists only in `~/portfolio-interview/`:

| Stage | Location | Status in `state.md` |
| --- | --- | --- |
| Interview in progress | `notes/<date>-<track>.md` | `in-progress` |
| Drafted | `drafts/<question-id>.md` | `drafted` |
| Approved, not yet published | Same file in `drafts/` | `approved` |
| Published | `interview.html` in this repository | `published` |

Raw notes are never published. Publishing copies the approved text from `drafts/` into `interview.html`; the answer becomes public when that change is committed and pushed.

**Backup.** `~/portfolio-interview/` is not in git and has no backup by default. If the machine or WSL installation is lost, unpublished drafts and interview progress are lost too. To protect them, keep a copy somewhere private, for example a private Git repository or a cloud-synced folder. Never use this repository or any other public location.

## Visibility and analytics

Page views are counted by [GoatCounter](https://irekromaniuk.goatcounter.com) (site code `irekromaniuk`). It uses no cookies, so no consent banner is needed, and it ignores visits from `localhost`. `analytics.js` also records these events:

- `click: <url>`: a click on a link to another site, such as LinkedIn or GitHub.
- `answer: <id>`: an interview answer opened on `interview.html`.

The footer shows the site's total visitor count from GoatCounter's public counter (`/counter/TOTAL.json`). This needs **Allow adding visitor counts on your website** turned on in GoatCounter's site settings; without it the count stays hidden. GoatCounter caches the number for up to four hours.

Both pages have a canonical URL, Open Graph and Twitter tags, and `og-image.png` as the link preview image. `index.html` also has schema.org `Person` data. If you add a page, add these tags and the two analytics `<script>` lines before `</body>`, list the page in `sitemap.xml`, and update its `lastmod` dates.

**Where to see the numbers**

- [GoatCounter dashboard](https://irekromaniuk.goatcounter.com): visitors per page, referrers, countries, devices, and the `click:` and `answer:` events.
- [Google Search Console](https://search.google.com/search-console), **Performance**: how often the site appears in Google results, clicks, and the searches that show it.
- [Bing Webmaster Tools](https://www.bing.com/webmasters): the same for Bing (which also covers DuckDuckGo).

To stop counting your own visits, open `https://irek.romaniuk.us/#toggle-goatcounter` once in each browser you use.

**External settings the site depends on**

| Service | Setting | If it changes |
| --- | --- | --- |
| GoatCounter | Site code `irekromaniuk`; **Your site** set to `irek.romaniuk.us`; **Allow adding visitor counts on your website** on | A new code means updating `data-goatcounter` in both pages and the URL in `analytics.js`. With visitor counts off, the footer count is hidden. |
| Google Search Console | Domain property `irek.romaniuk.us`, verified through the domain name provider; `sitemap.xml` submitted | Removing the verification DNS record loses verification. |
| Bing Webmaster Tools | Imported from Google Search Console | Re-import if the Search Console property is recreated. |
| LinkedIn, GitHub, YouTube | Profile links to `https://irek.romaniuk.us/` | Update them if the domain changes. |

**Updating the preview image.** Edit `docs/og-image.html`, then render it at 1200×630 with headless Chrome or Chromium:

```bash
chrome --headless=new --hide-scrollbars --window-size=1200,630 --screenshot=og-image.png "file://$PWD/docs/og-image.html"
```

After deploying, run the URL through the [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) to refresh LinkedIn's cached preview.

## Editing

Edit `index.html` to update the portfolio. Keep public content accurate, avoid sharing confidential work details, and review project attribution and links before publishing. See `AGENTS.md` for repository-specific guidance.

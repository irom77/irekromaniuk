---
name: portfolio-interview
description: Use when Irek wants to be interviewed about his security engineering experience, continue an interview session, review or approve draft interview answers, publish approved answers to interview.html on his portfolio, or re-review published answers after the portfolio changes.
---

# Portfolio interview

Interview Irek about his experience and turn his answers into reviewed, public interview answers for `interview.html` on his portfolio (`https://github.com/irom77/irekromaniuk`). This skill is public and tailored to Irek; it holds only the method, never interview content.

**Core rule:** the repository is public and GitHub Pages publishes all of it. Nothing Irek says goes into the repository until he has approved the finished answer.

## Files

| Path | Public? | Contents |
| --- | --- | --- |
| `~/portfolio-interview/state.md` | Private | Covered question IDs, draft status, open `[CONFIRM]` items, detail classifications |
| `~/portfolio-interview/notes/<date>-<track>.md` | Private | Raw session notes |
| `~/portfolio-interview/drafts/<question-id>.md` | Private | Draft answers |
| `interview.html` (repo root) | Public | Approved answers only |
| `question-bank.md` (this folder) | Public | Questions by track |
| `interview-page-template.html` (this folder) | Public | Starting point for `interview.html` |

Create `~/portfolio-interview/` and its subfolders if missing. It must stay outside any public git repository; it has no backup by default, so if Irek asks for one, use only a private location (a private Git repository or a cloud-synced folder). Never write notes, drafts, or state inside the portfolio repository, including `docs/` or `.gitignore`d paths.

## Modes

Pick the mode from Irek's request; if unclear, read `state.md` and offer the next step.

### Interview (default)

1. Read `state.md`. Say in one or two sentences what is covered and what this session will cover (one track, 2–4 questions from `question-bank.md`).
2. Ask **one question per message**. Wait for the answer. Ask one follow-up per message until the answer has: situation, Irek's own actions (separate "I" from "we"), a result, and a public source or "no public source".
3. **Classify before drafting.** List each concrete detail from the answer (names of employers, vendors, internal systems, teams, incidents, numbers, dates) and ask Irek to mark each one **public**, **generalize**, or **omit**. Record the decisions in `state.md`. Employers are always generalized ("a previous employer", "a large financial services firm"), whatever Irek marks.
4. Write the draft to `drafts/<question-id>.md` in the answer format below, applying the classifications. Mark anything Irek did not state or confirm as `[CONFIRM: …]`.
5. End the session by updating `state.md` and listing open `[CONFIRM]` items.

**Stopping early:** when Irek says stop, stop asking questions. Save what he has said so far to the session notes, set any partly answered question to `in-progress` (no draft yet), and record the next unanswered question as `Next: <question-id>` in `state.md`. The next interview session starts with that question, or finishes the in-progress one first.

Skip compensation, availability or notice period, work authorization, and reasons for leaving an employer unless Irek raises them himself and says he wants a published answer.

### Review

Go through drafts one at a time. For each, run the review checklist, resolve `[CONFIRM]` items with Irek one question at a time, show the final text, and ask: approve, edit, or reject. Record the decision in `state.md`.

### Publish

Only for answers marked approved in `state.md`.

1. If `interview.html` does not exist, copy `interview-page-template.html` to the repo root.
2. Add each answer as a `<details>` block (see below) inside its track's `<section class="track">`, creating the section if needed, in the order given in the template comment.
3. Set the "Last reviewed" date to today, and set each published answer's status to `published` in `state.md`.
4. If `index.html` doesn't link to `interview.html` yet, add `<a href="interview.html">Interview</a>` to its nav and a link in the Experience section. Show Irek the change.
5. Show Irek the diff and remind him to check the page locally before committing. Do not commit or push unless he asks.

### Re-review

When the portfolio's roles, projects, or skills change, or before a job search, re-run the checklist on every published answer, propose edits, and update "Last reviewed" after Irek approves.

## Answer format

```markdown
# <question-id>
Track: <automation | response | applied-ai | foundations | core>
Question: <question as a recruiter would ask it>
Short answer: <1–2 sentences, first person>
Situation: <context, generalized>
Action: <what Irek did, first person>
Result: <outcome, only as stated and confirmed by Irek>
Links: <public project or portfolio URLs, or "none">
```

Write in first person (these are Irek's own answers), plain language, about 150–250 words in total so it can be said aloud in under two minutes. Use only facts Irek stated. Never compute new figures from his numbers (percentages, totals, averages) unless he confirms the computed figure.

## Published block

```html
<details id="<question-id>">
  <summary><h3>Question text</h3><p>Short answer.</p></summary>
  <div class="answer">
    <p><span class="label">Situation</span>…</p>
    <p><span class="label">Action</span>…</p>
    <p><span class="label">Result</span>…</p>
    <p class="links"><a href="…" target="_blank" rel="noreferrer">Project name ↗</a></p>
  </div>
</details>
```

Omit the `links` paragraph when there are no links. Escape `&`, `<`, and `>` in answer text.

## Review checklist

An answer is ready to approve only when every item holds:

- [ ] No `[CONFIRM: …]` markers remain.
- [ ] Every concrete detail has a recorded classification, and the text follows it.
- [ ] No employer is named, and the answer can't be matched to an employer through role dates, job titles, or other details in `index.html`'s experience timeline.
- [ ] No internal system names, incident specifics, credentials, personal data, or unapproved numbers.
- [ ] No sensitive topic (compensation, availability, work authorization, reasons for leaving) unless Irek explicitly chose to publish it.
- [ ] Consistent with `index.html` (skills, project descriptions) and claims nothing the portfolio contradicts.
- [ ] Every link is public and works.
- [ ] Irek said "approve" for this exact text.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Asking several questions in one message | One question per message; keep the rest for later |
| Drafting before details are classified | Classify first, then draft |
| Turning "about 40 minutes to 5" into "cut by 85%" | Use Irek's wording or ask him to confirm the new figure |
| Saving a draft in the repo "temporarily" | Drafts live only in `~/portfolio-interview/`; git history is permanent |
| Naming the employer because Irek did | Always generalize employers |
| Committing after publishing | Show the diff; commit only when Irek asks |

# Portfolio Interview Builder — Plan for Review

## Goal

Create a skill, specific to Irek, that interviews him about his security engineering experience and turns his answers into accurate, recruiter-friendly interview answers. After Irek reviews and approves them, the answers are published on the portfolio.

## Role tracks

The interview is organized around the tracks the portfolio already presents: the "Security engineering, automation, or applied AI" contact line, the skills list, the experience timeline, and the selected projects.

| Track | Portfolio evidence to draw on |
| --- | --- |
| Security automation & orchestration | Splunk SOAR, Ansible, Python; earlier security automation roles |
| Incident response & vulnerability management | Current role (internal, described only at a high level); Standalone SOC Case Analyzer |
| Applied AI for security | SOC Case Analyzer, Fine-tuning LLMs Lab (LoRA, jailbreak evaluation, DPO data), NanoChat, FlightLens's reviewed-digest design |
| Network, cloud & audit foundations | Firewall engineering, data-center migrations, Azure & Terraform, Kubernetes, control assessments and compliance audits |

A shared core covers all tracks: career summary, how Irek approaches problems (the portfolio's "find the signal, add context, make the next step clear" and its three principles), leadership and collaboration, and interests such as FPV/Racegow, which show the same engineering habits outside work.

## Intended behavior

1. **Interview in short rounds.** Each round covers one track or core topic: role and scope, then 2–3 flagship examples, then results and evidence, then what Irek learned or would do differently. A topic is complete when the answer has a situation, Irek's own actions, a result, and either a public source (project link or portfolio section) or a note that it has none.
2. **Ask follow-ups on vague answers.** Separate "I" from "we", ask what Irek personally did, and ask how a result was measured.
3. **Keep claims grounded.** Use only what Irek says. Mark anything unconfirmed inline as `[CONFIRM: …]` (for example a metric, date, or scope). Never invent metrics, responsibilities, or outcomes.
4. **Never name employers.** Published answers describe employers generically (for example "a large financial services firm" or "a previous employer"). Because the portfolio's experience timeline lists employers with dates, answers also avoid role dates, job titles, or other details that would let a reader match an answer to a specific employer.
5. **Classify sensitive details.** For each concrete detail (system or vendor names, incident specifics, team sizes, numbers), ask Irek to mark it **public**, **generalize**, or **omit**. Generalized wording must stay true (for example "reduced manual triage" in place of an internal metric). The skill never decides on its own that a detail is safe to publish.
6. **Skip personal topics by default.** Don't ask about compensation, availability or notice period, work authorization, or reasons for leaving an employer unless Irek raises the topic and chooses to publish an answer.
7. **Draft in Irek's answer format.** Each answer has a one- or two-sentence short answer, then situation, action, and result, at a length suited to a spoken interview answer. Answers are first-person, because they are Irek's own reviewed answers.
8. **Hand off for review.** Produce a review checklist for each answer: no `[CONFIRM]` markers left, every detail classified, no employer named or identifiable, consistent with `index.html` (skills, project descriptions), links work. Irek approves each answer before it is published.

## Where content lives

The repository is public and GitHub Pages currently publishes the whole repository (`path: .` in `.github/workflows/deploy-pages.yml`). Anything committed is public, and stays in git history even if it is deleted later.

- **Private (outside this repo, never committed):** raw interview notes, transcripts, session state, and draft answers. Default location: `~/portfolio-interview/` (not a git repository). Session state records covered topics, open `[CONFIRM]` items, and draft status, so an interview can continue across sessions without repeating questions.
- **Public (this repo):** the skill itself, and only approved answers.

## Publishing on the portfolio

- Publish approved answers on a separate page, `interview.html`, in the same visual style as `index.html` (same tokens, typography, header, and footer). Link to it from the `index.html` nav and from the Experience section. The Pages deployment already publishes the whole repository, so no workflow change is needed.
- Group answers by track. Use native `<details>`/`<summary>` elements: the question and short answer are visible by default, and the full answer and links to relevant projects expand. This keeps the page compact and accessible without JavaScript.
- Add a short note at the top: the answers are Irek's own, reviewed for public sharing; employers are not named; confidential work is described only at a high level.
- Show a "Last reviewed" date for the page, and give each answer a stable `id` anchor so individual answers can be linked.
- Start with a small set, for example one strong answer per track, and add more over time.

## Packaging

- Keep the skill in this repository so it works in both Codex and Claude Code:
  - Canonical location: `.agents/skills/portfolio-interview/SKILL.md`, which Codex scans from the repository root.
  - Claude Code: `.claude/skills/portfolio-interview` as a symlink to the canonical folder, so there is one copy to maintain. Verify that Claude Code loads the symlinked skill; if it doesn't, keep a copy and add a check that the two match.
  - Frontmatter uses only `name` and `description`, which both tools support. Keep the body free of tool-specific instructions, or put them in clearly labeled sections.
- `SKILL.md` contains the role tracks, question bank, answer format, sensitivity and employer rules, `[CONFIRM]` convention, and review checklist. It is tailored to Irek and is not presented as a general-purpose tool.
- `SKILL.md` contains no real interview content; any examples are made up.
- The skill is public: it is committed to this public repository, and `interview.html` links to it as "How these answers were produced", which shows the review process behind the answers. Because it is public, it must contain only the method (questions, rules, checklist) and never interview content.
- The skill's output for publishing is a ready-to-paste `<details>` block for `interview.html`, plus any suggested updates to existing portfolio text (for example a new skill or project mention), each listed separately for Irek to approve.

## How to use it

**Start a session** from the repository folder:

- Claude Code: run `claude` in `~/irekromaniuk`, then type `/portfolio-interview security automation` (or ask "interview me for the security automation track").
- Codex: run `codex` in `~/irekromaniuk`, then type `$portfolio-interview security automation` (or pick it from `/skills`).

**During a session** (about 20–30 minutes, one track):

1. The skill reads `~/portfolio-interview/state.md` to see which topics are covered and which `[CONFIRM]` items are open, then says what this session will cover.
2. It asks one question at a time, with follow-ups when an answer is vague. Answer by typing (or by dictating and pasting).
3. For each concrete detail, it asks you to mark it public, generalize, or omit.
4. At the end it writes draft answers and updated state to `~/portfolio-interview/`, and lists what is still unconfirmed.

**Review and publish** (later, when ready):

1. Run the skill in review mode (`/portfolio-interview review` or `$portfolio-interview review`). It goes through drafts with the review checklist and asks you to resolve each `[CONFIRM]` item.
2. Approve, edit, or reject each draft. Only approved answers get a `<details>` block.
3. The skill adds approved blocks to `interview.html` and updates the "Last reviewed" date. You check the diff and the page locally, then commit and push; GitHub Pages publishes it.

**Typical prompts:**

- "Continue where we left off."
- "Interview me on applied AI for security, focusing on the fine-tuning lab."
- "What's still missing before I can publish the incident response answers?"
- "Re-review published answers — I've updated the portfolio's skills list."

## Maintenance

- **Skill:** revise after each real session, and do a light review quarterly.
- **Published answers:** re-review when a role, project, or skill on the portfolio changes, before an active job search, and at least yearly. Update the page's "Last reviewed" date on each review.
- On every update, check the answers against `index.html` for accuracy, check links, and check for accidental private information or employer names.

## First milestone

1. Create the private working directory and write `SKILL.md`: tracks, question bank, answer format, sensitivity and employer rules, `[CONFIRM]` convention, and review checklist. Add the Claude Code symlink and confirm the skill loads in both Codex and Claude Code.
2. Run a real session on one track, ideally security automation, which has the most public evidence. Note repetitive questions and missing evidence in the private session notes.
3. Revise the skill based on that session.
4. Done when one session yields at least three answers that Irek approves, with no `[CONFIRM]` markers and every detail classified.
5. Create `interview.html` with the approved answers, link it from `index.html`, review both pages (accuracy, links, mobile and keyboard use, no employer names or private details), and publish.

## Decisions

- **Employers:** published answers never name employers (decided 2026-10-22).
- **Location:** approved answers go on a separate `interview.html` page (decided 2026-10-22).
- **Tools:** the skill supports both Codex and Claude Code (decided 2026-10-22).

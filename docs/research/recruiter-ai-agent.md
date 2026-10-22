# Recruiter-facing portfolio agent: research and recommended plan

**Prepared:** 2026-10-21 — initial research and plan by Codex.

**Reviewed and updated:** 2026-10-21 — by Claude (Claude Code). The review reordered the phases (static, model-free deliverables first; chat backend as a separately gated experiment), resolved a conflict between origin checks and agent access, added structured data, a source-of-truth check, an evaluation set, cost/kill criteria, and a deployment-scope fix. Changes are summarized in [Review notes](#review-notes-claude-2026-10-21).

**Added requirement:** 2026-10-22 — by Irek. Maintain approved interview Q&A in Irek's preferred answer format as a public knowledge source alongside the portfolio. The Q&A will be updated over time and may grow into the primary source; publish only entries explicitly reviewed for public sharing. Plan changes for this requirement were reviewed by Claude (Claude Code) and are summarized in [Q&A review notes](#qa-review-notes-claude-2026-10-22).

**Scope:** A public assistant that answers recruiter questions about Irek using approved portfolio information and approved interview Q&A, with a browser interface for people and machine-readable files for recruiter agents.

## Current portfolio context

The portfolio is a single static `index.html`, published by GitHub Actions to GitHub Pages. It already describes public work, career history at a high level, and LinkedIn/GitHub/YouTube contact links. The repository guidance says to keep content public, avoid confidential work details and scraped job data, preserve the current Pages deployment, and check accuracy and links before publishing.

Two facts about the current setup matter for this plan:

- `index.html` has a basic `description` meta tag but no structured data (no schema.org JSON-LD, no Open Graph tags).
- `.github/workflows/deploy-pages.yml` uploads the whole repository (`path: .`), so `docs/`, `TODO.md`, and `AGENTS.md` are publicly served alongside the site.

## Recommendation

Split the work into two decisions:

1. **Do now — static, model-free agent readiness.** Add schema.org `Person` JSON-LD to `index.html`, publish a curated `profile.json`, approved `interview-qa.json`, and `llms.txt`, and narrow what the Pages deployment publishes. This covers most of what recruiter AI tools actually consume (crawled pages and static files), costs nothing to run, and carries no abuse or spend risk.
2. **Decide separately — chat assistant experiment.** Add a small accessible chat panel to `index.html`, backed by a separately deployed serverless endpoint (a Cloudflare Worker is a practical fit; Pages Functions are an option if the site later moves to Cloudflare Pages). The endpoint holds the model API key. Proceed only once the evaluation set (Phase 2) exists and a cost ceiling and kill criteria are agreed.

Both decisions share a small public knowledge base: the curated profile derived from `index.html`, plus a separately maintained interview Q&A containing approved answers in Irek's preferred interview format. Each hard fact (dates, roles, employers, metrics, links) lives in exactly one place, the profile; Q&A answers reference it by ID rather than restating it. This keeps the sources consistent even if the Q&A grows to become the larger, primary source of answers. CI enforces structure, references, and fact consistency; human review covers public-sharing approval and tone.

This is an architectural recommendation based on the current deployment and product requirements; it has not been implemented or deployed.

### Why this shape

- GitHub Pages is a static host; it does not provide a private server environment for an API secret. Provider documentation (e.g. OpenAI's) says API keys must not be exposed in browser code and should be loaded on the server.
- A separate Worker API can be introduced without changing the existing GitHub Pages publishing workflow. Pages Functions are also designed to add server-side behavior to static sites, but adopting them would mean serving the site through Cloudflare Pages rather than the current GitHub Pages deployment.
- Recruiter agents and LLM search tools are far more likely to read crawlable pages, structured data, and static files than to discover and call a bespoke chat endpoint. Static files therefore serve AI visitors; the chat endpoint serves human visitors.
- For the chat experiment, send a short, bounded turn history with each request and disable response storage (`store: false` on OpenAI's Responses API, or the equivalent on another provider). Avoid persistent conversation storage. Response storage settings do not control all provider-side retention: OpenAI documents a default retention period of up to 30 days for abuse-monitoring logs.
- Treat a standardized agent protocol (A2A, MCP) as a later phase after confirming real client demand. It adds more server complexity than a static profile.

## Product behavior

The assistant should:

1. Clearly identify itself as Irek's AI portfolio assistant, not Irek.
2. Answer questions about skills, experience, selected projects, interests, and contact options from the maintained public profile and approved interview Q&A.
3. Include links to the portfolio sections and project sources for factual claims where possible.
4. Say when the public material does not establish an answer; it must not invent dates, accomplishments, availability, compensation, work authorization, or private work details. Compensation, availability, and work authorization are discussed only if a Q&A entry explicitly approved for that topic exists; otherwise the assistant directs the recruiter to contact Irek.
5. Present approved Q&A answers as Irek's answers, not as the assistant speaking for itself — for example, “Irek's approved answer: …” for first-person text, or a faithful third-person rendering. The assistant must not adopt Irek's first-person voice.
6. Use the preferred answer format (see the style guide in Phase 1) when presenting approved answers. For questions no Q&A entry covers, answer only from profile facts; it may use the same structure but must not invent narrative, outcomes, or opinions Irek has not approved.
7. Encourage direct contact through the existing LinkedIn link when a recruiter wants a conversation with Irek.
8. Decline requests for confidential work details, private records, candidate/job scraping, or actions on Irek's behalf.
9. Avoid asking for or storing recruiter names, emails, candidate resumes, job descriptions, or other personal data in the first release.

For human visitors, provide an accessible text chat with suggested questions and a clear “Connect with Irek on LinkedIn” handoff. For AI visitors, provide JSON-LD on the page plus public, versioned `profile.json` and `interview-qa.json` files discoverable through `llms.txt`. Do not claim A2A or MCP compatibility unless the corresponding protocol is implemented and checked for conformance.

## Architecture options

| Option | Benefits | Costs / limits | Fit |
| --- | --- | --- | --- |
| Static agent readiness only (JSON-LD, `profile.json`, `interview-qa.json`, `llms.txt`) | Zero running cost; no secrets, abuse surface, or provider dependency; serves AI crawlers directly | No conversational experience for humans | **Recommended first step**, and a complete outcome if the chat experiment is not approved |
| Hosted chatbot vendor embedded in the page | Fastest initial UI; little backend code | Adds a vendor and its data handling; may have weaker prompt, retention, or source-control options; integration details vary | A quick prototype only if vendor terms and data handling meet the privacy bar |
| Custom static widget + separate serverless API | Keeps current GitHub Pages deploy; clear control over source facts, prompts, retention, and limits; low operational footprint | Requires API implementation, secret setup, monitoring, and abuse controls | **Recommended for the chat experiment** |
| Move the portfolio to Cloudflare Pages and use Pages Functions | Frontend and backend share an origin; Functions route directly alongside static files; secrets are supported | Changes hosting/deployment setup from the existing workflow; wider change than needed for one endpoint | Consider only if Cloudflare hosting is already desired |

## Implementation plan

### Phase 1 — Public knowledge sources and static agent readiness (do now)

- Create a compact approved profile file (`profile.json`) from the information already published in `index.html`: role/skill summaries, publicly shareable project summaries, dates already on the page, canonical links, an update date, and a statement that it is a portfolio summary rather than an authoritative employment verification source.
- Author the interview Q&A as one Markdown file per entry (for example `content/interview-qa/<id>.md`) with a short front-matter header and the answer as prose. A small build script generates the published `interview-qa.json` from these files in CI. Long answers stay easy to edit and review, diffs stay readable, and a human-readable Q&A page can be generated later from the same source.
- Define the entry schema and version it (`schema_version` at the top of the generated JSON):
  - `id` — stable, kebab-case, never reused.
  - `question` and `variants[]` — the canonical question plus common phrasings, used for matching and retrieval.
  - `tags[]` — topics such as `security-automation`, `applied-ai`, `leadership`.
  - `short_answer` — one or two sentences.
  - `answer` — the full answer in the preferred format.
  - `project_ids[]` and `fact_refs[]` — IDs of the profile projects and facts the answer relies on.
  - `sources[]` — allowlisted links.
  - `sensitive_topic` — set only for an approved entry on compensation, availability, work authorization, or reasons for leaving; absent otherwise.
  - `last_reviewed` and `review_by` — dates for the staleness check.
- Write a short style guide (`content/interview-qa/STYLE.md`) defining Irek's preferred answer format: structure (for example short answer first, then situation, action, and result), target length, tone, and voice. Entries follow it, and the chat backend uses it to present answers. The style guide is a build input, not a published file.
- Keep hard facts in the profile. Q&A answers refer to dates, roles, employers, and metrics through `fact_refs` and `project_ids` instead of restating them. CI fails if an answer contains a date, year, or number that does not appear in a referenced profile fact. If a new answer needs a new fact, add the fact to `profile.json` (and `index.html` where appropriate) first.
- Exclude sensitive interview topics by default: salary or compensation expectations, availability or notice period, work authorization, and reasons for leaving an employer. Include one only as a deliberate, per-entry decision marked with `sensitive_topic`, and keep reasons-for-leaving answers free of confidential employer details.
- Draft outside this repository. The repository is public, so committing a draft publishes it permanently through git history; a `draft` status field is not a privacy control. Raw interview notes, candidate answers, and unapproved entries never enter the repo. Only entries already reviewed for public sharing, confidentiality, personal data, and accuracy are committed.
- Define a repeatable update routine: draft privately, review the answer against the style guide and the profile, add any new facts to the profile first, commit the entry with an updated `last_reviewed`, and let CI validate and regenerate the JSON. Resolve conflicts with portfolio facts in the source material; Q&A never overrides the profile.
- Re-review entries periodically. CI warns when an entry's `review_by` date has passed (default 12 months after `last_reviewed`) or when a referenced project or fact changes after the entry was last reviewed.
- Direct `llms.txt` and any future chat backend to use both public files: the profile for verified facts, the Q&A for approved answers in Irek's preferred format. If sources disagree or a question is not covered, the assistant should say the public material does not establish it.
- Give each project a stable ID (e.g. `fpv-best-laps`), and each hard fact in the profile (a role, date range, or metric) a stable fact ID, so the Q&A and later components can reference them without restating facts or using free-form URLs.
- Mark unknowns explicitly. Exclude internal incident/vulnerability details, employer confidential information, and any scraped job or candidate data.
- Add schema.org `Person` JSON-LD (name, job title, `sameAs` links to LinkedIn/GitHub/YouTube, `knowsAbout` skills) and basic Open Graph tags to `index.html`.
- Publish a short `llms.txt` pointing to the portfolio sections, `profile.json`, and `interview-qa.json`, and identify the Q&A as approved public interview answers.
- Add a CI check covering both sources:
  - valid structure against the schema, and unique, stable IDs;
  - resolvable `project_ids` and `fact_refs`, and allowlisted links;
  - the profile-fact consistency rule above;
  - `profile.json` consistent with `index.html` (or generate one from the other);
  - a token-count report for the combined profile and Q&A, which fails above the context budget agreed in Phase 2.
- Narrow the Pages deployment so only site files are published, for example by moving them into a `site/` directory or building the upload artifact from an explicit allowlist. The allowlist must include `index.html`, `profile.json`, the generated `interview-qa.json`, and `llms.txt`. Planning docs, Q&A source files, the style guide, prompts, evaluation cases, and refusal rules should not be served publicly by default.

### Phase 2 — Evaluation set and go/no-go for the chat experiment

- Write 20–30 evaluation questions with expected outcomes: a grounded answer with source links, an honest “not stated publicly” response, or a refusal. Cover salary, work authorization, availability, confidential incidents, requests to act on Irek's behalf, and prompt-injection attempts.
- Include Q&A cases:
  - reworded versions of existing Q&A questions, which should return the approved answer;
  - questions near but outside Q&A coverage, which should be answered from profile facts only, with no invented narrative;
  - prompts that try to make the assistant answer as Irek in the first person;
  - each excluded sensitive topic, both with and without an approved entry.
- Treat this set as the acceptance test for the backend. Rerun it on every model, prompt, or Q&A change, and add cases as Q&A entries are added.
- Agree on a cost ceiling: model choice, maximum input/output tokens per turn, maximum turns, expected monthly cost, and a hard provider budget with alerts.
- Agree on a context budget for the knowledge base (for example a token limit for profile plus Q&A). Below it, the backend sends the full knowledge base with each request, using provider prompt caching for the fixed portion. Above it, switch to retrieval: select relevant Q&A entries by tags, variants, or embedding similarity, and always include the profile. The CI token report from Phase 1 shows when the switch is due.
- Agree on kill criteria, for example: fewer than N genuine conversations after 60 days, or any confidential-information leak in evaluation or production, means remove the widget and keep the Phase 1 static files.
- Proceed to Phase 3 only if this phase is approved.

### Phase 3 — Build and test the backend in isolation

- Deploy a small Worker endpoint, such as `POST /api/chat`, with a fixed model configuration, strict request-size and message-count limits, and server-side secret storage.
- Put the model call behind a thin provider adapter so the model or provider can be changed without rewriting the endpoint.
- Include the curated profile and approved interview Q&A as trusted context, within the Phase 2 context budget (full inclusion with prompt caching, or retrieval once the budget is exceeded). Include the style guide in the system prompt so approved answers are presented in Irek's preferred format and attributed to Irek. Treat visitor text as untrusted input and never grant tools that can browse private resources, send messages, or make changes. The Q&A is maintained content, not permission to reveal raw interview records or private details.
- Keep only the last few turns in the visitor's browser session and submit them with each request; disable provider response storage and do not create durable conversations.
- Never log request or response bodies. Disable or filter Workers request logging/tail capture so platform observability does not retain message content; keep only aggregate request, error, and cost counts.
- Scope abuse controls to the endpoint's actual audience: the endpoint serves the browser widget, so origin checks are appropriate. Add request validation, per-IP/session rate limits, a honeypot or equivalent low-friction control, and optional Turnstile escalation for suspicious traffic (validated server-side). Treat edge rate limits as an abuse speed bump, not as a hard spending limit.
- Use a restricted, project-scoped API key and the provider budget from Phase 2.
- Return a small typed JSON response. Have the model reference projects and sections by the stable IDs from Phase 1; the server maps IDs to URLs from an allowlist, so the model never emits free-form links.
- Decide explicitly between streaming (better perceived latency) and a single typed response (simpler validation). A single response is the simpler default for the first release.
- Pass the Phase 2 evaluation set before any public exposure.

### Phase 4 — Add the human interface

- Add a compact, keyboard-accessible chat panel consistent with the existing visual style, including focus management, screen-reader labels, pending/error states, and a clear reset action.
- Include suggested questions such as “What security automation work has Irek done?” and “Which projects show his applied AI experience?”
- Show an accurate privacy note before the first message: messages are sent to the model provider, which may retain them for a limited period for abuse monitoring; the portfolio service itself does not store transcripts; do not submit sensitive personal, candidate, or job data.
- Keep LinkedIn and GitHub links visible when the agent is unavailable.

### Phase 5 — Review and launch

- Review every fact and every published Q&A entry against the live portfolio and public project links; check for accidental confidential or personal data, and confirm no draft or unapproved Q&A exists anywhere in the repository history.
- Verify the widget on mobile, keyboard-only, and screen-reader flows, and verify JSON-LD with a structured-data validator.
- Test malformed/oversized input, rate limiting, missing API credentials, provider outage, and chat reset, in addition to the evaluation set.
- Deploy first to a preview endpoint. Review operational cost controls and provider data handling before linking the chat from the public portfolio.
- Launch with a visible fallback to LinkedIn. Review aggregate usage against the kill criteria at 60 days.

### Later — Agent protocols (only on demonstrated demand)

- A public chat API for third-party agents would conflict with the browser-only origin checks above. Agents should use `profile.json` and `interview-qa.json` instead. If agent-to-agent sessions are later justified, expose a separate, rate-limited agent path rather than loosening the widget endpoint.
- If adopting A2A, publish an Agent Card only together with a fully compatible task endpoint. Confirm the discovery path against the current specification: newer A2A revisions use `/.well-known/agent-card.json` rather than the older `/.well-known/agent.json`.

## Success criteria

- A recruiter agent or LLM search tool can retrieve accurate structured facts and approved interview answers (JSON-LD, `profile.json`, `interview-qa.json`, `llms.txt`) without page interaction or any running backend.
- `profile.json` and `index.html` stay consistent, and Q&A answers stay consistent with profile facts; both are enforced by CI.
- Approved interview answers are available in a maintained, versioned file generated from reviewed source entries; no entry is past its re-review date without a CI warning.
- Recruiter answers reflect Irek's preferred interview format, are attributed to Irek rather than spoken as Irek, and stay grounded in the portfolio and approved Q&A.
- The knowledge base can grow without breaking the cost ceiling: the CI token report stays under the context budget, or retrieval is in place.
- Only site files are published by the Pages deployment.
- If the chat experiment runs: a recruiter can ask a natural-language question and receive an accurate response with allowlisted source links or an honest uncertainty response; the evaluation set passes; spend stays under the agreed ceiling.
- The assistant never exposes confidential employment information, makes unsupported claims, or takes actions on Irek's behalf.
- The API key stays server-side, public-site traffic remains on the current GitHub Pages workflow, and neither application nor platform logs contain message transcripts.
- The experience remains usable on mobile and with keyboard/screen reader input, and LinkedIn remains available as a direct fallback.

## Review notes (Claude, 2026-10-21)

Changes from Codex's original plan:

1. **Phase order.** Static, model-free deliverables (formerly Phase 4) moved to Phase 1; the chat backend became a separately gated experiment.
2. **Structured data added.** schema.org `Person` JSON-LD and Open Graph tags were missing from the original plan and from `index.html`.
3. **Origin-check conflict resolved.** The original plan applied origin checks to `POST /api/chat` and also advertised that endpoint to external agents via OpenAPI, which those agents could not pass. The endpoint is now browser-only; agents use static files. The OpenAPI deliverable was dropped.
4. **Source-of-truth drift check.** Added a CI consistency check between `profile.json` and `index.html`.
5. **Evaluation set first.** Testing of refusals, uncertainty, and prompt injection is now a pre-build acceptance set (Phase 2), not only a launch-time check.
6. **Privacy note corrected.** The original note said no transcript is retained, which is true only of the portfolio service; it now discloses provider abuse-monitoring retention. Added an explicit rule against platform-level (Workers) body logging.
7. **Cost ceiling and kill criteria.** Added before any build commitment.
8. **Provider-agnostic adapter.** The model call sits behind a thin adapter rather than being tied to one provider.
9. **Link handling.** The model references stable project IDs that the server maps to allowlisted URLs, instead of filtering model-generated URLs.
10. **Streaming decision** made explicit.
11. **Deployment scope.** The Pages workflow currently publishes the whole repository, including this document; narrowing it is now a Phase 1 task.
12. **A2A discovery path.** Flagged that newer spec revisions use `/.well-known/agent-card.json`; verify against the current spec before implementing.
13. **Removed an unverified claim** about an OpenAI Agent Builder shutdown date that the plan did not depend on.

## Q&A review notes (Claude, 2026-10-22)

Changes after Irek added the interview Q&A requirement, which assumes the Q&A may grow into the primary source:

1. **Single home for facts.** Hard facts live only in the profile; Q&A answers reference them through `fact_refs` and `project_ids`. CI rejects dates or numbers in answers that do not appear in a referenced fact, replacing a manual conflict review that would not scale.
2. **Context budget and retrieval.** The full knowledge base is sent with each request (with prompt caching) only below an agreed token budget; above it, the backend switches to retrieval. A CI token report tracks growth.
3. **Markdown source, generated JSON.** Entries are authored as one Markdown file each and compiled to `interview-qa.json` in CI, for easier editing and review.
4. **Schema and style guide.** Defined the entry fields and added a style guide that captures the preferred answer format. Uncovered questions may use the same structure but not invented narrative.
5. **Voice.** Approved answers are attributed to Irek; the assistant never speaks as Irek in the first person.
6. **Sensitive interview topics.** Compensation, availability, work authorization, and reasons for leaving are excluded by default and allowed only per entry.
7. **Drafts stay out of the public repo.** Git history is permanent, so a draft flag is not a privacy control.
8. **Staleness.** Each entry has review dates, and CI warns on overdue entries or on changes to facts they reference.
9. **Evaluation, launch review, and deployment allowlist** updated to cover the Q&A.

## Official references

- OpenAI, [ChatKit](https://developers.openai.com/api/docs/guides/chatkit): embeddable chat UI options; current guidance for new integrations is to use a custom server integration.
- OpenAI, [API reference overview](https://developers.openai.com/api/reference/overview): API keys are secrets and should not be exposed in client-side code; load them on the server.
- OpenAI, [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state): Responses API state options, response storage behavior, and conversation persistence details.
- OpenAI, [Data controls](https://developers.openai.com/api/docs/guides/your-data): API data is not used for model training by default; abuse monitoring logs may retain content for up to 30 days; endpoint application-state retention and approved retention controls vary.
- OpenAI, [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits): requests and tokens are subject to project and organization limits; use bounded request sizes and configure spending controls.
- Cloudflare, [Pages Functions](https://developers.cloudflare.com/pages/functions/): server-side code for dynamic functionality without a dedicated server.
- Cloudflare, [Pages routing](https://developers.cloudflare.com/pages/functions/routing/): file-based routes, static asset fallthrough, and rules for limiting which paths invoke Functions.
- Cloudflare, [Pages bindings and secrets](https://developers.cloudflare.com/pages/functions/bindings/): encrypted secrets are available through the runtime environment; do not commit secrets.
- Cloudflare, [Turnstile setup](https://developers.cloudflare.com/turnstile/get-started/): public widget token must be validated server-side; tokens expire and are single-use.
- Cloudflare, [Workers rate limiting binding](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/): a low-latency edge rate limiter; its distributed counters are approximate and should not be treated as an exact billing control.
- Schema.org, [Person](https://schema.org/Person): structured-data vocabulary for describing a person, including `jobTitle`, `sameAs`, and `knowsAbout`.
- llmstxt.org, [The /llms.txt file](https://llmstxt.org/): proposed convention for an LLM-oriented site summary at the site root.
- A2A Project, [Agent2Agent specification](https://a2a-protocol.org/latest/specification/): agent discovery and communication; the Agent Card describes capabilities and endpoint (verify the current well-known path).

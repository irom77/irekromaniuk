# Recruiter-facing portfolio agent: research and recommended plan

**Prepared:** 2026-10-21

**Scope:** A public assistant that answers recruiter questions about Irek using only approved portfolio information, with a browser interface for people and a machine-readable interface for recruiter agents.

## Current portfolio context

The portfolio is a single static `index.html`, published by GitHub Actions to GitHub Pages. It already describes public work, career history at a high level, and LinkedIn/GitHub/YouTube contact links. The repository guidance says to keep content public, avoid confidential work details and scraped job data, preserve the current Pages deployment, and check accuracy and links before publishing.

## Recommendation

Keep GitHub Pages serving the existing site. Add a small accessible chat panel to `index.html`, backed by a separately deployed serverless endpoint (a Cloudflare Worker is a practical fit; Pages Functions are an option if the site later moves to Cloudflare Pages). The endpoint holds the model API key and exposes a narrow, documented chat API. Maintain a curated public profile as the agent's only source of truth, preferably a small JSON or Markdown file in the repo. Use the same facts to produce a human-readable assistant response and machine-readable public profile documents.

This is an architectural recommendation based on the current deployment and product requirements; it has not been implemented or deployed.

### Why this shape

- GitHub Pages is a static host; it does not provide a private server environment for an API secret. OpenAI's documentation says API keys must not be exposed in browser code and should be loaded on the server.
- A separate Worker API can be introduced without changing the existing GitHub Pages publishing workflow. Pages Functions are also designed to add server-side behavior to static sites, but adopting them would mean serving the site through Cloudflare Pages rather than the current GitHub Pages deployment.
- OpenAI's Responses API supports conversational turns. For a public recruiter tool, manually send a short, bounded turn history and use `store: false`; avoid persistent Conversations API storage unless there is a deliberate need for cross-session memory. OpenAI documents a default 30-day retention period for abuse monitoring logs; `store: false` controls response-object storage, not all service-side retention.
- An AI recruiter needs a stable way to discover and fetch approved facts. Publish a concise public profile JSON plus a short `llms.txt`/agent instructions page, and document the chat endpoint schema. Treat a standardized agent protocol as a later phase after confirming real client demand; A2A is an agent-to-agent protocol with a discovery card and adds more server complexity than a static profile/API.

## Product behavior

The assistant should:

1. Clearly identify itself as Irek's AI portfolio assistant, not Irek.
2. Answer questions about skills, experience, selected projects, interests, and contact options from a maintained, approved public fact set.
3. Include links to the portfolio sections and project sources for factual claims where possible.
4. Say when the public material does not establish an answer; it must not invent dates, accomplishments, availability, compensation, work authorization, or private work details.
5. Encourage direct contact through the existing LinkedIn link when a recruiter wants a conversation with Irek.
6. Decline requests for confidential work details, private records, candidate/job scraping, or actions on Irek's behalf.
7. Avoid asking for or storing recruiter names, emails, candidate resumes, job descriptions, or other personal data in the first release.

For human visitors, provide an accessible text chat with suggested questions and a clear “Connect with Irek on LinkedIn” handoff. For AI visitors, provide a public, versioned JSON profile and an OpenAPI description of the same chat endpoint so agents can discover its capabilities and request bounded answers. Do not claim A2A or MCP compatibility unless the corresponding protocol is implemented and checked for conformance.

## Architecture options

| Option | Benefits | Costs / limits | Fit |
| --- | --- | --- | --- |
| Hosted chatbot vendor embedded in the page | Fastest initial UI; little backend code | Adds a vendor and its data handling; may have weaker prompt, retention, or source-control options; integration details vary | A quick prototype only if vendor terms and data handling meet the privacy bar |
| Custom static widget + separate serverless API | Keeps current GitHub Pages deploy; clear control over source facts, prompts, retention, and limits; low operational footprint | Requires API implementation, secret setup, monitoring, and abuse controls | **Recommended** |
| Move the portfolio to Cloudflare Pages and use Pages Functions | Frontend and backend share an origin; Functions route directly alongside static files; secrets are supported | Changes hosting/deployment setup from the existing workflow; wider change than needed for one endpoint | Consider only if Cloudflare hosting is already desired |

## Implementation plan

### Phase 1 — Define the source of truth

- Create a compact approved profile file from the information already published in `index.html`.
- Include role/skill summaries, publicly shareable project summaries, dates already on the page, and canonical links.
- Mark unknowns explicitly. Exclude internal incident/vulnerability details, employer confidential information, and any scraped job or candidate data.
- Establish response rules: source-grounded claims, concise answer style, refusal boundaries, uncertainty language, and recruiter handoff.

### Phase 2 — Build and test the backend in isolation

- Deploy a small Worker endpoint, such as `POST /api/chat`, with a fixed model configuration, strict request-size and message-count limits, and server-side secret storage.
- Use the Responses API with the curated profile included as trusted context. Treat visitor text as untrusted input and never grant tools that can browse private resources, send messages, or make changes.
- Keep only the last few turns in the visitor's browser session and submit them with each request; use `store: false` and do not create durable conversations or keep transcripts in application logs.
- Add server-side origin checks, request validation, per-IP/session rate limits, a honeypot or equivalent low-friction abuse control, and optional Turnstile escalation for suspicious traffic. Turnstile must be validated server-side; do not require a visual challenge on every interaction because that can block automated recruiter clients.
- Use a restricted, project-scoped API key, set provider spend limits/alerts, and cap request size, context length, output tokens, and turns. Treat edge rate limits as an abuse speed bump, not as a hard spending limit.
- Return plain text or a small typed JSON response. Use a server-side allowlist for outbound links rather than model-generated URLs.

### Phase 3 — Add the human interface

- Add a compact, keyboard-accessible chat panel consistent with the existing visual style, including focus management, screen-reader labels, pending/error states, and a clear reset action.
- Include suggested questions such as “What security automation work has Irek done?” and “Which projects show his applied AI experience?”
- Show an explicit privacy note before the first message: messages are sent to the model provider; do not submit sensitive personal, candidate, or job data; no transcript is retained by the portfolio service.
- Keep LinkedIn and GitHub links visible when the agent is unavailable.

### Phase 4 — Make it usable by recruiter agents

- Add a compact public `profile.json` (and optionally `llms.txt`) with canonical facts, project links, section URLs, update date, and a statement that it is a portfolio summary rather than an authoritative employment verification source.
- Publish a small OpenAPI document for `POST /api/chat`, including request limits, the no-auth public access model, example questions, expected response shape, privacy behavior, and contact handoff.
- If partner/recruiter systems demonstrate demand for direct agent-to-agent sessions, add an A2A Agent Card and implement the full compatible task endpoint. Avoid publishing an Agent Card that advertises a protocol the service does not actually support.

### Phase 5 — Review and launch

- Review every fact against the live portfolio and public project links; check for accidental confidential or personal data.
- Verify the widget on mobile, keyboard-only, and screen-reader flows, plus the direct JSON/API flow used by an AI client.
- Test refusal/uncertainty cases, prompt injection attempts, malformed/oversized input, rate limiting, missing API credentials, provider outage, and chat reset.
- Deploy first to a preview endpoint. Review operational cost controls and provider data handling before linking the chat from the public portfolio.
- Launch with a visible fallback to LinkedIn; review only aggregate request/error/cost counts and avoid collecting conversation content.

## Success criteria

- A recruiter can ask a natural-language question and receive an accurate response with source links or an honest uncertainty response.
- A recruiter agent can retrieve the structured profile and use the documented chat endpoint without relying on page interaction.
- The assistant never exposes confidential employment information, makes unsupported claims, or takes actions on Irek's behalf.
- The API key stays server-side, public-site traffic remains on the current GitHub Pages workflow, and portfolio service logs contain no message transcripts.
- The experience remains usable on mobile and with keyboard/screen reader input, and LinkedIn remains available as a direct fallback.

## Official references

- OpenAI, [ChatKit](https://developers.openai.com/api/docs/guides/chatkit): embeddable chat UI options; current guidance for new integrations is to use a custom server integration. Its existing Agent Builder hosted integration is in a transition period, with Agent Builder scheduled to shut down November 30, 2026.
- OpenAI, [API reference overview](https://developers.openai.com/api/reference/overview): API keys are secrets and should not be exposed in client-side code; load them on the server.
- OpenAI, [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state): Responses API state options, response storage behavior, and conversation persistence details.
- OpenAI, [Data controls](https://developers.openai.com/api/docs/guides/your-data): API data is not used for model training by default; abuse monitoring logs may retain content for up to 30 days; endpoint application-state retention and approved retention controls vary.
- Cloudflare, [Pages Functions](https://developers.cloudflare.com/pages/functions/): server-side code for dynamic functionality without a dedicated server.
- Cloudflare, [Pages routing](https://developers.cloudflare.com/pages/functions/routing/): file-based routes, static asset fallthrough, and rules for limiting which paths invoke Functions.
- Cloudflare, [Pages bindings and secrets](https://developers.cloudflare.com/pages/functions/bindings/): encrypted secrets are available through the runtime environment; do not commit secrets.
- Cloudflare, [Turnstile setup](https://developers.cloudflare.com/turnstile/get-started/): public widget token must be validated server-side; tokens expire and are single-use.
- OpenAI, [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits): requests and tokens are subject to project and organization limits; use bounded request sizes and configure spending controls.
- Cloudflare, [Workers rate limiting binding](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/): a low-latency edge rate limiter; its distributed counters are approximate and should not be treated as an exact billing control.
- A2A Project, [Agent2Agent specification](https://a2a-protocol.org/latest/specification/): A2A defines agent discovery and communication; the Agent Card describes capabilities and endpoint and is conventionally served at `/.well-known/agent.json`.

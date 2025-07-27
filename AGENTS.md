AGENTS.md

🧠 Tornetic Code Agent Engineering Guide
1. ⚙️ Architecture & Code Quality
Follow SaaS best practices: Apply modular design, stateless services (where possible), and separation of concerns.

Modularize aggressively: Break functionality into clear services/components/modules. Avoid tight coupling and cross-dependencies.

Favor reuse: Use shared libraries/utilities when possible instead of duplicating logic.

Readable code:

Name variables and functions descriptively.

Keep logic blocks small and focused.

Use helper functions over nested complexity.

Consistency: Follow established linting rules, formatting conventions, and architecture patterns.

2. 📝 Documentation Standards
Update docs:

Every new feature must come with documentation.

Modified logic must reflect changes in the corresponding doc files (e.g., API endpoints, behavior changes).

Inline comments:

Add comments to any non-obvious logic or "why" decisions.

Avoid redundant or obvious comments.

Config & Flags:

Document all new configuration keys or feature flags in a central README.md, config.md, or inline above the declaration.

3. 🧪 Testing Requirements
Test coverage is required for all new logic. No exceptions.

Types of tests:

✅ Unit tests for every component/module

🔄 Integration tests for workflows and pipelines

🚩 Feature flag tests to ensure toggled logic behaves correctly

For existing code:

Add or extend tests if new branches or edge cases are introduced.

CI Enforcement:

Your PR must pass CI including typecheck, lint, and test suites.

4. 🌿 Git & Branching Hygiene
Commits:

Use clear, imperative commit messages: Fix crash in scheduler, Refactor slot detection, etc.

Group related changes together.

Pull Requests:

Keep PRs focused and single-purpose.

Don’t mix unrelated fixes or refactors.

Add a descriptive summary with:

What changed

Why it changed

Any follow-ups needed

5. 🔐 Security & Privacy
Sanitize all logs:

No tokens, email addresses, user messages, or sensitive payloads in logs or stack traces.

Input validation:

All user inputs and external API data must be validated (schema or manual).

Access control:

Double-check permission checks for subscription-based features and authenticated access.

Use role-based gates or decorators where applicable.

6. 🚀 Performance Best Practices
Database queries:

Avoid N+1 patterns (e.g., use joins or select_related / preload where supported).

Async pipelines:

Long-running tasks (e.g., transcription, speech-to-text, external API requests) must use background queues (e.g., Celery, Sidekiq).

Caching:

Use memory or edge caching for static/public data (e.g., tutor bios, reviews).

Avoid stale cache issues—define TTLs or version keys.

7. 🧰 Type & Lint Enforcement
Your code must pass npm run typecheck.

Use descriptive types and interfaces.

Avoid any, @ts-ignore, or unsafe casts unless strongly justified (and documented).

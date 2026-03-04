# Proximity Sprint 1 MVP

This repository now contains a runnable Sprint 1 scaffold for the **Proximity** family-office product.

## What is implemented

- **Auth + onboarding primitives**: register/login and onboarding update endpoints.
- **Organization model** with role-aware team invite flow (owner/admin can invite).
- **Expert directory API** with search/filter support and bookmark support.
- **Chat hub/thread APIs** with tier-gating for private experts.
- **Dashboard aggregate API** returning recommended experts, recent conversations, and announcements.
- **Credit-tracking hook** via `chatEvents` entries with `creditsConsumed: 0` for Sprint 1.
- **Frontend shell** (`public/`) with sidebar navigation for dashboard, experts, chat, and team management.

## Run

```bash
npm start
```

Open <http://localhost:3000>.

Demo login is auto-executed in the browser using:

- `owner@acmefo.com`
- `Password!123`

## Tests

```bash
npm test
```

## Notes

- This is dependency-free and uses Node.js built-ins only, to run in constrained environments.
- Data is in-memory (`src/data.js`) and resets on server restart.
- Chat responses are stubs intended to connect to your existing agent infrastructure in a later iteration.

# SmartSpend — frontend demo

React 19 + Vite + Tailwind 4 + Recharts. Pages: Dashboard, Transactions, Budgets, Analytics, AI Assistant (demo), Goals, Settings, demo Login/Signup.

## Run

```bash
npm install
npm run dev
```

Open the local URL shown by Vite. For a production build, run `npm run build`.

## Important limitations

- Demo data is stored in browser localStorage; it is not a secure financial database.
- Login and signup are **UI demonstrations only**, not authentication. Passwords are not stored or transmitted.
- AI Assistant is a rules-based demo using deterministic calculations, not an LLM.
- Dashboard summary, Analytics, Transactions, Budgets and Goals use local data. Dashboard chart previews use illustrative mock data.
- CSV import is a basic parser, not suitable for arbitrary bank statements or quoted CSV fields.
- Never upload real banking information or credentials to this demo.

## Backend integration

Replace the localStorage state in `src/hooks/useFinance.js` with authenticated FastAPI endpoints. Keep server-side ownership checks, validation, audit logging, and secure session handling. Replace the assistant's local response function with a backend analytics service; compute amounts using SQL rather than trusting LLM arithmetic.

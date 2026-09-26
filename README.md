# StockSense — Centralized Inventory Management System

StockSense replaces manual registers, Excel sheets and scattered inventory
tracking with a single source of truth for stock. It is built for inventory
managers and warehouse staff who need accurate, auditable control over what
moves in and out of every storage location.

## Features

- **Authentication** — signup, login, logout, protected routes, session
  handling (Auth.js JWT sessions), bcrypt password hashing and an OTP-based
  password reset architecture (hashed, expiring, single-use 6-digit codes).
- **Products** — create/edit, unique SKUs, categories, units of measure,
  reorder levels, active/inactive, opening stock, per-location availability.
- **Warehouses & locations** — multiple warehouses, each with any number of
  locations; every stock quantity belongs to exactly one location.
- **Receipts (incoming stock)** — Draft → Validate → Done. Validation
  increases stock and writes ledger entries in one transaction.
- **Delivery orders (outgoing stock)** — Draft → Picking → Packed → Validate →
  Done. Delivering more than the available stock is impossible — the whole
  transaction rolls back.
- **Internal transfers** — move stock between locations atomically; total
  inventory never changes.
- **Stock adjustments** — physical counts (system 100, counted 97 → −3) with
  reason capture; confirming applies the difference with a ledger entry.
- **Stock movement ledger** — every unit explained: type, quantity, source,
  destination, reference document, user and before/after quantities.
- **Dashboard** — live KPIs (products in stock, low stock, out of stock,
  pending receipts, pending deliveries, scheduled transfers), movement charts,
  stock-by-category, alert tables and pending operations (Recharts).
- **Alerts** — low stock (quantity ≤ the product's own reorder level) and out
  of stock (= 0) surfaced on the dashboard, product views and operations UI.
- **Search & filters** — SKU/name search plus document type, status,
  warehouse/location and date-range filters across every module.

## Technology stack

| Layer      | Choice                                             |
| ---------- | -------------------------------------------------- |
| Frontend   | Next.js (App Router), React, TypeScript, Tailwind, shadcn-style UI |
| Backend    | Next.js Route Handlers + server-side service layer |
| Database   | PostgreSQL                                         |
| ORM        | Prisma                                             |
| Auth       | Auth.js (NextAuth v5), bcryptjs, OTP reset         |
| Validation | Zod                                                |
| Charts     | Recharts                                           |
| Tests      | Vitest (DB-backed integration + schema unit tests) |

## Architecture

```
Browser
  ↓
Next.js UI (server components + client components)
  ↓
Route Handlers (Zod validation, auth guard)          ← src/app/api/*
  ↓
Service layer (business logic, transactions)         ← src/lib/services/*
  ↓
Prisma                                               ← src/lib/db/prisma.ts
  ↓
PostgreSQL
```

### Stock consistency rule

`StockLevel` is the **only** source of truth for quantities. Every mutation
goes through the stock engine (`src/lib/services/stock.ts`):

```
BEGIN TRANSACTION
  1. Validate the operation (status, items, parties)
  2. Update stock  — decrements are atomic guarded updates (no negative stock)
  3. Insert the StockMovement ledger entry (same transaction)
  4. Update the operation status
COMMIT — any failure rolls back all of it
```

## Folder structure

```
src/
  app/
    (auth)/                 # login / signup / forgot / reset (split-screen layout)
    (app)/                  # authenticated shell (sidebar + header)
      dashboard/
      products/
      operations/{receipts,deliveries,transfers,adjustments,moves}/
      settings/warehouses/
      profile/
    api/                    # route handlers (auth, products, receipts, ...)
  components/
    ui/                     # shadcn-style primitives + domain badges
    layout/                 # sidebar, header
    auth/  products/  operations/  dashboard/  settings/  profile/
  lib/
    api.ts                  # ok/error responses, Zod body parsing, error mapping
    errors.ts               # typed domain errors -> HTTP statuses
    client-api.ts           # browser fetch wrapper
    auth/                   # session helpers
    db/                     # Prisma client singleton
    services/               # business logic & stock engine (one module per domain)
    validations/            # Zod schemas (auth, catalog, operations)
  types/                    # shared DTO contract between services and UI
prisma/
  schema.prisma             # normalized data model
  seed.ts                   # demo data seeded THROUGH the service layer
```

## Setup

```bash
# 1. Install dependencies
npm install

# 2. Create your environment file
cp .env.example .env

# 3. Push the schema to PostgreSQL
npx prisma db push

# 4. Generate the client (runs automatically on install/push)
npx prisma generate

# 5. Seed demo data (optional but recommended)
npx tsx prisma/seed.ts

# 6. Start developing
npm run dev
```

Demo credentials after seeding:

- `admin@stocksense.dev` / `Admin@12345` (ADMIN)
- `staff@stocksense.dev` / `Staff@12345` (STAFF)

## Environment variables

| Variable       | Purpose                                             |
| -------------- | --------------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection string used by Prisma         |
| `AUTH_SECRET`  | Auth.js session secret (`openssl rand -base64 32`)  |
| `AUTH_URL`     | Base URL in production (optional in dev)            |

Never commit `.env`. `.env.example` documents every required variable.

> **Password-reset delivery:** in production the OTP is meant to be emailed by
> your mail provider. In development the code is returned by the API and shown
> in the UI so the full flow can be tested without SMTP.

## Prisma commands

```bash
npx prisma generate      # regenerate the client after schema changes
npx prisma db push       # apply schema to the database (no migrations)
npx prisma studio        # browse data in a GUI
npx tsx prisma/seed.ts   # seed demo data
```

## Development commands

```bash
npm run dev        # dev server
npm run build      # production build
npm run start      # start the production server
npm run lint       # ESLint
npm run typecheck  # TypeScript strict check
npx vitest run     # test suite
```

## Testing

`npx vitest run` executes DB-backed integration tests plus validation unit
tests. Integration tests create isolated fixtures and clean up after
themselves. Coverage includes the critical invariants:

- Receipt: `100 + 50 = 150` (with before/after ledger entry)
- Delivery: `150 - 20 = 130`
- Transfer: source `100` → move `30` → `70` / `30`, total stays `100`
- Adjustment: system `100`, counted `97` → final `97`, difference `−3`
- Rejects: over-delivery, over-transfer, negative stock, double validation,
  duplicate SKUs — with full transaction rollback
- Zod API validation of malformed payloads

## Git workflow (four-member team)

```
main
 ├── member-1--auth-products      # authentication + product management
 ├── member-2--receipts           # receipts / incoming stock
 ├── member-3--deliveries         # delivery orders + internal transfers
 └── member-4--ashwin             # dashboard + adjustments + alerts + filters
```

1. Each member works on their own module against the shared schema and the
   service interfaces in `src/lib/services/` + DTOs in `src/types/`.
2. Schema changes are coordinated through `prisma/schema.prisma` (single
   owner per PR, reviewed by the whole team).
3. Open a PR per module; keep `npx vitest run`, `npm run typecheck` and
   `npm run build` green before merging.
4. Never commit `.env`.

### Module ownership map

| Area                                                        | Owner    |
| ----------------------------------------------------------- | -------- |
| `src/auth*`, `(auth)/*`, `api/auth/*`, products module      | Member 1 |
| `receipts.service.ts`, `api/receipts/*`, receipts UI        | Member 2 |
| `deliveries.service.ts`, `transfers.service.ts` + APIs + UI | Member 3 |
| `dashboard.service.ts`, `adjustments.service.ts`, moves, alerts, filters | Member 4 |

## API overview

```
POST /api/auth/signup | /forgot-password | /reset-password
GET|POST /api/products          GET|PATCH /api/products/[id]
GET|POST /api/warehouses        POST /api/locations
GET|POST /api/receipts          POST /api/receipts/[id]/validate
GET|POST /api/deliveries        POST /api/deliveries/[id]/validate
PATCH /api/deliveries/[id]/status
GET|POST /api/transfers         POST /api/transfers/[id]/validate
GET|POST /api/adjustments       POST /api/adjustments/[id]/validate
GET /api/movements              GET /api/dashboard
```

All endpoints validate input with Zod, require an authenticated session and
return structured errors (`{ error: { code, message, fields? } }`) with proper
HTTP status codes.

# Architecture

UdyamOne remains a Streamlit application with `app.py` as its entry point. The flow is `Streamlit UI → data loaders/repository → deterministic engines → supplied CSV datasets`.

- `src/config/settings.py` centralizes paths and upload limits.
- `src/data/loaders.py` loads and caches the catalogue, synthetic mock registries, and generated synthetic demo analytics.
- `src/engines/` contains deterministic catalogue eligibility, pricing, and recommendations. There is no LLM path that can override these decisions.
- `src/database/` persists businesses, quotes, orders, order events, consent, and structured KYC results in SQLite.
- `src/services/registry_service.py` separates identifier format checks from mock registry existence/status.
- `app.py` supplies the customer journey and operations dashboard.

SQLite is a local/demo adapter. Production should use managed storage, authentication/authorization, and database migrations. Live Airtel, government registry, OCR, payment, and notification integrations are not configured.

Recurring charges use the supplied minimum monthly rate. Quotes include setup charges, maximum minimum-contract duration, and longest listed typical installation estimate. No taxes, discounts, or negotiated pricing are inferred. Per-site recurring products scale by profile site count.

The dashboard reads the committed `data/analytics/synthetic_demo_leads.csv`, applies selected segment and city-tier filters to all metrics, and calculates results from those filtered synthetic rows. It has no business names, registration numbers, contact details, or source lead IDs. The generator in `scripts/generate_synthetic_analytics.py` uses fixed fictional distributions and never reads the Git-ignored local `smb_leads.csv`.

On startup, the app creates the configured SQLite parent directory and schema. Relative `UDYAMONE_DB_PATH` values resolve from the repository root. Community Cloud local storage is ephemeral and shared between app sessions; do not store real customer data there.

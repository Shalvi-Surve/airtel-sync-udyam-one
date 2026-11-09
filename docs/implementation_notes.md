# Implementation notes

## Audit findings

The original repository contained a styled Streamlit landing page and source CSVs. Most listed source modules, pending pages, tests, docs, and assets were zero bytes. No existing business logic was available to preserve. The app uses the tracked 25-product catalogue, synthetic mock registries, and a separate generated analytics dataset. The locally supplied `smb_leads.csv` is Git-ignored and is not an application dependency.

## Assumptions

- Catalogue minimum monthly prices are used for estimates; max price is shown while browsing.
- Per-site recurring products scale by the profile site count. Setup is multiplied by selected quantity because the dataset does not specify per-site setup charging.
- Business segments use the dataset's `micro`, `prof`, `multi`, and `mfg` codes.
- Mock registry matches do not prove real government status.
- Uploads are not persisted, OCR processed, or content verified.
- Advisor goal matching filters catalogue categories; deterministic eligibility remains authoritative.
- The in-app clinic demo uses the Balaji Dental Care record pair in the supplied mock registries and a bundle that satisfies the supplied catalogue requirements. It is labeled as synthetic mock data.
- Operations charts use `data/analytics/synthetic_demo_leads.csv`; regenerate it with `python scripts/generate_synthetic_analytics.py`. The generator uses a fixed seed and hard-coded fictional cohorts and never reads local lead data.
- Sample PDFs are watermarked and generated in memory. Upload handling checks type, signature, and size only; it does not parse or validate document claims.

## Follow-up

- Complete English/Hindi translation.
- Add catalogue snapshots and quote expiry handling; quote recalculation history is now recorded for demo revisions.
- Expand KYC to address/signatory checks and secure production document processing.
- Bundle eligibility is checked before quote save/recalculation and revalidated against current catalogue pricing/rules when accepting a quote.
- Add remaining analytics breakdowns and production access controls.
- Add authentication, authorization, encryption, migrations, and managed storage before production use.
- Community Cloud deployment remains an external verification step. Use the root `requirements.txt`, root `.streamlit/config.toml`, and `app.py` entrypoint; no apt packages or secrets are required for the demo.

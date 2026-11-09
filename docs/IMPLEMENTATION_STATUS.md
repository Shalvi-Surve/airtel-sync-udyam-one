# UdyamOne Community Cloud demo readiness

Audit date: 2026-11-09

## Deployment preparation completed

- The Operations Dashboard reads the committed `data/analytics/synthetic_demo_leads.csv`, a deterministic, clearly labelled dataset of fictional cohort rows. It contains no real names, contact information, registration numbers, addresses, or source lead IDs. `scripts/generate_synthetic_analytics.py` recreates the file without reading the Git-ignored `smb_leads.csv`.
- `data/analytics/README.md` documents provenance and regeneration. Dashboard title, baseline, and chart captions identify all results as synthetic demo metrics.
- Startup initializes the SQLite database and schema, creating its parent folder automatically. `UDYAMONE_DB_PATH` accepts absolute paths; relative values resolve from the repository root. A database failure or missing required catalogue/registry data shows a short actionable error and stops before the app renders partial pages.
- All catalogue, mock registry, analytics, stylesheet, Streamlit config, and dependency files used by the demo live in the repository. No developer-machine absolute paths are required.
- The sidebar's **Load synthetic clinic demo** action seeds the sample profile and starter bundle. No manual SQLite setup or database seed command is needed. A global database reset control is intentionally omitted: it could erase another active visitor's state on the shared Cloud app. A new Streamlit session starts with a fresh session-bound business ID.
- Community Cloud deployment instructions are in `README.md`. The runtime has a root `requirements.txt`, root `.streamlit/config.toml`, and an empty `packages.txt` because no OS-level package is required.

## Verified behavior

- `python -m compileall -q app.py src tests scripts` completed successfully.
- `python -m pytest -q` passed **31 tests**. Coverage includes pricing, eligibility/dependencies, mock registry checks, upload size/signature checks, synthetic analytics values/labels, required-data and SQLite startup errors, fresh schema creation, all nine navigation destinations, and the end-to-end quote → failed/recovered KYC → simulated activation journey.
- Synthetic PDF generation checks verify the PDF header, watermark, and trailer. PDF buttons are rendered on the Smart KYC page; the browser download path still requires a live browser click-through before claiming that a file download was completed.
- Desktop/mobile layout inspection from the preceding release audit covered 1280×720 and 390×844. Responsive overview content collapsed to one column without horizontal overflow. This audit additionally tested all nine destination pages with AppTest.
- Package versions installed locally satisfy the declared requirements. Community Cloud's actual build/deployment has not been performed.

## Deployment steps

1. Review and commit the repository, including `data/analytics/synthetic_demo_leads.csv`; do not add `data/analytics/smb_leads.csv`.
2. Push the branch to GitHub.
3. In Streamlit Community Cloud, create an app for that repository and branch with `app.py` as the main file.
4. No secrets or apt packages are needed for the synthetic demo. Keep the default SQLite path unless a different writable demo path is required.
5. After deployment, verify the Cloud build log, Overview, Operations Dashboard charts/filters, synthetic PDF downloads, and the full simulated clinic journey.

These are instructions only; successful Cloud deployment has not been claimed or tested.

## Remaining limitations and risks

- Community Cloud local filesystem persistence is not guaranteed and the SQLite database is shared between app sessions. Demo quotes/orders may disappear after a restart or rebuild. Do not store real customer data here.
- There is no authentication or per-business authorization. A global reset could destroy other users' demo state and is intentionally not exposed.
- Mock registries, KYC, and order progress are synthetic/simulated. Upload bytes receive basic signature/size checks only; contents are not extracted or verified. Do not upload real documents.
- Quote estimates use catalogue starting prices and setup fees; tax, discounts, enforcement, and expiry are not modeled. Hindi support is limited to navigation labels.
- The private/local `smb_leads.csv` is ignored by Git and not read. Analytics are generated demo figures and must not be described as actual business performance.
- An actual Community Cloud build and live browser verification of PDF downloads and the full remote journey remain outstanding.
- This demo is not ready for real-customer onboarding or production fulfilment.

# UdyamOne

UdyamOne is a Streamlit demonstration of a catalogue-driven MSME onboarding journey for Airtel Business services. The workflow connects business profile capture, deterministic recommendations, product selection, indicative quote saving, consent-first mock registry checks, and simulated order tracking.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The application uses the catalogue, synthetic mock registries, and synthetic analytics under `data/`. On first start it creates `storage/udyamone.sqlite` and its schema automatically; no manual database setup or seed command is required. Change the path with `UDYAMONE_DB_PATH` (relative paths resolve from the repository root).

## What works

- English and Hindi page navigation labels.
- Business profile capture persisted in local SQLite.
- Searchable, filterable catalogue from the supplied 25 products.
- Deterministic product eligibility, recommendation, setup fee and minimum-rate bundle calculations.
- Saved quotes, quote acceptance, unique demo order references, and guarded order transitions.
- Quote recalculation from the current bundle, with saved revisions and rejection of recalculation after acceptance.
- Consent recording/withdrawal and GSTIN/Udyam format plus mock registry checks.
- Downloadable, watermarked synthetic sample certificates plus PDF/PNG/JPEG signature and size checks. Files are held in memory and not saved or OCR processed.
- Operations charts calculated from the committed synthetic demo CSV with segment/city-tier filters. The dataset is generated, labelled, and contains no real lead identifiers. The separate local `smb_leads.csv` remains ignored and is never loaded by the app.

## Try the synthetic clinic journey

1. Start the app with `streamlit run app.py`.
2. Select **Load synthetic clinic demo** in the sidebar. This loads the synthetic Balaji Dental Care profile and starter bundle; it also saves the profile to the local demo database.
3. Open **Bundle Builder**, review and save the quote, then open **Quotes & Orders** to recalculate or accept it.
4. In **Smart KYC**, record consent and run the mock checks. Use the synthetic GSTIN/Udyam values prefilled by the demo button, or intentionally enter an invalid value to see the recovery path.
5. In **Order Tracker**, advance the simulated order through each available state.

All identifiers, KYC results, and fulfilment states in this path are synthetic or mocked. No real service is ordered or activated. New visitor sessions start with an empty quote/order journey; there is intentionally no global database reset button because the Cloud demo database is shared by active sessions.

## Demo-only features and limitations

There is no live Airtel, government registry, LLM, OCR, payment, notification, installation, or activation integration. Registry results come from mock CSVs. Order lifecycle updates are simulated. Quotes use catalogue starting rates without taxes or unsupported discounts. Upload handling checks file signatures but does not verify document contents; synthetic PDFs exist only to test upload handling and must not be treated as verified documents. English/Hindi support currently covers navigation labels; not all content is translated. Analytics metrics describe generated synthetic records, not market or Airtel performance.

SQLite is suitable for a local demonstration. Streamlit Community Cloud local storage is not a durable production database. Production use needs managed storage, authentication/authorization, encryption and retention controls, security review, real integration adapters, and operational monitoring.

## Streamlit Community Cloud

The repository uses a root-level `requirements.txt`, a root-level `.streamlit/config.toml`, and does not require operating-system packages (`packages.txt` is intentionally empty). Application data and CSS paths are resolved from the repository files; there are no local-machine path dependencies. `data/analytics/synthetic_demo_leads.csv` is committed, so the dashboard has demo data in a clean checkout. The app has not been deployed to Community Cloud.

To deploy: push this repository to a GitHub repository; in Streamlit Community Cloud choose **Create app**, select that repository and branch, and set the main file path to `app.py`; leave secrets empty for this demo; then deploy. Confirm the build completes and smoke-test the demo journey after deployment. SQLite is created automatically in the app's local storage, but Community Cloud storage can be lost on restart/rebuild and is shared by sessions, so it is for demonstration only. Do not use real customer data. A deployment has not been performed or verified as part of this audit.

## Tests

Run `python -m compileall -q app.py src tests` and `python -m pytest -q`.

## Data handling

The local source analytics file `data/analytics/smb_leads.csv` remains ignored by Git because it may contain identifiable lead data. The application uses only the committed synthetic dataset. See `docs/privacy.md` before handling sensitive information.

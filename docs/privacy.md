# Privacy and demo data handling

This demonstration must not process real identity documents or sensitive customer records.

- Included registries are mock data; no government lookup occurs.
- Uploaded PDF/PNG/JPEG data is checked in memory for actual file signature and size (5 MB default). The app does not save uploads, extract text, or claim document verification.
- The consent screen records the user's choice for mock registry verification; choosing unchecked records consent withdrawal.
- Structured business profiles, quotes, consent records, and KYC check outcomes are stored in local SQLite, which is not encrypted by this demo.
- The app's analytics dashboard uses only committed generated synthetic data, labelled in the CSV and UI; it contains no real business identifiers or source lead IDs.
- The separate local `data/analytics/smb_leads.csv` may contain sensitive fields, is ignored by Git, and is never loaded by the application or analytics generator. Do not commit or distribute it.
- Community Cloud uses shared, ephemeral local storage for this demo. Do not enter real business identifiers or documents; there is no authentication or per-user database authorization.

Production requires authentication/authorization, encryption in transit and at rest, retention/deletion workflows, least-privilege data access, managed secrets, secure temporary document processing, and privacy/security review.

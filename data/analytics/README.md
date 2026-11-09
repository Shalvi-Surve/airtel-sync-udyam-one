# Public analytics demo data

`synthetic_demo_leads.csv` is a deterministic, generated demonstration dataset. Its rows are fictional combinations of segment, city tier, coarse workflow stage, registry-presence flag, simulated outcome, and broad drop reason. It contains no real business names, contact details, registration numbers, addresses, or source lead identifiers.

Regenerate the committed deployment file with:

```powershell
python scripts/generate_synthetic_analytics.py
```

The generator does not read `smb_leads.csv`. That separate local file remains Git-ignored and is not used by the application. Dashboard figures based on this file describe synthetic rows only and must not be presented as actual Airtel or market performance.

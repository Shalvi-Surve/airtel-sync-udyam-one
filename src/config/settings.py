"""Central application paths and settings."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CATALOGUE_PATH = DATA_DIR / "catalogue" / "product_catalogue.csv"
GSTIN_REGISTRY_PATH = DATA_DIR / "registries" / "mock_gstin_registry.csv"
UDYAM_REGISTRY_PATH = DATA_DIR / "registries" / "mock_udyam_registry.csv"
ANALYTICS_PATH = DATA_DIR / "analytics" / "synthetic_demo_leads.csv"
DB_PATH = Path(os.getenv("UDYAMONE_DB_PATH", str(ROOT / "storage" / "udyamone.sqlite"))).expanduser()
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH
MAX_UPLOAD_BYTES = int(os.getenv("UDYAMONE_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Point at an isolated SQLite file before any app module is imported,
# so tests never touch the local dev database.
_test_db_path = Path(tempfile.gettempdir()) / "fieldsense_test.db"
if _test_db_path.exists():
    _test_db_path.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"

import pytest  # noqa: E402

from database import init_db  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _init_test_db():
    init_db()

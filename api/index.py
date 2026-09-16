import sys
from pathlib import Path

from mangum import Mangum

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app  # noqa: E402

handler = Mangum(app, lifespan="off")

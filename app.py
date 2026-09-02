from pathlib import Path

# Chemins d'accès dynamiques basés sur la racine du projet
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "igoudar_logo.png"

# Chargement du favicon et conversion base64
try:
    _favicon = Image.open(LOGO_PATH)
    with open(LOGO_PATH, "rb") as _f:
        _LOGO_B64 = base64.b64encode(_f.read()).decode("ascii")
except Exception:
    _favicon = "📈"
    _LOGO_B64 = ""

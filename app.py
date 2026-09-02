LOGO_PATH = "assets/igoudar_logo.png"
_favicon = Image.open(LOGO_PATH)
with open(LOGO_PATH, "rb") as _f:
    _LOGO_B64 = base64.b64encode(_f.read()).decode("ascii")

from pathlib import Path

PROJECT_NAME = "AI Resume Analyzer"
VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_FOLDER = DATA_DIR / "uploads"
DATABASE_NAME = "resume_analyzer.db"

ALLOWED_FILE_TYPES = (".pdf", ".docx")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

THEME_COLORS = {
    "primary":    "#1E3A5F",
    "secondary":  "#3D7EA6",
    "accent":     "#F4A261",
    "background": "#F8F9FA",
    "surface":    "#FFFFFF",
    "text":       "#212529",
    "text_muted": "#6C757D",
    "success":    "#2A9D8F",
    "warning":    "#E9C46A",
    "error":      "#E76F51",
}

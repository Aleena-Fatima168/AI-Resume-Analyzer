from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

from config import DATA_DIR, DATABASE_NAME
from utils.resume_parser import ResumeData

DB_PATH: Path = DATA_DIR / DATABASE_NAME

_DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS resumes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    filename     TEXT    NOT NULL,
    file_type    TEXT    NOT NULL,
    name         TEXT,
    email        TEXT,
    phone        TEXT,
    github       TEXT,
    linkedin     TEXT,
    raw_text     TEXT    NOT NULL DEFAULT '',
    uploaded_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS resume_sections (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    section   TEXT    NOT NULL,
    content   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS resume_skills (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    skill     TEXT    NOT NULL,
    category  TEXT    NOT NULL DEFAULT 'Other'
);

CREATE TABLE IF NOT EXISTS resume_scores (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id      INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    total_score    REAL    NOT NULL,
    ats_score      REAL    NOT NULL,
    section_scores TEXT    NOT NULL DEFAULT '{}',
    feedback       TEXT    NOT NULL DEFAULT '[]',
    scored_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sections_resume  ON resume_sections(resume_id);
CREATE INDEX IF NOT EXISTS idx_skills_resume    ON resume_skills(resume_id);
CREATE INDEX IF NOT EXISTS idx_skills_category  ON resume_skills(category);
CREATE INDEX IF NOT EXISTS idx_scores_resume    ON resume_scores(resume_id);
CREATE INDEX IF NOT EXISTS idx_scores_scored_at ON resume_scores(scored_at);
"""


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialise(self) -> None:
        with self.connect() as conn:
            conn.executescript(_DDL)

    @property
    def path(self) -> Path:
        return self._path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


class ResumeRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def insert(self, data: ResumeData, filename: str, file_type: str) -> int:
        with self._db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO resumes
                    (filename, file_type, name, email, phone, github, linkedin,
                     raw_text, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename, file_type,
                    data.name, data.email, data.phone, data.github, data.linkedin,
                    data.raw_text, _now_iso(),
                ),
            )
            resume_id: int = cur.lastrowid  # type: ignore[assignment]

            section_rows: list[tuple[int, str, str]] = []
            for section in ("education", "experience", "projects", "certifications", "languages", "skills"):
                for line in getattr(data, section, []):
                    if line.strip():
                        section_rows.append((resume_id, section, line.strip()))

            if section_rows:
                conn.executemany(
                    "INSERT INTO resume_sections (resume_id, section, content) VALUES (?, ?, ?)",
                    section_rows,
                )

        return resume_id

    def delete(self, resume_id: int) -> bool:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            deleted = cur.rowcount > 0
        return deleted

    def get(self, resume_id: int) -> dict[str, Any] | None:
        with self._db.connect() as conn:
            row = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
        return _row_to_dict(row)

    def get_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM resumes ORDER BY uploaded_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_sections(self, resume_id: int) -> dict[str, list[str]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT section, content FROM resume_sections WHERE resume_id = ? ORDER BY id",
                (resume_id,),
            ).fetchall()
        result: dict[str, list[str]] = {}
        for row in rows:
            result.setdefault(row["section"], []).append(row["content"])
        return result

    def count(self) -> int:
        with self._db.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM resumes").fetchone()
        return row["n"] if row else 0

    def search_by_name(self, name: str) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM resumes WHERE name LIKE ? ORDER BY uploaded_at DESC",
                (f"%{name}%",),
            ).fetchall()
        return [dict(r) for r in rows]


class SkillRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def insert(self, resume_id: int, categorized: dict[str, list[str]]) -> int:
        rows: list[tuple[int, str, str]] = [
            (resume_id, skill, category)
            for category, skills in categorized.items()
            for skill in skills
            if skill.strip()
        ]
        if not rows:
            return 0
        with self._db.connect() as conn:
            conn.executemany(
                "INSERT INTO resume_skills (resume_id, skill, category) VALUES (?, ?, ?)",
                rows,
            )
        return len(rows)

    def delete_for_resume(self, resume_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM resume_skills WHERE resume_id = ?", (resume_id,))

    def get_for_resume(self, resume_id: int) -> dict[str, list[str]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT skill, category FROM resume_skills WHERE resume_id = ? ORDER BY category, skill",
                (resume_id,),
            ).fetchall()
        result: dict[str, list[str]] = {}
        for row in rows:
            result.setdefault(row["category"], []).append(row["skill"])
        return result

    def get_flat_for_resume(self, resume_id: int) -> list[str]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT skill FROM resume_skills WHERE resume_id = ? ORDER BY id",
                (resume_id,),
            ).fetchall()
        return [r["skill"] for r in rows]

    def get_category_counts(self, resume_id: int) -> dict[str, int]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT category, COUNT(*) AS cnt
                FROM resume_skills
                WHERE resume_id = ?
                GROUP BY category
                ORDER BY cnt DESC
                """,
                (resume_id,),
            ).fetchall()
        return {r["category"]: r["cnt"] for r in rows}

    def get_global_top_skills(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT skill, category, COUNT(*) AS count
                FROM resume_skills
                GROUP BY skill
                ORDER BY count DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


class ScoreRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def insert(
        self,
        resume_id: int,
        total_score: float,
        ats_score: float,
        section_scores: dict[str, float],
        feedback: list[str],
    ) -> int:
        with self._db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO resume_scores
                    (resume_id, total_score, ats_score, section_scores, feedback, scored_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    resume_id,
                    round(float(total_score), 2),
                    round(float(ats_score), 2),
                    json.dumps(section_scores),
                    json.dumps(feedback),
                    _now_iso(),
                ),
            )
        return cur.lastrowid  # type: ignore[return-value]

    def get_latest(self, resume_id: int) -> dict[str, Any] | None:
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM resume_scores
                WHERE resume_id = ?
                ORDER BY scored_at DESC
                LIMIT 1
                """,
                (resume_id,),
            ).fetchone()
        return self._deserialise(row)

    def get_history(self, resume_id: int) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM resume_scores WHERE resume_id = ? ORDER BY scored_at ASC",
                (resume_id,),
            ).fetchall()
        return [r for r in (self._deserialise(row) for row in rows) if r is not None]

    def get_score_trend(self, resume_id: int) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT scored_at, total_score, ats_score
                FROM resume_scores
                WHERE resume_id = ?
                ORDER BY scored_at ASC
                """,
                (resume_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_average_score(self, resume_id: int) -> float | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT AVG(total_score) AS avg FROM resume_scores WHERE resume_id = ?",
                (resume_id,),
            ).fetchone()
        return round(row["avg"], 2) if row and row["avg"] is not None else None

    def get_global_score_stats(self) -> dict[str, Any]:
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*)          AS count,
                    AVG(total_score)  AS avg_total,
                    AVG(ats_score)    AS avg_ats,
                    MAX(total_score)  AS max_total,
                    MIN(total_score)  AS min_total
                FROM resume_scores
                """
            ).fetchone()
        if not row or row["count"] == 0:
            return {"count": 0, "avg_total": None, "avg_ats": None,
                    "max_total": None, "min_total": None}
        return {
            "count":     row["count"],
            "avg_total": round(row["avg_total"], 2),
            "avg_ats":   round(row["avg_ats"], 2),
            "max_total": round(row["max_total"], 2),
            "min_total": round(row["min_total"], 2),
        }

    @staticmethod
    def _deserialise(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        d = dict(row)
        d["section_scores"] = json.loads(d.get("section_scores") or "{}")
        d["feedback"]       = json.loads(d.get("feedback")       or "[]")
        return d


class DatabaseManager:
    def __init__(self, path: Path | str | None = None) -> None:
        db_path = Path(path) if path is not None else DB_PATH
        self._db = Database(db_path)
        self._db.initialise()

        self.resumes = ResumeRepository(self._db)
        self.skills  = SkillRepository(self._db)
        self.scores  = ScoreRepository(self._db)

    def save_analysis(
        self,
        resume_data: ResumeData,
        filename: str,
        file_type: str,
        categorized_skills: dict[str, list[str]],
        total_score: float,
        ats_score: float,
        section_scores: dict[str, float],
        feedback: list[str],
    ) -> int:
        resume_id = self.resumes.insert(resume_data, filename, file_type)
        self.skills.insert(resume_id, categorized_skills)
        self.scores.insert(resume_id, total_score, ats_score, section_scores, feedback)
        return resume_id

    def get_full_record(self, resume_id: int) -> dict[str, Any] | None:
        resume = self.resumes.get(resume_id)
        if resume is None:
            return None
        resume["sections"] = self.resumes.get_sections(resume_id)
        resume["skills"]   = self.skills.get_for_resume(resume_id)
        resume["score"]    = self.scores.get_latest(resume_id)
        return resume

    def get_dashboard_stats(self) -> dict[str, Any]:
        return {
            "total_resumes": self.resumes.count(),
            "score_stats":   self.scores.get_global_score_stats(),
            "top_skills":    self.skills.get_global_top_skills(limit=10),
        }

    @property
    def db_path(self) -> Path:
        return self._db.path

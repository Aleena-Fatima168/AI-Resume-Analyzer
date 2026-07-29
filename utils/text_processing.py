from __future__ import annotations

import re
import unicodedata


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\S\n\t ]+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    result: list[str] = []
    blanks = 0
    for ln in lines:
        if ln == "":
            blanks += 1
            if blanks <= 1:
                result.append(ln)
        else:
            blanks = 0
            result.append(ln)
    return "\n".join(result).strip()


def split_into_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


SECTION_ALIASES: dict[str, list[str]] = {
    "education": ["education", "academic background", "academic qualifications", "qualifications"],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
    ],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "project work"],
    "certifications": [
        "certifications", "certification", "certificates", "licences", "licenses",
        "professional development",
    ],
    "skills": ["skills", "technical skills", "core competencies", "competencies", "technologies"],
    "languages": ["languages", "language proficiency", "spoken languages"],
    "summary": ["summary", "profile", "objective", "about me", "professional summary", "career objective"],
}


def _is_section_heading(line: str, keywords: list[str]) -> bool:
    return line.strip().lower().rstrip(":") in keywords


def find_section_bounds(lines: list[str], section: str) -> tuple[int, int] | None:
    target_kws = SECTION_ALIASES.get(section.lower(), [section.lower()])
    all_heading_kws = [kw for kws in SECTION_ALIASES.values() for kw in kws]

    start: int | None = None
    for i, line in enumerate(lines):
        if start is None:
            if _is_section_heading(line, target_kws):
                start = i + 1
        else:
            if _is_section_heading(line, all_heading_kws):
                return (start, i)

    if start is not None:
        return (start, len(lines))
    return None


def extract_section_lines(lines: list[str], section: str) -> list[str]:
    bounds = find_section_bounds(lines, section)
    if bounds is None:
        return []
    start, end = bounds
    return [ln for ln in lines[start:end] if ln.strip()]

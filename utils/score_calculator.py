from __future__ import annotations

from dataclasses import dataclass, field

from utils.resume_parser import ResumeData

_SECTION_WEIGHTS: dict[str, float] = {
    "contact":    0.15,
    "skills":     0.25,
    "experience": 0.25,
    "education":  0.20,
    "projects":   0.10,
    "extras":     0.05,
}


@dataclass
class ScoreResult:
    total_score:    float
    ats_score:      float
    section_scores: dict[str, float] = field(default_factory=dict)
    feedback:       list[str]        = field(default_factory=list)

    @property
    def grade(self) -> str:
        if self.total_score >= 85:
            return "Excellent"
        if self.total_score >= 70:
            return "Good"
        if self.total_score >= 50:
            return "Fair"
        return "Needs Work"

    @property
    def grade_color(self) -> str:
        return {
            "Excellent":  "#2A9D8F",
            "Good":       "#3D7EA6",
            "Fair":       "#E9C46A",
            "Needs Work": "#E76F51",
        }[self.grade]


class ResumeScorer:
    def score(self, data: ResumeData, skills: list[str]) -> ScoreResult:
        sections, feedback = self._section_scores(data, skills)
        total = round(sum(sections[k] * w for k, w in _SECTION_WEIGHTS.items()), 2)
        ats   = round(self._ats_score(data, skills), 2)
        return ScoreResult(
            total_score=total,
            ats_score=ats,
            section_scores=sections,
            feedback=feedback,
        )

    def _section_scores(
        self, data: ResumeData, skills: list[str]
    ) -> tuple[dict[str, float], list[str]]:
        scores: dict[str, float] = {}
        feedback: list[str] = []

        contact_fields = [data.name, data.email, data.phone, data.github, data.linkedin]
        filled = sum(1 for f in contact_fields if f)
        scores["contact"] = round(filled / len(contact_fields) * 100, 1)
        if not data.email:
            feedback.append("Add an email address to your contact section.")
        if not data.phone:
            feedback.append("Include a phone number for recruiter contact.")
        if not data.linkedin:
            feedback.append("Add a LinkedIn profile URL to boost credibility.")

        skill_count = len(skills)
        if skill_count == 0:
            scores["skills"] = 0.0
            feedback.append("No recognisable skills detected — list technical skills explicitly.")
        elif skill_count < 5:
            scores["skills"] = 40.0
            feedback.append("Expand your skills section; aim for at least 8–10 key skills.")
        elif skill_count < 10:
            scores["skills"] = 65.0
            feedback.append("Good start on skills — consider adding more domain-specific tools.")
        elif skill_count < 20:
            scores["skills"] = 85.0
        else:
            scores["skills"] = 100.0

        exp_lines = len(data.experience)
        if exp_lines == 0:
            scores["experience"] = 0.0
            feedback.append("No work experience section detected — add employment history.")
        elif exp_lines < 3:
            scores["experience"] = 40.0
            feedback.append("Expand experience entries with responsibilities and achievements.")
        elif exp_lines < 8:
            scores["experience"] = 70.0
            feedback.append("Add quantified achievements (e.g. 'reduced latency by 30%').")
        else:
            scores["experience"] = 100.0

        edu_lines = len(data.education)
        if edu_lines == 0:
            scores["education"] = 0.0
            feedback.append("No education section found — include your highest qualification.")
        elif edu_lines < 2:
            scores["education"] = 60.0
            feedback.append("Add graduation year and field of study to your education entry.")
        else:
            scores["education"] = 100.0

        proj_lines = len(data.projects)
        if proj_lines == 0:
            scores["projects"] = 0.0
            feedback.append("Add a projects section to showcase practical experience.")
        elif proj_lines < 3:
            scores["projects"] = 55.0
            feedback.append("Describe project outcomes and technologies used.")
        else:
            scores["projects"] = 100.0

        extras = len(data.certifications) + len(data.languages)
        scores["extras"] = min(extras * 20.0, 100.0)

        return scores, feedback

    def _ats_score(self, data: ResumeData, skills: list[str]) -> float:
        points = 0.0
        total  = 0.0

        total += 30
        contact_fields = [data.name, data.email, data.phone]
        points += sum(10 for f in contact_fields if f)

        total += 30
        if len(skills) >= 15:
            points += 30
        elif len(skills) >= 8:
            points += 20
        elif len(skills) >= 3:
            points += 10

        total += 30
        if data.experience:
            points += 10
        if data.education:
            points += 10
        if data.skills or skills:
            points += 10

        total += 10
        word_count = len(data.raw_text.split())
        if 200 <= word_count <= 1200:
            points += 10
        elif word_count > 100:
            points += 5

        return round(points / total * 100, 2)

from __future__ import annotations

from dataclasses import dataclass, field

JOB_PROFILES: dict[str, dict] = {
    "Python Developer": {
        "icon": "",
        "description": (
            "Build scalable back-end services, automation scripts, and data "
            "pipelines using Python and its ecosystem."
        ),
        "required": {
            "Python": 1.0, "Git": 1.0, "REST API": 1.0,
            "SQL": 1.0, "pytest": 0.8,
        },
        "nice_to_have": [
            "FastAPI", "Django", "Flask", "PostgreSQL", "Docker",
            "Redis", "Celery", "SQLAlchemy", "GitHub Actions",
        ],
        "salary_range": "$85,000 – $145,000 / yr",
        "growth": "High",
    },
    "Data Analyst": {
        "icon": "",
        "description": (
            "Transform raw data into actionable insights through querying, "
            "visualisation, and statistical analysis."
        ),
        "required": {
            "SQL": 1.0, "Python": 1.0, "Pandas": 1.0,
            "Matplotlib": 0.8, "Excel": 0.8,
        },
        "nice_to_have": [
            "NumPy", "Seaborn", "Plotly", "Tableau", "Power BI",
            "scikit-learn", "Snowflake", "BigQuery", "dbt",
        ],
        "salary_range": "$70,000 – $120,000 / yr",
        "growth": "High",
    },
    "Software Engineer": {
        "icon": "",
        "description": (
            "Design, develop, and maintain production software across the "
            "full stack with a focus on reliability and performance."
        ),
        "required": {
            "Git": 1.0, "REST API": 1.0, "SQL": 1.0,
            "CI/CD": 1.0, "Docker": 0.9,
        },
        "nice_to_have": [
            "Python", "Java", "TypeScript", "Kubernetes", "PostgreSQL",
            "Redis", "GitHub Actions", "Terraform", "AWS",
        ],
        "salary_range": "$95,000 – $165,000 / yr",
        "growth": "High",
    },
    "AI Engineer": {
        "icon": "",
        "description": (
            "Build and deploy machine-learning models and LLM-powered "
            "applications from research prototype to production."
        ),
        "required": {
            "Python": 1.0, "Machine Learning": 1.0, "PyTorch": 1.0,
            "scikit-learn": 0.9, "NumPy": 0.8,
        },
        "nice_to_have": [
            "TensorFlow", "Hugging Face", "LangChain", "OpenAI API",
            "MLflow", "Docker", "FastAPI", "Pandas", "ONNX",
            "Natural Language Processing", "Deep Learning",
        ],
        "salary_range": "$120,000 – $200,000 / yr",
        "growth": "High",
    },
    "Backend Developer": {
        "icon": "",
        "description": (
            "Architect and implement server-side logic, APIs, databases, "
            "and integrations that power web and mobile products."
        ),
        "required": {
            "REST API": 1.0, "SQL": 1.0, "Git": 1.0,
            "Docker": 1.0, "PostgreSQL": 0.9,
        },
        "nice_to_have": [
            "Node.js", "Python", "Java", "Redis", "Kafka",
            "Kubernetes", "AWS", "Nginx", "GraphQL", "JWT",
        ],
        "salary_range": "$90,000 – $155,000 / yr",
        "growth": "High",
    },
    "Frontend Developer": {
        "icon": "",
        "description": (
            "Craft responsive, accessible user interfaces using modern "
            "JavaScript frameworks and CSS tooling."
        ),
        "required": {
            "JavaScript": 1.0, "HTML5": 1.0, "CSS3": 1.0,
            "React": 1.0, "Git": 0.9,
        },
        "nice_to_have": [
            "TypeScript", "Next.js", "Tailwind CSS", "Vite", "Redux",
            "Jest", "Storybook", "Figma", "GraphQL Client", "Webpack",
        ],
        "salary_range": "$80,000 – $140,000 / yr",
        "growth": "Medium",
    },
    "Cloud Engineer": {
        "icon": "",
        "description": (
            "Design, provision, and operate cloud infrastructure with a "
            "focus on scalability, security, and cost efficiency."
        ),
        "required": {
            "AWS": 1.0, "Terraform": 1.0, "Docker": 1.0,
            "Kubernetes": 1.0, "Linux": 0.9,
        },
        "nice_to_have": [
            "Azure", "Google Cloud", "Ansible", "Helm", "CI/CD",
            "Prometheus", "Grafana", "Python", "Bash", "IAM",
        ],
        "salary_range": "$105,000 – $175,000 / yr",
        "growth": "High",
    },
    "DevOps Engineer": {
        "icon": "",
        "description": (
            "Bridge development and operations by automating pipelines, "
            "managing infrastructure, and ensuring system reliability."
        ),
        "required": {
            "CI/CD": 1.0, "Docker": 1.0, "Kubernetes": 1.0,
            "Git": 1.0, "Linux": 0.9,
        },
        "nice_to_have": [
            "Terraform", "Ansible", "AWS", "Prometheus", "Grafana",
            "GitHub Actions", "Jenkins", "Python", "Helm", "ArgoCD",
        ],
        "salary_range": "$100,000 – $165,000 / yr",
        "growth": "High",
    },
}

_NICE_WEIGHT = 0.4


@dataclass
class JobMatch:
    title:          str
    icon:           str
    confidence:     float
    description:    str
    salary_range:   str
    growth:         str
    matched:        list[str] = field(default_factory=list)
    missing:        list[str] = field(default_factory=list)
    nice_matched:   list[str] = field(default_factory=list)

    @property
    def confidence_label(self) -> str:
        if self.confidence >= 80:
            return "Excellent Match"
        if self.confidence >= 60:
            return "Strong Match"
        if self.confidence >= 40:
            return "Good Match"
        if self.confidence >= 20:
            return "Partial Match"
        return "Low Match"

    @property
    def confidence_color(self) -> str:
        if self.confidence >= 80:
            return "#2A9D8F"
        if self.confidence >= 60:
            return "#3D7EA6"
        if self.confidence >= 40:
            return "#E9C46A"
        return "#E76F51"


class JobRecommender:
    def recommend(self, candidate_skills: list[str]) -> list[JobMatch]:
        candidate_set = {s.lower() for s in candidate_skills}
        results: list[JobMatch] = []

        for title, profile in JOB_PROFILES.items():
            required:     dict[str, float] = profile["required"]
            nice_to_have: list[str]        = profile["nice_to_have"]

            matched:  list[str] = []
            missing:  list[str] = []
            matched_w  = 0.0
            required_w = sum(required.values())

            for skill, weight in required.items():
                if skill.lower() in candidate_set:
                    matched.append(skill)
                    matched_w += weight
                else:
                    missing.append(skill)

            nice_matched: list[str] = []
            nice_w = 0.0
            for skill in nice_to_have:
                if skill.lower() in candidate_set:
                    nice_matched.append(skill)
                    nice_w += _NICE_WEIGHT

            unmatched_nice_w = (len(nice_to_have) - len(nice_matched)) * _NICE_WEIGHT
            numerator   = matched_w + nice_w
            denominator = required_w + unmatched_nice_w + nice_w

            raw_score  = (numerator / denominator * 100) if denominator > 0 else 0.0
            confidence = round(min(max(raw_score, 0.0), 100.0), 1)

            results.append(
                JobMatch(
                    title        = title,
                    icon         = profile["icon"],
                    confidence   = confidence,
                    description  = profile["description"],
                    salary_range = profile["salary_range"],
                    growth       = profile["growth"],
                    matched      = matched,
                    missing      = missing,
                    nice_matched = nice_matched,
                )
            )

        results.sort(key=lambda m: m.confidence, reverse=True)
        return results

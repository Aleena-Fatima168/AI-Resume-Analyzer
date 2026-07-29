"""Skill extraction, normalisation, and categorisation.

Architecture
------------
SKILL_TAXONOMY   : canonical display names grouped by category (~550+ skills).
_AliasIndex      : module-level singleton — builds token/phrase lookup maps once.
SkillExtractor   : public API — extract, normalise, categorise, or do all at once.

Matching strategy
-----------------
1. Text is lowercased and tokenised (spaCy when available, regex fallback).
2. Greedy left-to-right scan tries the longest known phrase first, then
   single tokens, so "machine learning" is captured as one skill rather
   than two separate tokens.
3. Results are deduplicated while preserving first-appearance order.
4. Canonical display names (correct casing, e.g. "PyTorch") are returned.
"""

from __future__ import annotations

import re
from typing import Iterator

# ---------------------------------------------------------------------------
# Skill taxonomy  (category → list of canonical display names)
# ---------------------------------------------------------------------------

SKILL_TAXONOMY: dict[str, list[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
        "Perl", "Haskell", "Elixir", "Erlang", "Clojure", "F#", "Dart",
        "Lua", "Julia", "Groovy", "Objective-C", "Assembly", "COBOL",
        "Fortran", "VHDL", "Verilog", "Bash", "PowerShell", "Shell",
        "Awk", "Sed", "Tcl", "Prolog", "Lisp", "Scheme", "OCaml",
        "Crystal", "Nim", "Zig", "V", "Solidity", "Move",
    ],
    "Frontend": [
        "React", "Next.js", "Vue.js", "Nuxt.js", "Angular", "Svelte",
        "SvelteKit", "Ember.js", "Backbone.js", "jQuery", "Alpine.js",
        "Lit", "Stencil", "Qwik", "Astro", "Remix", "Gatsby",
        "HTML", "HTML5", "CSS", "CSS3", "Sass", "SCSS", "Less",
        "Tailwind CSS", "Bootstrap", "Material UI", "Chakra UI",
        "Ant Design", "Styled Components", "Emotion", "Radix UI",
        "shadcn/ui", "Headless UI", "Framer Motion", "GSAP",
        "Three.js", "D3.js", "Chart.js", "Recharts", "Highcharts",
        "Webpack", "Vite", "Parcel", "Rollup", "esbuild", "Turbopack",
        "Babel", "ESLint", "Prettier", "Storybook", "Figma",
        "WebAssembly", "PWA", "Web Components", "GraphQL Client",
        "Apollo Client", "React Query", "SWR", "Zustand", "Redux",
        "MobX", "Recoil", "Jotai", "XState",
    ],
    "Backend": [
        "Node.js", "Express.js", "Fastify", "NestJS", "Koa", "Hapi",
        "Django", "Flask", "FastAPI", "Tornado", "Starlette", "Sanic",
        "Spring Boot", "Spring Framework", "Spring MVC", "Micronaut",
        "Quarkus", "Vert.x", "Ruby on Rails", "Sinatra", "Hanami",
        "Laravel", "Symfony", "CodeIgniter", "Lumen", "Slim",
        "ASP.NET Core", "ASP.NET", ".NET", ".NET Core", "Blazor",
        "Gin", "Echo", "Fiber", "Chi", "Actix", "Axum", "Rocket",
        "Phoenix", "Plug", "Ktor", "Helidon",
        "GraphQL", "REST API", "gRPC", "WebSocket", "SOAP",
        "OAuth2", "JWT", "OpenID Connect", "CORS", "Nginx",
        "Apache HTTP Server", "Caddy", "Traefik", "HAProxy",
        "Celery", "RQ", "Sidekiq", "Bull", "Temporal",
        "Kafka", "RabbitMQ", "NATS", "ActiveMQ", "ZeroMQ",
        "Redis", "Memcached", "Elasticsearch", "OpenSearch",
        "Solr", "Meilisearch", "Typesense",
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MariaDB", "SQLite", "Oracle Database",
        "Microsoft SQL Server", "IBM Db2", "CockroachDB", "YugabyteDB",
        "TiDB", "PlanetScale", "Neon", "Supabase",
        "MongoDB", "CouchDB", "RavenDB", "Amazon DocumentDB",
        "Cassandra", "ScyllaDB", "HBase", "DynamoDB",
        "Redis", "KeyDB", "Dragonfly",
        "Neo4j", "Amazon Neptune", "ArangoDB", "JanusGraph",
        "InfluxDB", "TimescaleDB", "QuestDB", "Prometheus",
        "Snowflake", "BigQuery", "Redshift", "Databricks",
        "ClickHouse", "Apache Druid", "Apache Pinot", "Firebolt",
        "Dbt", "Airbyte", "Fivetran", "Stitch",
        "SQL", "NoSQL", "PL/SQL", "T-SQL", "JPQL", "HQL",
        "SQLAlchemy", "Prisma", "TypeORM", "Sequelize", "Hibernate",
        "Mongoose", "Drizzle ORM",
    ],
    "Cloud & Infrastructure": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure",
        "Google Cloud", "GCP", "Google Cloud Platform",
        "IBM Cloud", "Oracle Cloud", "Alibaba Cloud",
        "DigitalOcean", "Linode", "Vultr", "Hetzner",
        "EC2", "S3", "Lambda", "ECS", "EKS", "Fargate",
        "RDS", "Aurora", "CloudFront", "Route 53", "VPC",
        "IAM", "CloudFormation", "CDK", "SAM",
        "Azure Functions", "Azure DevOps", "Azure Kubernetes Service",
        "Azure Blob Storage", "Azure Active Directory",
        "Cloud Run", "Cloud Functions", "GKE", "Firebase",
        "Terraform", "Pulumi", "Ansible", "Chef", "Puppet",
        "Packer", "Vagrant", "CloudInit",
        "Docker", "Kubernetes", "Helm", "Kustomize",
        "Istio", "Linkerd", "Envoy", "Consul",
        "Prometheus", "Grafana", "Loki", "Tempo", "Jaeger",
        "Datadog", "New Relic", "Dynatrace", "Splunk",
        "PagerDuty", "OpsGenie", "VictorOps",
        "Serverless Framework", "OpenTofu", "Crossplane",
    ],
    "AI & Machine Learning": [
        "Machine Learning", "Deep Learning", "Neural Networks",
        "Natural Language Processing", "NLP", "Computer Vision",
        "Reinforcement Learning", "Transfer Learning",
        "Supervised Learning", "Unsupervised Learning",
        "Semi-supervised Learning", "Self-supervised Learning",
        "Generative AI", "Large Language Models", "LLM",
        "Prompt Engineering", "RAG", "Retrieval-Augmented Generation",
        "Fine-tuning", "RLHF",
        "TensorFlow", "PyTorch", "Keras", "JAX", "Flax",
        "scikit-learn", "XGBoost", "LightGBM", "CatBoost",
        "Hugging Face", "Transformers", "Diffusers", "PEFT",
        "LangChain", "LlamaIndex", "Haystack", "Semantic Kernel",
        "OpenAI API", "Anthropic API", "Cohere", "Mistral",
        "spaCy", "NLTK", "Gensim", "FastText", "Word2Vec",
        "BERT", "GPT", "T5", "LLaMA", "Falcon",
        "Stable Diffusion", "DALL-E", "Midjourney",
        "MLflow", "Weights & Biases", "Neptune.ai", "Comet ML",
        "DVC", "ClearML", "Kubeflow", "Metaflow",
        "ONNX", "TensorRT", "OpenVINO", "CoreML", "TFLite",
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
        "Plotly", "Bokeh", "Altair",
        "Feature Engineering", "Model Deployment", "Model Monitoring",
        "A/B Testing", "Bayesian Optimization", "AutoML",
        "Federated Learning", "Edge AI",
    ],
    "DevOps & CI/CD": [
        "DevOps", "GitOps", "MLOps", "DataOps", "FinOps", "SRE",
        "CI/CD", "Continuous Integration", "Continuous Deployment",
        "Continuous Delivery",
        "GitHub Actions", "GitLab CI", "Jenkins", "CircleCI",
        "Travis CI", "Bamboo", "TeamCity", "Buildkite",
        "ArgoCD", "Flux", "Spinnaker", "Harness",
        "Git", "GitHub", "GitLab", "Bitbucket", "Azure Repos",
        "Docker", "Docker Compose", "Podman", "Buildah",
        "Kubernetes", "OpenShift", "Rancher", "k3s", "k0s",
        "Helm", "Kustomize", "Skaffold", "Tilt",
        "Terraform", "Ansible", "Pulumi", "Chef", "Puppet",
        "Prometheus", "Grafana", "ELK Stack", "Elasticsearch",
        "Logstash", "Kibana", "Fluentd", "Fluent Bit",
        "SonarQube", "Snyk", "Trivy", "Checkov", "tfsec",
        "Nexus", "JFrog Artifactory", "Harbor",
        "Linux", "Ubuntu", "CentOS", "RHEL", "Debian", "Alpine",
        "Bash Scripting", "Python Scripting",
        "Load Testing", "Chaos Engineering", "Incident Management",
    ],
    "Automation & Testing": [
        "Selenium", "Playwright", "Cypress", "Puppeteer",
        "WebdriverIO", "Nightwatch.js", "TestCafe",
        "Appium", "Detox", "Espresso", "XCUITest",
        "Jest", "Vitest", "Mocha", "Jasmine", "Karma",
        "pytest", "unittest", "nose2", "hypothesis",
        "JUnit", "TestNG", "Mockito", "AssertJ",
        "NUnit", "xUnit", "MSTest", "SpecFlow",
        "RSpec", "Capybara", "Minitest",
        "Postman", "Insomnia", "REST Assured", "Karate",
        "k6", "Locust", "Gatling", "JMeter", "Artillery",
        "Robot Framework", "Behave", "Cucumber",
        "Allure", "ReportPortal", "TestRail",
        "Stubs", "Mocks", "Test Doubles", "TDD", "BDD",
        "Contract Testing", "Pact", "WireMock",
        "Static Analysis", "SAST", "DAST",
        "UiPath", "Blue Prism", "Automation Anywhere",
        "Power Automate", "Zapier", "Make", "n8n",
        "Apache Airflow", "Prefect", "Dagster", "Luigi",
    ],
    "Cybersecurity": [
        "Cybersecurity", "Information Security", "Network Security",
        "Application Security", "Cloud Security", "Zero Trust",
        "Penetration Testing", "Ethical Hacking", "Red Team",
        "Blue Team", "Purple Team", "Threat Modeling",
        "OWASP", "CVE", "CWE", "CVSS",
        "SIEM", "SOC", "Incident Response", "Forensics",
        "Splunk", "IBM QRadar", "Microsoft Sentinel",
        "Nmap", "Metasploit", "Burp Suite", "Wireshark",
        "Nessus", "OpenVAS", "Qualys", "Rapid7",
        "Kali Linux", "Parrot OS", "BlackArch",
        "Firewalls", "IDS", "IPS", "WAF", "DLP",
        "PKI", "TLS", "SSL", "mTLS", "Certificate Management",
        "LDAP", "Active Directory", "SAML", "OAuth2",
        "MFA", "SSO", "PAM", "IAM",
        "GDPR", "HIPAA", "SOC 2", "ISO 27001", "PCI DSS",
        "NIST", "CIS Benchmarks", "MITRE ATT&CK",
        "Cryptography", "AES", "RSA", "ECC", "Hashing",
        "Vulnerability Assessment", "Risk Assessment",
        "Security Auditing", "Compliance", "GRC",
        "HashiCorp Vault", "AWS Secrets Manager", "CyberArk",
        "Snyk", "Checkmarx", "Veracode", "SonarQube",
    ],
    "Data Engineering": [
        "Apache Spark", "Apache Kafka", "Apache Flink",
        "Apache Hadoop", "Apache Hive", "Apache Pig",
        "Apache Beam", "Apache NiFi", "Apache Airflow",
        "Databricks", "Delta Lake", "Apache Iceberg", "Apache Hudi",
        "dbt", "Great Expectations", "Soda", "Monte Carlo",
        "Snowflake", "BigQuery", "Redshift", "Synapse Analytics",
        "Fivetran", "Airbyte", "Stitch", "Talend", "Informatica",
        "Kafka Streams", "KSQL", "Confluent",
        "Pandas", "Polars", "Dask", "Vaex", "Modin",
        "PySpark", "Spark SQL", "Spark Streaming",
        "ETL", "ELT", "Data Pipeline", "Data Warehouse",
        "Data Lake", "Data Lakehouse", "Data Mesh",
        "Data Modeling", "Data Governance", "Data Quality",
        "Data Catalog", "Apache Atlas", "DataHub", "Amundsen",
        "Parquet", "Avro", "ORC", "JSON", "CSV",
        "Protobuf", "Thrift", "MessagePack",
        "Stream Processing", "Batch Processing", "Real-time Analytics",
        "Change Data Capture", "CDC", "Debezium",
    ],
}

# ---------------------------------------------------------------------------
# Alias map  (common alternate spellings → canonical name)
# ---------------------------------------------------------------------------

_ALIASES: dict[str, str] = {
    # Languages
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "golang": "Go",
    "c plus plus": "C++",
    "cplusplus": "C++",
    "csharp": "C#",
    "c sharp": "C#",
    "objective c": "Objective-C",
    # Frontend
    "reactjs": "React",
    "react.js": "React",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "angularjs": "Angular",
    "nextjs": "Next.js",
    "nuxtjs": "Nuxt.js",
    "sveltejs": "Svelte",
    "tailwind": "Tailwind CSS",
    "materialui": "Material UI",
    "mui": "Material UI",
    "styledcomponents": "Styled Components",
    "d3": "D3.js",
    "threejs": "Three.js",
    # Backend
    "nodejs": "Node.js",
    "node": "Node.js",
    "expressjs": "Express.js",
    "express": "Express.js",
    "nestjs": "NestJS",
    "fastapi": "FastAPI",
    "springboot": "Spring Boot",
    "rails": "Ruby on Rails",
    "ror": "Ruby on Rails",
    "dotnet": ".NET",
    "asp.net": "ASP.NET Core",
    "aspnet": "ASP.NET Core",
    # Databases
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "mssql": "Microsoft SQL Server",
    "sqlserver": "Microsoft SQL Server",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "dynamo": "DynamoDB",
    "dynamodb": "DynamoDB",
    "elastic": "Elasticsearch",
    "es": "Elasticsearch",
    # Cloud
    "amazon web services": "AWS",
    "microsoft azure": "Azure",
    "google cloud platform": "Google Cloud",
    "gcp": "Google Cloud",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    # AI / ML
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "nlp": "Natural Language Processing",
    "llms": "Large Language Models",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "hf": "Hugging Face",
    "huggingface": "Hugging Face",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "openai": "OpenAI API",
    "wb": "Weights & Biases",
    "wandb": "Weights & Biases",
    # DevOps
    "gh actions": "GitHub Actions",
    "gitlab ci/cd": "GitLab CI",
    "gitlab cicd": "GitLab CI",
    "ci cd": "CI/CD",
    "cicd": "CI/CD",
    "argocd": "ArgoCD",
    "elk": "ELK Stack",
    # Security
    "infosec": "Information Security",
    "appsec": "Application Security",
    "pentest": "Penetration Testing",
    "pen testing": "Penetration Testing",
    "burpsuite": "Burp Suite",
    "mitre attack": "MITRE ATT&CK",
    "soc2": "SOC 2",
    "iso27001": "ISO 27001",
    "pci-dss": "PCI DSS",
    # Data Engineering
    "pyspark": "PySpark",
    "spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "flink": "Apache Flink",
    "hadoop": "Apache Hadoop",
    "hive": "Apache Hive",
    "airflow": "Apache Airflow",
    "dbt": "dbt",
    "delta": "Delta Lake",
}


# ---------------------------------------------------------------------------
# Internal alias index (built once at module load)
# ---------------------------------------------------------------------------

class _AliasIndex:
    """
    Flat lookup structures built from SKILL_TAXONOMY + _ALIASES.

    Attributes
    ----------
    canonical_set   : set of all canonical names (lowercase) for fast membership.
    phrase_map      : lowercase multi-word phrase → canonical name,
                      sorted longest-first for greedy matching.
    token_map       : lowercase single token → canonical name.
    reverse_map     : lowercase canonical name → category label.
    """

    def __init__(self) -> None:
        self.phrase_map: list[tuple[str, str]] = []   # (phrase, canonical)
        self.token_map:  dict[str, str]         = {}  # token  → canonical
        self.reverse_map: dict[str, str]        = {}  # lower(canonical) → category

        for category, skills in SKILL_TAXONOMY.items():
            for canonical in skills:
                lower = canonical.lower()
                self.reverse_map[lower] = category
                if " " in lower or "." in lower or "/" in lower:
                    self.phrase_map.append((lower, canonical))
                else:
                    self.token_map[lower] = canonical

        # Aliases
        for alias, canonical in _ALIASES.items():
            lower_alias = alias.lower()
            lower_canon = canonical.lower()
            # Ensure canonical is registered in reverse_map (may already be)
            if lower_canon not in self.reverse_map:
                # Find category by scanning taxonomy
                for category, skills in SKILL_TAXONOMY.items():
                    if canonical in skills:
                        self.reverse_map[lower_canon] = category
                        break
            if " " in lower_alias:
                self.phrase_map.append((lower_alias, canonical))
            else:
                self.token_map[lower_alias] = canonical

        # Sort phrases longest-first so greedy scan captures "machine learning"
        # before "machine" or "learning" individually.
        self.phrase_map.sort(key=lambda t: len(t[0]), reverse=True)

    def category_of(self, canonical: str) -> str | None:
        return self.reverse_map.get(canonical.lower())


_INDEX = _AliasIndex()


# ---------------------------------------------------------------------------
# Tokeniser (spaCy when available, regex fallback)
# ---------------------------------------------------------------------------

# Module-level blank spaCy pipeline — created once, reused on every call.
# Falls back to None if spaCy is not installed.
try:
    import spacy as _spacy
    _BLANK_NLP = _spacy.blank("en")
except Exception:
    _BLANK_NLP = None  # type: ignore[assignment]


def _tokenize(text: str) -> list[str]:
    """
    Return a list of lowercase tokens preserving punctuation-joined terms
    like "c++", "node.js", "ci/cd".

    Uses the module-level blank spaCy pipeline when available; falls back
    to a regex split that handles the same edge cases.
    """
    if _BLANK_NLP is not None:
        return [tok.text.lower() for tok in _BLANK_NLP(text) if tok.text.strip()]
    # Keep tokens like "c++", "node.js", "ci/cd", ".net"
    return re.findall(r"[\w][\w.+#/\-]*|[.#][\w]+", text.lower())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class SkillExtractor:
    """
    Extract, normalise, and categorise skills from free-form resume text.

    All methods are stateless and safe to call from multiple threads.

    Examples
    --------
    >>> se = SkillExtractor()
    >>> skills = se.extract_skills("Built REST APIs with FastAPI and PostgreSQL.")
    >>> se.categorize_skills(skills)
    {'Backend': ['FastAPI'], 'Databases': ['PostgreSQL']}
    """

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract_skills(self, text: str) -> list[str]:
        """
        Detect all skill mentions in *text* and return canonical display names.

        Strategy
        --------
        1. Tokenise the lowercased text.
        2. Greedy left-to-right scan: try every known phrase starting at the
           current position (longest first), then fall back to single-token
           lookup.
        3. Deduplicate while preserving first-appearance order.

        Args:
            text: Plain-text resume or job-description content.

        Returns:
            Ordered, deduplicated list of canonical skill names.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a str.")
        if not text.strip():
            return []

        tokens = _tokenize(text)
        found: list[str] = []
        seen: set[str]   = set()
        i = 0

        while i < len(tokens):
            matched = False

            # Try multi-word phrases first (already sorted longest-first)
            for phrase, canonical in _INDEX.phrase_map:
                phrase_tokens = phrase.split()
                n = len(phrase_tokens)
                window = " ".join(tokens[i : i + n])
                if window == phrase:
                    key = canonical.lower()
                    if key not in seen:
                        seen.add(key)
                        found.append(canonical)
                    i += n
                    matched = True
                    break

            if not matched:
                token = tokens[i]
                canonical = _INDEX.token_map.get(token)
                if canonical:
                    key = canonical.lower()
                    if key not in seen:
                        seen.add(key)
                        found.append(canonical)
                i += 1

        return found

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def normalize_skills(self, skills: list[str]) -> list[str]:
        """
        Map raw skill strings (aliases, wrong casing) to canonical names.

        Unknown strings are passed through unchanged so no data is silently
        dropped.

        Args:
            skills: Raw skill labels from any source.

        Returns:
            List of canonical names, order preserved, duplicates removed.
        """
        if not isinstance(skills, list):
            raise TypeError("skills must be a list.")

        seen: set[str] = set()
        result: list[str] = []
        for raw in skills:
            lower = raw.strip().lower()
            # Check alias map first, then token map, then phrase map
            canonical = (
                _ALIASES.get(lower)
                or _INDEX.token_map.get(lower)
                or next((c for p, c in _INDEX.phrase_map if p == lower), None)
                or raw.strip()          # unknown — pass through as-is
            )
            key = canonical.lower()
            if key not in seen:
                seen.add(key)
                result.append(canonical)
        return result

    # ------------------------------------------------------------------
    # Categorisation
    # ------------------------------------------------------------------

    def categorize_skills(self, skills: list[str]) -> dict[str, list[str]]:
        """
        Group *skills* into taxonomy categories.

        Args:
            skills: Canonical skill names (output of :meth:`extract_skills`
                    or :meth:`normalize_skills`).

        Returns:
            ``{category: [skill, ...]}`` — only categories with ≥1 match are
            included; order within each list mirrors *skills* input order.
        """
        if not isinstance(skills, list):
            raise TypeError("skills must be a list.")

        result: dict[str, list[str]] = {}
        for skill in skills:
            category = _INDEX.category_of(skill) or "Other"
            result.setdefault(category, []).append(skill)
        return result

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def extract_and_categorize(self, text: str) -> dict[str, list[str]]:
        """
        Extract skills from *text* and return them already categorised.

        Equivalent to ``categorize_skills(extract_skills(text))``.

        Args:
            text: Plain-text resume or job-description content.

        Returns:
            ``{category: [skill, ...]}`` mapping.
        """
        return self.categorize_skills(self.extract_skills(text))

    def all_categories(self) -> list[str]:
        """Return the ordered list of taxonomy category names."""
        return list(SKILL_TAXONOMY.keys())

    def skill_count(self) -> int:
        """Return total number of canonical skills in the taxonomy."""
        return sum(len(v) for v in SKILL_TAXONOMY.values())

    # ------------------------------------------------------------------
    # Iterator helpers
    # ------------------------------------------------------------------

    def iter_taxonomy(self) -> Iterator[tuple[str, str]]:
        """Yield ``(category, canonical_name)`` for every skill in the taxonomy."""
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                yield category, skill

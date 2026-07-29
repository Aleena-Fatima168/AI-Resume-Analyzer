# AI Resume Analyzer

A Python-based web application that analyzes resumes using Natural Language Processing (NLP). The application extracts important information, evaluates ATS compatibility, identifies technical skills, analyzes skill gaps, and recommends suitable job roles through an interactive dashboard.


Features:

- Upload resumes in PDF, DOCX, and TXT formats
- Extract personal information (Name, Email, Phone Number)
- Detect technical skills using NLP
- Calculate ATS compatibility score
- Analyze resume quality and completeness
- Identify missing skills for selected job roles
- Recommend suitable job positions
- Interactive dashboard with charts and analytics
- Store resume analysis history using SQLite
- Generate downloadable PDF reports

Technologies Used:

- Python
- Streamlit
- spaCy
- Scikit-learn
- Pandas
- NumPy
- Plotly
- SQLite
- pdfplumber
- PyPDF2
- python-docx
- FPDF2

Project Structure:

text
AI-Resume-Analyzer/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── pages/
│   ├── Dashboard.py
│   ├── Resume_Analysis.py
│   ├── Skill_Gap.py
│   ├── Job_Recommendation.py
│   └── About.py
│
├── utils/
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── score_calculator.py
│   ├── recommendation.py
│   ├── visualization.py
│   ├── database.py
│   ├── text_processing.py
│   └── styles.py
│
├── assets/
├── data/
├── models/
├── sample_resumes/
└── tests/

Installation:

Clone the repository:

```bash
git clone https:https://github.com/Aleena-Fatima168/AI-Resume-Analyzer
```

Navigate to the project directory:

```bash
cd AI-Resume-Analyzer
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Download the spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

Run the application:

```bash
streamlit run app.py
```

Open your browser and visit:

```text
http://localhost:8501
```
Usage:

1. Launch the application.
2. Upload a resume in PDF, DOCX, or TXT format.
3. Review the extracted information.
4. View the ATS score and resume analysis.
5. Analyze skill gaps for different job roles.
6. Explore recommended job positions.
7. View analytics and charts from the dashboard.

Future Improvements:

- AI-powered cover letter generation
- Resume and Job Description matching
- AI interview question generator
- Multi-language resume support
- User authentication
- Cloud deployment
- Docker support
- REST API integration

License:

This project is licensed under the MIT License.

Author:

Aleena Fatima

Bachelor of Computer Science (BSCS)

Government College University Faisalabad

GitHub: https://github.com/Aleena-Fatima168

LinkedIn: https://www.linkedin.com/in/aleena-fatima-dev

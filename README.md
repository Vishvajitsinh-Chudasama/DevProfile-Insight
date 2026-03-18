# DevProfile Insight

DevProfile Insight is a **Django web app** that evaluates how well a candidate’s **resume** and **GitHub profile** match a target **job role**.

At a high level, the app:

- Extracts text from an uploaded **PDF/DOCX** resume
- Pulls **GitHub profile + repositories + contribution activity** using the GitHub REST + GraphQL APIs
- Uses **DSPy** + a **Mistral** LLM (via `MISTRAL_API_KEY`) with **FAISS retrieval** (LangChain) to generate:
  - a **role fit score** (0–100)
  - **strengths**, **weaknesses**, and **recommendations**
- Stores results in the database and displays them on the **Personal Dashboard**

---

## Features

- **Personal + company sign-up flows** (custom user model with a `role`)
- **Resume upload** from the dashboard (PDF/DOCX)
- **GitHub analysis**
  - user metadata (followers, repos, etc.)
  - repo language breakdown (percentages per language)
  - contribution calendar via GitHub GraphQL
  - a computed GitHub “activity score”
- **AI evaluation**
  - Retrieval step backed by FAISS + `sentence-transformers` embeddings
  - DSPy module that generates fit score and feedback
- **Stored results** (`ProfileAnalysis`) shown in `dashboard/templates/personal_dashboard.html`

---

## Tech stack

- **Backend**: Django 5 (Python)
- **Database**: SQLite (default)
- **Frontend**: Django templates + CSS/JS in each app’s `static/`
- **AI/ML**:
  - LangChain vector store: `langchain-community` + **FAISS**
  - Embeddings: `sentence-transformers` (`all-MiniLM-L6-v2`)
  - LLM orchestration/evaluation: **DSPy**
  - LLM provider: **Mistral** (configured in `dashboard/utils/evaluator.py`)
- **GitHub integration**:
  - REST API for users/repos/readmes
  - GraphQL API for contribution calendar

---

## Live routes (current code)

These routes are present in the current project URLs:

- **Landing page**: `GET /`
- **Features page**: `GET /Features/`
- **Sign up chooser**: `GET /authentication/`
- **Login**: `GET|POST /authentication/login/`
- **Personal dashboard (resume upload + results)**: `GET|POST /dashboard/personal/` (requires login)

Notes:

- The “company” signup flow exists, but a **company dashboard route is not implemented** in the current code (login redirects to `company_dashboard`, which is not defined).

---

## Project structure

```text
DevProfile-Insight/
├─ DevProfile-Insight/                # Django project (settings/urls/asgi/wsgi)
├─ accounts/                          # CustomUser + signup/login views
├─ dashboard/                         # Personal dashboard + ProfileAnalysis model
│  ├─ utils/
│  │  ├─ evaluator.py                 # GitHub fetch + FAISS/DSPy evaluation
│  │  └─ text_extractor.py            # PDF/DOCX text extraction
│  ├─ templates/personal_dashboard.html
│  └─ static/css/personal_dashboard.css
├─ home/                              # Landing + Features pages
├─ media/                             # Uploaded files (created at runtime)
├─ db.sqlite3                         # Default DB (created at runtime)
├─ manage.py
├─ requirements.txt
└─ README.md
```

---

## Prerequisites

- **Python**: 3.10+ recommended
- **pip** (or `pipx`/venv tooling)
- **GitHub token**: required (see Environment variables)
- **Mistral API key**: required (see Environment variables)

Optional but recommended:

- A GPU is **not required**, but the first run may take time because dependencies like `torch` and `transformers` are large.

---

## Setup (local development)

### 1) Clone the repo

```bash
git clone <your-repo-url>
cd DevProfile-Insight
```

### 2) Create and activate a virtual environment

```bash
python -m venv env
source env/bin/activate
```

On Windows (PowerShell):

```bash
python -m venv env
.\env\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create a `.env` file (required)

This project loads environment variables from a `.env` file in the repo root (see `DevProfile-Insight/settings.py`).

Create a file named `.env` in the project root:

```bash
cat > .env <<'EOF'
# Required: GitHub API token (classic PAT works)
GITHUB_TOKEN=ghp_your_token_here

# Required: Mistral API key (used by DSPy)
MISTRAL_API_KEY=your_mistral_api_key_here
EOF
```

### 5) Provide `ResumeDataSet.csv` (required by current evaluator code)

`dashboard/utils/evaluator.py` currently expects this file to exist:

- `dashboard/utils/ResumeDataSet.csv`

If it is missing, Django will raise an error at import time (before pages load).

**Expected columns** (minimum):

- `Resume`: text content for retrieval documents
- `Category`: label/category for metadata

Create it at `dashboard/utils/ResumeDataSet.csv`, for example:

```csv
Resume,Category
"Experienced Python developer with Django and REST APIs.","Software Engineer"
"Skilled in SQL, analytics, and dashboards using pandas.","Data Analyst"
```

### 6) Run migrations

```bash
python manage.py migrate
```

### 7) Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 8) Start the server

```bash
python manage.py runserver
```

Then open:

- Home: `http://127.0.0.1:8000/`
- Signup: `http://127.0.0.1:8000/authentication/`
- Personal dashboard: `http://127.0.0.1:8000/dashboard/personal/`

---

## How to use (app flow)

### Create an account

1. Go to `authentication/`
2. Choose **Personal** (recommended — it’s the only dashboard implemented)
3. Sign up, then log in at `authentication/login/`

### Run an evaluation

1. Navigate to `dashboard/personal/`
2. Fill out:
   - **Resume** (PDF/DOCX)
   - **Target Job Role** (free text)
   - **GitHub Username**
3. Submit the form

The app will:

- Save your resume under `media/resumes/`
- Extract plain text from it
- Fetch GitHub details and contributions
- Generate a fit score + feedback
- Store the results in the `ProfileAnalysis` table and display them on the page

---

## Environment variables

These variables are required at runtime:

- **`GITHUB_TOKEN`**: GitHub token used for REST + GraphQL calls
- **`MISTRAL_API_KEY`**: Mistral API key used by DSPy (`mistral/mistral-tiny`)

Where they’re used:

- GitHub calls: `dashboard/utils/evaluator.py`
- LLM/DSPy config: `dashboard/utils/evaluator.py`

---

## Data & storage

- **Database**: SQLite at `db.sqlite3` (default Django config)
- **Uploads**:
  - `MEDIA_ROOT` is set to `media/`
  - The personal dashboard view writes resumes to `media/resumes/`

If you get a file write error on upload, ensure this folder exists:

```bash
mkdir -p media/resumes
```

---

## Troubleshooting

### `ValueError: GITHUB_TOKEN not set in environment`

- Add `GITHUB_TOKEN` to your `.env` and restart the server.

### `ValueError: MISTRAL_API_KEY not set in environment`

- Add `MISTRAL_API_KEY` to your `.env` and restart the server.

### `FileNotFoundError: ResumeDataSet.csv not found in utils folder`

- Create `dashboard/utils/ResumeDataSet.csv` with at least `Resume` and `Category` columns.

### Slow first run / large downloads

- The project depends on ML libraries (e.g. `torch`, `transformers`, `sentence-transformers`). Initial installs can be large and take time.

---

## Development notes (current implementation)

- `accounts.CustomUser` is the active user model (`AUTH_USER_MODEL` is set in settings).
- The current dashboard is **personal only** (`dashboard/urls.py` exposes `/dashboard/personal/`).
- The evaluator initializes FAISS + embeddings at import time; ensure required files/env vars exist before starting Django.

---

## License

Add your license here (e.g. MIT) if you plan to publish this project.

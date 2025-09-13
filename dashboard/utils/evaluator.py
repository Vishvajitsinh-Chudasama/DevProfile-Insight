"""
insight/utils/evaluator.py

Reusable GitHub + Resume + DSPy evaluator.

Call:
    from .evaluator import run_full_evaluation
    result = run_full_evaluation(resume_text, "github-username", "Data Scientist")
"""

import os
import base64
import requests
import pandas as pd
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import dspy
from dspy.teleprompt import BootstrapFewShot


# ---------------------------------------------------------------------------
# 🔑 Environment
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

if not GITHUB_TOKEN:
    raise ValueError("❌ GITHUB_TOKEN not set in environment")
if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY not set in environment")

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------
def fetch_github_user(username: str):
    url = f"https://api.github.com/users/{username}"
    resp = requests.get(url, headers=HEADERS).json()
    return {
        "name": resp.get("name"),
        "bio": resp.get("bio"),
        "company": resp.get("company"),
        "location": resp.get("location"),
        "followers": resp.get("followers", 0),
        "following": resp.get("following", 0),
        "public_repos": resp.get("public_repos", 0),
        "created_at": resp.get("created_at"),
        "updated_at": resp.get("updated_at"),
    }


def fetch_all_repos(username: str):
    """All repos with language percentages and optional README text."""
    repos, page = [], 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS).json()
        if not r or "message" in r:
            break
        for repo in r:
            repo_name = repo["name"]
            langs = requests.get(repo["languages_url"], headers=HEADERS).json()
            total = sum(langs.values())
            languages = (
                {lang: f"{(size / total) * 100:.2f}%" for lang, size in langs.items()}
                if total
                else {}
            )
            readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
            readme_resp = requests.get(readme_url, headers=HEADERS)
            readme_content = None
            if readme_resp.status_code == 200:
                content = readme_resp.json().get("content", "")
                readme_content = base64.b64decode(content).decode("utf-8", errors="ignore")
            repos.append(
                {
                    "repo": repo_name,
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "updated_at": repo.get("updated_at"),
                    "languages": languages,
                    "readme": readme_content,
                }
            )
        page += 1
    return repos


def fetch_github_contributions(username: str):
    """Daily contribution counts using GitHub GraphQL API."""
    url = "https://api.github.com/graphql"
    query = """
    query($login: String!) {
        user(login: $login) {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                        }
                    }
                }
            }
        }
    }
    """
    resp = requests.post(url, headers=HEADERS,
                         json={"query": query, "variables": {"login": username}}).json()
    if "errors" in resp or "data" not in resp or resp["data"]["user"] is None:
        return []
    weeks = resp["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    out = []
    for w in weeks:
        for d in w["contributionDays"]:
            out.append({"date": d["date"], "count": d["contributionCount"]})
    return out


def evaluate_github(username: str):
    """Compute basic GitHub score and summary info."""
    user_data = fetch_github_user(username)
    repos = fetch_all_repos(username)
    contributions = fetch_github_contributions(username)
    total_contributions = sum(day["count"] for day in contributions)
    active_days = sum(1 for day in contributions if day["count"] > 0)
    consistency = (active_days / len(contributions) * 100) if contributions else 0
    score = min(100,
                (user_data.get("public_repos", 0) * 2 + total_contributions / 10 + consistency))
    pros = [
        f"Public repos: {user_data.get('public_repos')}",
        f"Total contributions: {total_contributions}",
        f"Contribution consistency: {consistency:.2f}%",
    ]
    cons = []
    if user_data.get("public_repos", 0) < 5:
        cons.append("Few public repositories")
    if consistency < 50:
        cons.append("Low GitHub activity consistency")
    return {
        "user_data": user_data,
        "repos": repos,
        "contributions": contributions,
        "score": round(score, 2),
        "pros": pros,
        "cons": cons,
    }


def summarize_github_for_eval(username: str) -> str:
    result = evaluate_github(username)
    summary = f"""
User: {result['user_data']['name']} ({username})
Public Repos: {result['user_data']['public_repos']}
Followers: {result['user_data']['followers']}
Total Contributions: {sum(day['count'] for day in result['contributions'])}
Active Days: {sum(1 for day in result['contributions'] if day['count'] > 0)}
Top Repos: {', '.join([repo['repo'] for repo in result['repos'][:5]])}
Languages (Top Repos):
"""
    for repo in result['repos'][:5]:
        summary += f"{repo['repo']}: {repo['languages']}\n"
    return summary.strip()


# ---------------------------------------------------------------------------
# DSPy + FAISS initialization (done once)
# ---------------------------------------------------------------------------
# Load resume dataset for reference (if you have one)
data_file = Path(__file__).resolve().parent / "ResumeDataSet.csv"
if not data_file.exists():
    raise FileNotFoundError("ResumeDataSet.csv not found in utils folder")

df = pd.read_csv(data_file)
docs = [Document(page_content=row["Resume"], metadata={"category": row["Category"]})
        for _, row in df.iterrows()]

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

faiss_dir = Path(__file__).resolve().parent / "faiss_index"
if not faiss_dir.exists():
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(faiss_dir))
else:
    # Rebuild if needed
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(faiss_dir))

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

lm = dspy.LM("mistral/mistral-tiny", api_key=MISTRAL_API_KEY)
dspy.configure(lm=lm, rm=retriever)


# Training example for bootstrap
trainset = [
    dspy.Example(
        resume="Skilled in Python, SQL, Machine Learning.",
        github_summary="Active on GitHub with 5 repos, 120 contributions.",
        role="Data Science",
        score=85,
        strengths=["Python", "Machine Learning"],
        weaknesses=["Deep Learning", "Big Data"],
        recommendations="Add deep learning projects, mention Hadoop/Spark for big data."
    ).with_inputs("resume", "github_summary", "role")
]


class CombinedEvalSig(dspy.Signature):
    resume = dspy.InputField(desc="Resume text")
    github_summary = dspy.InputField(desc="GitHub summary")
    role = dspy.InputField(desc="Target job role")
    score = dspy.OutputField(desc="Fit score 0-100 with explanation")
    strengths = dspy.OutputField(desc="Strengths relevant to the role")
    weaknesses = dspy.OutputField(desc="Weaknesses or gaps")
    recommendations = dspy.OutputField(desc="Suggestions to improve fit")


class CombinedEvaluator(dspy.Module):
    def __init__(self, retriever):
        super().__init__()
        self.predict = dspy.Predict(CombinedEvalSig)
        self.retriever = retriever

    def forward(self, resume, github_summary, role):
        # Additional retrieval context if needed
        _ = self.retriever.get_relevant_documents(resume)
        return self.predict(resume=resume, github_summary=github_summary, role=role)


teleprompter = BootstrapFewShot()
combined_eval = teleprompter.compile(CombinedEvaluator(retriever), trainset=trainset)


# ---------------------------------------------------------------------------
# Public function for Django views
# ---------------------------------------------------------------------------
def run_full_evaluation(resume_text: str, github_username: str, job_role: str) -> dict:
    """
    Main entry point.

    Args:
        resume_text: Plain text extracted from user's PDF/DOCX.
        github_username: GitHub handle.
        job_role: Target job role.

    Returns:
        dict with keys: github_summary, score, strengths, weaknesses, recommendations
    """
    github_summary = summarize_github_for_eval(github_username)
    combined_result = combined_eval(
        resume=resume_text,
        github_summary=github_summary,
        role=job_role
    )
    return {
        "github_summary": github_summary,
        "score": combined_result.score,
        "strengths": combined_result.strengths,
        "weaknesses": combined_result.weaknesses,
        "recommendations": combined_result.recommendations,
    }

# DevProfile Insight

DevProfile Insight is an **AI-based system** that evaluates how well a candidate’s **resume** and **GitHub profile** match a specific job role.  
It checks:

- ✅ **Resume relevance**  
- ✅ **Code quality**  
- ✅ **Tech stack suitability**  
- ✅ **GitHub activity consistency**

The system then provides a **role-fit score** along with actionable feedback to guide **both job seekers and recruiters**.

---

## ✨ Features
- **Automated Resume Parsing**: Extracts key details from uploaded resumes.
- **GitHub Analysis**: Evaluates repositories, commits, and technology usage.
- **Role Matching**: Uses AI (LangChain + RAG + DSPy) to compare the candidate’s profile against job descriptions.
- **Dashboard**: Personalized dashboard for candidates and recruiters to view scores and insights.

---

## 🛠️ Tech Stack
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS
- **AI/ML**:  
  - [LangChain](https://www.langchain.com/) for LLM orchestration  
  - **RAG (Retrieval-Augmented Generation)** for contextual analysis  
  - [DSPy](https://dspy-docs.vercel.app/) for declarative prompting and evaluation

---

## 📂 Project Structure (key folders)
```
DevProfile-Insight/
├─ accounts/ # User authentication & signup
├─ dashboard/ # Main logic, views & AI evaluation
│ ├─ utils/ # evaluator.py, text_extractor.py, faiss_index
│ ├─ templates/ # personal_dashboard.html
├─ home/ # Landing & static pages
├─ static/ # CSS, JS files
├─ media/ # Uploaded resumes
├─ env/ # Virtual environment (local)
├─ manage.py
└─ README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/DevProfile-Insight.git
cd DevProfile-Insight
```
### 2️⃣ Create & activate virtual environment
```
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```
### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```
### 4️⃣ Apply migrations
```
python manage.py migrate
```
### 5️⃣ Run the server
```
python manage.py runserver
```

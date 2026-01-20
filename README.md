# ApplyWise 🤖  
### Intelligent, Trust-Driven Job Application Agent

**ApplyWise** is an autonomous AI-powered job application system that **thinks before it applies**.

Unlike traditional auto-apply bots, ApplyWise evaluates job quality, matches roles against your resume, makes explainable decisions, and only applies when it is **safe, relevant, and trusted** — with full persistence, observability, and human control.

---

## ✨ Key Features

- 🧠 **Agent-based decision making** using LangGraph
- 🔍 **Multi-source job discovery** (Greenhouse, Lever, company career pages)
- 🧪 **Job quality filtering** (scam detection, role mismatch, transparency checks)
- 🎯 **AI/ML skill & domain matching**
- 📄 **Dynamic resume positioning**
- ✍️ **Optional cover letter generation (trust-gated)**
- 🚀 **Safe application execution (Playwright, gated by trust)**
- 🗃️ **Full MongoDB persistence** (jobs, decisions, matches, applications, trust)
- ⏸️ **Human-in-the-loop support** (HOLD / manual approval)
- 🖥️ **Streamlit dashboard** for monitoring & control
- 🔐 **Idempotent & restart-safe** (never applies twice)

---

## 🧠 Design Philosophy

> **Discover broadly → Filter strictly → Decide carefully → Apply selectively**

ApplyWise is built around the idea that **not applying is often the correct action**.

The system remembers every job it has seen and every decision it has made, ensuring:
- No duplicate applications
- No infinite loops
- No blind automation

---

## 🏗️ Architecture Overview
```text
Job Discovery
↓
DB Pre-Filter (Already seen? Archived? Applied?)
↓
LangGraph Agent
├─ Resume Intelligence
├─ Job Quality Filter
├─ AI/ML Matching
├─ Application Strategy
├─ Resume Positioning
├─ Cover Letter Generation
├─ Apply (optional, trust-gated)
├─ Trust Update
├─ Hold / Archive
↓
MongoDB (Memory)
↓
Streamlit Dashboard
```
---

## 🗂️ Project Structure
```text
autoApplyAgent/
│
├── runner.py # Entry point (runs the agent)
├── main.py # LangGraph graph & AgentState
│
├── jobDiscovery.py
├── resumeIntelligence.py
├── jobQualityFilter.py
├── aimlMatching.py
├── applicationStrategy.py
├── resumePositioning.py
├── coverLetter.py
├── apply.py
├── trustUpdate.py
├── hold.py
├── archive.py
│
├── preFilter.py # DB-backed pre-run gate
│
├── db/
│ ├── init.py
│ ├── client.py # MongoDB connection
│ └── repositories.py # All DB reads/writes
│
├── dashboard/
│ ├── app.py
│ └── pages/
│ ├── Overview
│ ├── Jobs Explorer
│ ├── Decisions
│ ├── Holds
│ ├── Archives
│ ├── Applications
│ ├── Trust
│ └── Analytics
│
├── resumes/
│ └── sir.pdf
│
└── README.md
```

---

## ⚙️ Tech Stack

- **Python 3.11+**
- **LangGraph** – agent orchestration
- **MongoDB** – persistent memory
- **Playwright** – browser automation (optional, gated)
- **Streamlit** – dashboard & observability
- **BeautifulSoup / Requests** – job discovery
- **pdfplumber** – resume parsing

---

## 🚀 Getting Started

### 1️⃣ Clone & Setup

```bash
git clone https://github.com/yourusername/applywise.git
cd applywise
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

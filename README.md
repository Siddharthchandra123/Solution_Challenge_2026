# ⚖️ Decoupled AI Fairness & Ethical Compliance Platform

<div align="center">
  <img src="https://img.shields.io/badge/Architecture-Decoupled-blue" />
  <img src="https://img.shields.io/badge/Frontend-Next.js%20%7C%20React-black" />
  <img src="https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688" />
  <img src="https://img.shields.io/badge/Machine%20Learning-Fairlearn%20%7C%20SHAP-orange" />
</div>

<br>

**A production-ready Enterprise B2B Dashboard designed to algorithmically detect, XAI-explain, and mathematically mitigate Demographic Bias in AI decision-making models.**

This project was built for the **Solution Challenge 2026**. It transforms opaque, black-box Machine Learning algorithms into fully transparent, legally compliant pipelines by bridging the gap between deep Python Data Science and accessible, lightning-fast UI/UX.

---

## 🌟 The 5 Compliance Modules

1. **The Model Fixer (Fairness Audit):** Evaluates a baseline Random Forest ML model predicting Income Scores. It actively intercepts the algorithm and deploys a Post-Processing Threshold Optimizer to mechanically force the model to respect *Demographic Parity*, reducing predictive bias against women by over 80%.
2. **Explainability Engine (SHAP):** Integrates Game-Theory architecture to reverse-engineer individual AI predictions. Generates live Global Feature Importance and Beeswarm plots to prove exactly *why* a decision was made.
3. **Data Diagnostics (Quality Profiler):** An ultra-fast native scanner that mathematically dissects datasets to measure categorical completeness, track missing values, and flag vulnerable Protected Attributes before training even begins.
4. **Bivariate Explorer (Proxy Detector):** Autonomously calculates Cramer's V Contingency logic to actively warn humans when innocent variables (like Zip Code) are acting as statistical "Proxies" for forbidden demographics (like Race or Sex).
5. **Live Production Monitor (The Drift Simulator):** A time-series simulation recreating production traffic. It tracks ML model accuracy and Bias Dispersal over a chronological 24-hour window, automatically triggering compliance alarms if real-world data causes the model to "Drift" into a biased state.

---

## 🛠️ Tech Stack

**Frontend (Client Layer)**
* **Next.js 15 & React 19:** Lightning fast Server and Client routing.
* **Tailwind CSS & Custom Globals:** Providing a sleek, native B2B Dark Mode environment.
* **Recharts:** Highly responsive, data-bound analytical visualizations.

**Backend (API & Core Intelligence)**
* **FastAPI & Uvicorn:** Extreme-performance Python microservices.
* **Scikit-Learn:** Baseline Random Forest intelligence.
* **Fairlearn (Microsoft):** Constraint-based ethical mitigation.
* **SHAP:** Complex TreeExplainer probability arrays.
* **SciPy & Pandas:** Statistical significance and covariance computations.

---

## 🚀 Running the Platform Locally

Because this relies on an Enterprise Decoupled Architecture, you must spin up both the Frontend and the Backend servers independently.

### 1. Start the Machine Learning Backend (Python)
Open a terminal in the root directory:
```bash
# Strongly recommended to use a virtual environment
pip install -r requirements.txt
uvicorn api:app --reload
```
*The FastAPI server will boot and begin listening on `http://127.0.0.1:8000`.*

### 2. Start the Compliance Dashboard (Node.js)
Open a *second* separate terminal in the root directory:
```bash
npm install
npm run dev
```
*The React Dashboard will compile. Navigate your browser to `http://localhost:3000` to interact with the platform.*

---

## 📄 Deep-Dive Documentation
For a comprehensive breakdown of the mathematics, algorithms, problem space, and the actual business/enterprise architecture, please view our technical white paper included in this repository: 
👉 [**White_Paper_AI_Fairness.md**](./White_Paper_AI_Fairness.md)

---
*Built with code, compliance, and conscience.*

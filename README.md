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

## 🛠️ Enterprise Tech Stack (Phase 3)

Built on world-class Google infrastructure to ensure maximum credibility, scalability, and ethical transparency.

**Artificial Intelligence Layer**
* **Gemini 1.5 Flash**: Orchestrating the qualitative reasoning and automated mitigation strategy generation.
* **Vertex AI**: Continuous Model Monitoring and Feature Attribution Drift tracking.

**Core Data Tools & Toolkits**
* **TensorFlow Data Validation (TFDV)**: Scalable statistical auditing for massive datasets.
* **Google Model Card Toolkit**: Automated generation of transparency reports per Google standards.
* **Learning Interpretability Tool (LIT)**: Custom visual heatmapping for deep model interrogation.

**Cloud & Infrastructure**
* **Google Cloud Run**: Serverless container hosting for FastAPI microservices.
* **Firebase & Firestore**: Real-time persistence for historical "Bias Audit Reports."
* **Next.js & Tailwind**: The high-end visualization layer deployed on Firebase Hosting.

---

## 📄 Documentation & Social Impact

For a deep-dive into how our platform operates and its societal contribution, explore the following:

🚀 [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Scalable Cloud-Native Pipeline & Diagram.
🌍 [**SDG_ALIGNMENT.md**](./SDG_ALIGNMENT.md) - Mapping AI Fairness to UN SDG 10 (Reduced Inequalities).
📄 [**White_Paper_AI_Fairness.md**](./White_Paper_AI_Fairness.md) - Technical Deep-Dive into Algorithms.

---


## 🚀 Running the Platform Locally

This application utilizes a modern Microservices Architecture orchestrated via **Docker**.

### Start the entire platform via Docker
Open a terminal in the root directory and run:
```bash
docker compose up -d --build
```

**Services initialized:**
- **Frontend Dashboard:** `http://localhost:3000`
- **Gateway Proxy:** `http://localhost:8001`
- **Microservices Layer:** `8002-8007`

*Wait a moment for the containers to build and initialize. Navigate your browser to `http://localhost:3000` to interact with the platform.*

---

## 📄 Deep-Dive Documentation
For a comprehensive breakdown of the mathematics, algorithms, problem space, and the actual business/enterprise architecture, please view our technical white paper included in this repository: 
👉 [**White_Paper_AI_Fairness.md**](./White_Paper_AI_Fairness.md)

---
*Built with code, compliance, and conscience.*

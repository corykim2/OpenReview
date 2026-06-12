# OpenReview

> **An open-source AI framework for structured idea and project proposal reviews using configurable expert agents.**

## 📖 Introduction

OpenReview is an open-source framework that helps developers, students, entrepreneurs, and teams review ideas in a structured and repeatable way.

Instead of asking a language model for a single opinion, OpenReview executes multiple configurable review agents, each responsible for evaluating a specific aspect of an idea, such as technical feasibility, market potential, user experience, business value, and potential risks.

The framework aggregates these evaluations into a unified report, making idea validation more objective, transparent, and actionable.

---

## ✨ Features

* 🤖 Multi-agent AI review workflow
* 📊 Specialized reviewers (Technology, Business, Market, UX, Risk)
* 📝 Automatic Markdown review report generation
* ⚙️ Configurable prompt templates
* 📁 YAML/JSON project input support
* 🔌 Easily extensible reviewer modules
* 🌍 Open-source and community-driven

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/OpenReview.git
cd OpenReview
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
export OPENAI_API_KEY=your_api_key
```

### 4. Create an idea file

```yaml
title: AI Resume Builder

description: |
  A platform that automatically generates customized resumes using AI.

target_users:
  - Students
  - Job seekers

business_model:
  Subscription
```

### 5. Run the review

```bash
python main.py --input examples/resume_builder.yaml
```

---

## 📄 Example Output

```text
Overall Score: 84/100

Technology
- Technically feasible
- Low implementation complexity

Business
- Clear subscription model
- Strong competition exists

Market
- Large target audience
- Existing competitors should be analyzed

UX
- User flow is simple
- Resume customization should be improved

Risk
- Personal information handling required
- AI hallucination should be considered

Recommendations
- Add portfolio generation
- Support ATS optimization
```

---

## 📂 Project Structure

```text
OpenReview/

src/
    reviewers/
        technology.py
        business.py
        market.py
        ux.py
        risk.py

    report/
        generator.py

    prompts/

examples/

tests/

docs/

README.md
```

---

## 🎯 Roadmap

* [ ] Parallel multi-agent execution
* [ ] GitHub Action integration
* [ ] Web dashboard
* [ ] Custom reviewer plugins
* [ ] PDF report export
* [ ] REST API support

---

## 🤝 Contributing

Contributions are welcome!

You can contribute by:

* Adding new reviewer modules
* Improving prompt templates
* Reporting bugs
* Writing tests
* Improving documentation

---

## 📜 License

This project is licensed under the **MIT License**.

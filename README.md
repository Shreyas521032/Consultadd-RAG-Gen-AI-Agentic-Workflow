# 🧠 Consultadd RAG GenAI Agentic Workflow

A **Retrieval-Augmented Generation (RAG)** AI system built with **Next.js**, designed to automate and streamline review of complex documents like RFPs. It uses **LLMs**, **Pinecone**, and a custom chunking & processing workflow for intelligent summarization, eligibility extraction, and structured report generation.

🌍 **Live Demo**: [https://shreyas-rag-gen-ai-agentic-workflow-rdu4o1apy.vercel.app](https://shreyas-rag-gen-ai-agentic-workflow.vercel.app/)

---

## ⚙️ Features

- 📄 Upload and process large business documents (e.g., 50+ page RFPs)
- 🔍 Custom tokenizer for document chunking
- 🧠 LLM-based summarization (DeepSeek R1 / OpenAI)
- ✅ Extract and match eligibility criteria with intelligent scoring
- 📊 Auto-generate structured response reports
- 💻 Clean and responsive UI (Geist + Tailwind)

---

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+
- npm / yarn / bun
- Pinecone account
- LLM API key (DeepSeek, OpenAI, etc.)

### Clone the repo

```bash
git clone https://github.com/Shreyas521032/Consultadd-RAG-Gen-AI-Agentic-Workflow.git
cd Consultadd-RAG-Gen-AI-Agentic-Workflow
```

### Install dependencies

```bash
npm install
# or
yarn install
# or
bun install
```

### Environment Variables

Create a `.env.local` file:

```bash
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX=your_index_name
LLM_API_KEY=your_llm_key_here
```

### Run development server

```bash
npm run dev
# or
yarn dev
```

Visit [http://localhost:3000](http://localhost:3000)

---

## 🧱 Tech Stack

- **Frontend**: Next.js 14, Tailwind CSS, Geist UI
- **Backend**: Node.js, Vercel Functions
- **Vector Store**: Pinecone
- **AI Models**: DeepSeek R1 / Llama
- **Chunking**: Custom tokenizer and sentence splitter
- **Deployment**: Vercel

---

## 📂 File Structure Overview

```
app/
 ├─ api/         # API routes
 ├─ components/  # UI components
 ├─ lib/         # Pinecone, tokenizer, and LLM utils
 └─ page.js      # Entry point UI
public/
.env.local.example
next.config.js
README.md
```

---

## 🔹 Use Cases

- Resume shortlisting by matching applicant data with job descriptions for eligibility scoring
- Legal document summarization
- Proposal matching & analysis
- Automated document QA

---

## 🚧 Roadmap

- 🔐 Auth & access control
- 🔢 In-browser query assistant
- 📊 Visual analytics dashboard
- 🌍 Multi-language document support

---


---

## 📄 License

This project is licensed under the **MIT License**.

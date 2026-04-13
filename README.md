# TestGen AI

An autonomous AI pipeline that analyses a GitHub repository, generates comprehensive test suites, and opens a pull request — without any human intervention.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Agent Reference](#agent-reference)
- [Tools Used](#tools-used)
- [Tech Stack](#tech-stack)
- [Supported Languages](#supported-languages)
- [Database Schema](#database-schema)
- [Environment Variables](#environment-variables)
- [Prerequisites](#prerequisites)
- [How To Run](#how-to-run)
- [Coverage Strategy](#coverage-strategy)
- [Contributing](#contributing)
- [Linsence](#license)

## Features

1. Spins up an isolated Docker container for the repository
2. Clones the repo and scans its structure
3. Detects existing tests and installs the right test framework
4. Iteratively generates tests for each source file, running coverage checks after every change
5. Keeps looping until every source file reaches ≥ 80% coverage or 20 iterations are exhausted
6. Opens a pull request with the generated tests on a unique branch

## Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────┐
│              Pipeline Orchestrator               │
│         (test_gen_pipeline_agent)                │
└──────┬──────────────────────────────────────────┘
       │
       ├──▶ Docker Agent ──────────────────────────────────┐
       │    Spins up the correct base image                 │
       │    (python:latest / maven:latest / node:latest)    │
       │                                                    │
       ├──▶ Git Agent ──────────────────────────────────────┤
       │    Clones the repo into /app                       │
       │    Generates the folder structure                  │
       │    Creates pull requests                           │
       │                                                    │
       └──▶ Code Orchestrator ──────────────────────────────┤
                │                                           │
                ├──▶ Code Analysis Agent                    │
                │    Detects test files & project type      │
                │    Installs test dependencies             │
                │    Fixes broken build configs (pom.xml)   │
                │                                           │
                ├──▶ Code Modify Agent (loop)               │
                │    Picks lowest-coverage source file      │
                │    Writes or improves its test file       │
                │    Saves a git diff to the database       │
                │                                           │
                └──▶ Code Runner Agent (loop)               │
                     Executes the full test suite           │
                     Parses coverage report                 │
                     Returns per-file coverage numbers      │
                                                            │
                                              MongoDB ◀─────┘
                                          (job state, diffs,
                                           file coverage)
```

## Agent Reference

### Docker Agent

Responsible for infrastructure setup. Selects the correct base Docker image based on the repository language (`python:latest`, `maven:latest`, `node:latest`, etc.), starts the container, and records the container ID to the job record.

### Git Agent

Handles all GitHub operations. On analysis jobs it clones the repository into `/app` inside the container and returns the full folder structure as absolute paths. On PR jobs it creates a unique branch (`testgen/<job-short-id>-<timestamp>`), commits the generated test files, pushes the branch, and opens a pull request via the GitHub API.

### Code Analysis Agent

The first agent called by the orchestrator on every job. It reads the folder structure, identifies the project type from build files (`requirements.txt`, `pom.xml`, `package.json`, `go.mod`, etc.), detects existing test files using language-specific naming conventions, and ensures the test framework is installed and configured. For Java projects it also fixes missing JUnit/JaCoCo dependencies in `pom.xml` before returning.

### Code Modify Agent

Called once per iteration, targeting one source file at a time. It reads the source file, writes tests that cover the happy path, edge cases, and error conditions, and then calls `save_diff` to record exactly what changed to the database. Always targets the source file with the lowest current coverage. Never overwrites test files for other source files.

### Code Runner Agent

Executes the full test suite after every modify cycle and reads the coverage report. For Python it runs `pytest --cov` and reads `coverage.json`. For Java it runs `mvn test jacoco:report` and reads the JaCoCo XML report. Returns per-file coverage percentages and overall totals back to the orchestrator.

### Code Orchestrator Agent

The control loop that owns the overall strategy. It calls the analysis agent first, then alternates between the modify and runner agents until every source file reaches ≥ 80% coverage or 20 iterations are exhausted. It maintains the job state in MongoDB throughout — tracking coverage progress, written files, and diffs — and opens a clean final output before signalling the loop to end.

## Tools Used

### Core Infrastructure

- **Docker SDK (Python)** — programmatic container lifecycle management
- **Docker Images** — `python:latest`, `node:latest`, `maven:latest` for language-specific execution
- **Celery** — asynchronous job execution and distributed task queue
- **Redis** — message broker for Celery

### Backend & API

- **FastAPI** — high-performance backend API for orchestrating jobs
- **MongoDB** — persistent job state, coverage tracking, and diffs

### AI & Agent Framework

- **Google ADK (Agent Development Kit)** — multi-agent orchestration
- **OpenAI Models** — `GPT-4.1 mini`, `GPT-5 mini` for:
  - code analysis
  - test generation
  - diff creation

### Code Execution & Coverage

- **pytest + pytest-cov** — Python testing and coverage
- **JUnit 5 + JaCoCo** — Java testing and coverage
- **Jest + Istanbul** — Node.js testing and coverage
- **Go testing + cover** — native Go testing
- **RSpec + SimpleCov** — Ruby testing

### Git & Version Control

- **Git CLI** — commit, branch, and diff operations inside containers
- **GitHub API** — pull request creation and repository interaction
- **GitHub OAuth** — user authentication

### Frontend

- **React** — UI framework
- **TypeScript** — type safety
- **Tailwind CSS** — styling

## Tech Stack

| Layer             | Technology                        |
| ----------------- | --------------------------------- |
| Agent framework   | Google ADK                        |
| LLM               | GPT-4.1 mini / GPT-5 mini         |
| Task queue        | Celery + Redis                    |
| Database          | MongoDB                           |
| Container runtime | Docker SDK (Python)               |
| Backend API       | FastAPI                           |
| Frontend          | React + TypeScript + Tailwind CSS |
| Auth              | GitHub OAuth                      |

## Supported Languages

| Language | Test Framework | Coverage Tool                    |
| -------- | -------------- | -------------------------------- |
| Python   | pytest         | pytest-cov / coverage.json       |
| Java     | JUnit 5        | JaCoCo                           |
| Node.js  | Jest           | Istanbul / coverage-summary.json |

## Database Schema

```json
{
  "job_id": "uuid",
  "user_id": "github_id",
  "repo_url": "owner/repo",
  "language": "python",
  "container_id": "abc123",

  "containerCreated": "IN-PROGRESS | SUCCEEDED | FAILED",
  "repoCloned": "IN-PROGRESS | SUCCEEDED | FAILED",
  "analysisComplete": "IN-PROGRESS | SUCCEEDED | FAILED",
  "jobComplete": "IN-PROGRESS | SUCCEEDED | FAILED",

  "initialCoverage": "21.0",
  "currentCoverage": "74.5",
  "finalCoverage": "100.0",

  "files": [{ "filename": "/app/app.py", "coverage": 100 }],

  "tests": [
    {
      "filename": "/app/test_app.py",
      "diff": "diff --git a/test_app.py ...",
      "coverage": 100
    }
  ],

  "prCreated": true,
  "prUrl": "https://github.com/owner/repo/pull/42",

  "created_at": "ISO timestamp"
}
```

## Environment Variables

To configure the project, create a `.env` file in the backend and frontend folder and add the following environment variables respectively:

**BACKEND**

```env
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

CELERY_BROKER_URL=
CELETY_BROKER_BACKEND=

USER=
PASSWORD=
HOST=
APP_NAME=

SECRET_KEY=
ALGORITHM=

OPENAI_API_KEY=
```

**FRONTEND (Only for local deployment)**

```env
VITE_GITHUB_CLIENT_ID=
VITE_BACKEND_HOST=
VITE_BACKEND_PORT=
```

## Prerequisites

1. You must have a github oauth app created. (Github acc -> Settings -> Developer Settings -> Oauth apps). This gives you the client id and secret.
2. Docker
3. MongoDB cluster
4. OpenAI API Key

## How to run

Once you have the prerequisites

#### 1. Github

```bash
git clone https://github.com/Aadhithya-Ganesh/TestGen-AI.git
```

```bash
cd TestGen-AI
```

Configure the env file after cloning before you continue

#### 2. Run the application

```bash
docker compose up --build
```

### Visit the website at "localhost"

## Coverage Strategy

The orchestrator does not exit when overall coverage looks high. It checks **every source file individually** and only exits when no single file is below 80%. This prevents a well-covered file from masking an untested one in the aggregate number.

```
app.py   → 100% ✅
setup.py →  45% ❌  ← loop continues, this file is targeted next
utils.py →  80% ✅
```

The loop exits only when every file shows ✅ or 20 iterations have been exhausted.

## Contributing

When the user clicks "Create Pull Request" in the UI:

1. The API triggers a new Celery task
2. The Git Agent creates a unique branch: `testgen/<job-id-short>-<YYYYMMDD-HHMMSS>`
3. All generated test files are committed with git identity set to `TestGen Bot`
4. The branch is pushed using the GitHub token injected into the remote URL
5. A PR is opened via the GitHub API targeting `main`
6. The job record is updated with `prCreated: true` and `prUrl`
7. The frontend polls until `prCreated` is set and shows the PR link

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE.txt) file for details.

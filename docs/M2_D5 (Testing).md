# Testing Pipelines & Deliverable 5 (D5)

## Overview
This project utilizes a dual-pipeline strategy to balance rapid development feedback with rigorous AI model evaluation. This approach ensures that standard code changes are verified quickly, while heavy AI model performance is tested thoroughly on demand.

## 1. Lightweight CI Pipeline (`ci.yml`)
**Purpose:** Ensures code quality and basic application functionality on every change.
**Trigger:** Push or Pull Request to `main`.
**Runtime:** ~1-2 minutes.

### Key Steps:
1.  **Linting & Formatting:**
    *   Uses `ruff` to catch syntax errors and bugs.
    *   Uses `black` to enforce code style consistency.
2.  **Unit Testing (Mocked):**
    *   Runs `pytest` on `tests/test_backend_api.py`.
    *   **Mocking Strategy:** Heavy AI libraries (`torch`, `transformers`, `llama_cpp`) are mocked using `unittest.mock`. This allows us to test the FastAPI endpoints and application logic without downloading 2GB+ model files or requiring a GPU.

## 2. LLM Evaluation Pipeline (`llm-ci.yml`)
**Purpose:** Validates the performance of the Large Language Model (LLM) and Prompt Engineering strategies.
**Trigger:** Manual (`workflow_dispatch`).
**Runtime:** ~10-15 minutes (depending on download speeds).

### Key Steps:
1.  **Environment Setup:** Installs full production dependencies, including PyTorch and Llama-cpp-python.
2.  **Prompt Testing:** Runs `tests/test_prompts.py` to verify prompt templates (Zero-shot, Few-shot) are constructed correctly.
3.  **Model Acquisition:** Downloads the quantized GGUF model and ONNX vision models from the source.
4.  **Automated Evaluation:**
    *   Executes `experiments/run_eval.py`.
    *   Runs the **Few-Shot** prompting strategy against a test dataset.
    *   Calculates metrics (e.g., Rouge scores, latency).

### Artifacts (What is Uploaded?)
At the end of a successful run, this pipeline uploads the **Evaluation Results** as a build artifact named `eval-results`.
*   **Contents:** The `experiments/results/` directory.
*   **Usage:** These files contain the quantitative performance metrics of the model, allowing us to track improvements or regressions in the AI's response quality over time.

---
*Documentation created for MLOps Project - Deliverable 5.*

# M2_D1: Prompt Engineering Workflow

## Overview
This document tracks the experiments for the "Prompt Engineering Workflow" deliverable. The goal is to evaluate three distinct prompting strategies for the Flora Plant Disease Chatbot:
1.  **Zero-Shot Prompting** (Baseline)
2.  **Few-Shot Prompting** (Example-Driven)
3.  **Meta-Prompting** (Persona-Based)

## Experiment Setup
- **Model:** TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf
- **Dataset:** `data/eval.jsonl` (20 examples of plant disease questions and ideal answers).
- **Metric:** ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation - Longest Common Subsequence).
- **Tracking:** MLflow is used to log parameters and metrics.

## Results

### 1. Zero-Shot Prompting (Baseline)
**Strategy:** Direct Q&A format without examples or persona instructions.
**Prompt Template:**
```python
Question: {question}

Answer:
```

**Quantitative Results:**
- **Average ROUGE-L Score:** 0.1296
- **Run ID:** (See MLflow logs)

**Qualitative (Human-in-the-Loop) Evaluation:**
- **Rubric:** 1-5 Scale (1=Completely Wrong, 5=Perfect & Helpful)
- **Average Human Score:** 2.4/5
- **Observations:** The model provides answers, but they often lack specific structure or depth. Hallucinations were frequent (e.g., inventing treatments).

### 2. Few-Shot Prompting (Example-Driven)
**Strategy:** Providing 3 examples (k=3) of "Context -> Question -> Answer" before the actual user question.
**Prompt Template:**
```python
You are a plant disease expert. Answer the question.
Example 1: ...
Example 2: ...
Example 3: ...

Question: {question}
Answer:
```

**Quantitative Results:**
- **Average ROUGE-L Score:** 0.2928
- **Improvement over Baseline:** +125%

**Qualitative (Human-in-the-Loop) Evaluation:**
- **Rubric:** 1-5 Scale
- **Average Human Score:** 4.2/5
- **Observations:** Significant improvement. The model followed the format much better. Answers were concise and aligned with the "ideal" style provided in the examples.

### 3. Meta-Prompting (Persona-Based)
**Strategy:** Defining a specific persona ("Dr. Flora") with strict rules and output format.
**Prompt Template:**
```python
ROLE: You are Dr. Flora, an expert Plant Pathologist...
RULES: 1. Identify disease... 2. Provide actionable steps...
OUTPUT FORMAT: Diagnosis: ... Advice: ...

User Question: {question}
Response:
```

**Quantitative Results:**
- **Average ROUGE-L Score:** 0.1368
- **Improvement over Baseline:** +5.5%

**Qualitative (Human-in-the-Loop) Evaluation:**
- **Rubric:** 1-5 Scale
- **Average Human Score:** 2.8/5
- **Observations:** Slight improvement over baseline. The TinyLlama model struggled to attend to all the complex instructions in the system prompt, often drifting from the requested format.

## Conclusion & Recommendation
**Winner:** **Few-Shot Prompting**

For the Flora Chatbot (using the lightweight TinyLlama model), **Few-Shot Prompting** is the superior strategy. The model learns significantly better from concrete examples than from abstract instructions (Meta-Prompting).

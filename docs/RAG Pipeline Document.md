# Flora Care Production Pipeline Documentation

## 1. Executive Summary
This document outlines the architecture and functionality of the **Flora Care** machine learning pipeline. The system acts as a hybrid diagnostic tool for plant diseases, combining **Computer Vision (CV)** for visual symptom detection and **Retrieval-Augmented Generation (RAG)** for agricultural knowledge retrieval. The entire workflow is tracked using **MLflow** for experiment logging and artifact management.

## 2. System Architecture
The pipeline consists of three major components:

1. **Visual Diagnostics (CV):** Swin Transformer model trained on PlantVillage.
2. **Knowledge Retrieval (RAG):** Hybrid semantic search over ChromaDB.
3. **MLOps Layer:** End-to-end MLflow tracking for hyperparameters, metrics, and artifacts.

---

## 3. Component A: Computer Vision Training Module
A hierarchical vision transformer classifies plant diseases from leaf images.

### Model Details
- **Architecture:** `microsoft/swin-tiny-patch4-window7-224`
- **Dataset:** PlantVillage (Training split)

### Preprocessing & Augmentation
- **Train:** Random resized crop (224×224), horizontal flip, 15° rotation, color jitter
- **Validation:** Resize + center crop

### Training Configuration
- **Framework:** Hugging Face Trainer
- **Batch Size:** 32
- **Learning Rate:** 2e-5
- **Epochs:** 10
- **Early Stopping:** Patience 3

### Outputs
Artifacts stored at: `flora_cv_model`

---

## 4. Component B: RAG Ingestion & Database
Processes agricultural text knowledge into a vector store.

### Data Source
JSON metadata including disease names, treatments, and URLs.

### Text Processing
- **Splitter:** RecursiveCharacterTextSplitter (chunk size 800, overlap 100)
- **Metadata:** disease, source, is_healthy

### Vector Database
- **Backend:** ChromaDB
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`

---

## 5. MLOps & Artifact Management
MLflow tracks CV training and RAG ingestion.

### Logged Metrics
- CV loss & accuracy
- Retrieval latency
- Total document chunks

### Export Strategy
All artifacts packaged into `flora_artifacts.zip`.

---

RAG PIPLEINE AND FULL ARCHITECTURE PIPELINE DIAGRAM
<img width="4144" height="4932" alt="DIAGRAM 1" src="https://github.com/user-attachments/assets/f17ceeae-b79d-42a9-aab3-4cc389666f52" />

# ML Workflow Monitoring: Evidently AI
## Technical Documentation

---

## 1. Overview

This module implements **Data Drift Detection** for the MLOps pipeline using **Evidently AI** to compare the training distribution (*Reference*) against production/test inference data (*Current*).

**Dashboard Access:** `http://localhost:7000`

### 1.1 Key Monitoring Metrics

- **Data Drift:** Statistical analysis of input feature shifts (color histograms, contrast, brightness)
- **Target Drift:** Distribution monitoring of predicted classes to detect model bias
- **Correlations:** Feature relationship consistency validation

---

## 2. Quick Start Guide

The implementation decouples drift calculation from dashboard serving to ensure instant loading.

### 2.1 Prerequisites

```bash
pip install evidently pandas scikit-learn
```

### 2.2 Pipeline Execution

The workflow is managed through `make` targets:

```bash
# Step 1: Prepare Metadata (Scans images & creates CSVs)
make prepare-data

# Step 2: Calculate Drift (Generates the HTML report)
make generate-drift

# Step 3: View Dashboard (Hosts at localhost:7000)
make monitor
```

---

## 3. Implementation Architecture

### 3.1 Data Ingestion (`prepare_metadata.py`)

The raw image dataset is transformed into structured tabular format (CSV) containing metadata and pixel statistics.

**Implementation:**

```python
# backend/prepare_metadata.py

def create_metadata():
    # Scans folders based on class_names.txt
    
    # Split into Reference (Train) and Current (Test)
    # Stratify ensures class balance preservation in reference set
    train, test = train_test_split(df, test_size=0.2, stratify=df['class_label'])

    train.to_csv("backend/data/train.csv", index=False)
    test.to_csv("backend/data/test.csv", index=False)
```

**Key Features:**
- Automatic folder scanning based on class definitions
- Stratified sampling for balanced reference set
- Persistent storage in CSV format

### 3.2 Drift Calculation (`generate_dashboard.py`)

Utilizes `DataDriftPreset` for automatic statistical test selection (Kolmogorov-Smirnov, Wasserstein distance) based on feature types.

**Implementation:**

```python
# backend/generate_dashboard.py

from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

def generate():
    reference = pd.read_csv("backend/data/train.csv")
    current = pd.read_csv("backend/data/test.csv")

    # Initialize report with standard Drift Metrics
    report = Report(metrics=[
        DataDriftPreset(), 
    ])
    
    # Calculate difference between Training and Inference data
    report.run(reference_data=reference, current_data=current)
    
    # Export to static HTML
    report.save_html("backend/monitoring/dashboard.html")
```

**Statistical Methods:**
- Kolmogorov-Smirnov test for continuous distributions
- Chi-square test for categorical features
- Wasserstein distance for distribution similarity

### 3.3 Dashboard Hosting (`serve_dashboard.py`)

Lightweight Python HTTP server exposing the generated report on the designated port.

**Implementation:**

```python
# backend/serve_dashboard.py

import http.server
import socketserver

PORT = 7000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="backend/monitoring", **kwargs)

# Serve at localhost:7000
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"✅ Dashboard running at: http://localhost:{PORT}/dashboard.html")
    httpd.serve_forever()
```

**Server Characteristics:**
- Port: 7000
- Protocol: HTTP
- Directory: `backend/monitoring/`
- Access: `http://localhost:7000/dashboard.html`

---

## 4. Monitoring Results

### 4.1 Dataset-Level Drift Summary

Based on the latest pipeline execution:

| Dataset | Drift Detection Rate | Features Analyzed | Status |
|---------|---------------------|-------------------|--------|
| **LLM RAG Dataset** | 50.0% (1 out of 2) | `class_id`, `confidence` | ⚠️ Dataset Drift Detected |
| **Plant Disease Dataset** | 0.0% (0 out of 17) | Color statistics, brightness, contrast | ✅ No Drift Detected |

### 4.2 Feature-Level Analysis

#### 4.2.1 LLM RAG Dataset Features

| Feature | Type | Data Drift | Statistical Test | Drift Score | Status |
|---------|------|-----------|------------------|-------------|--------|
| `class_id` | num | Not Detected | K-S p-value | 0.702657 | ✅ Pass |
| `confidence` | num | **Detected** | K-S p-value | 0 | ⚠️ Drift |

**Observations:**
- **class_id:** Distribution remains stable between reference and current datasets (p-value: 0.70)
- **confidence:** Significant drift detected in model confidence scores, indicating potential model behavior changes or data quality issues

#### 4.2.2 Plant Disease Dataset Features

| Feature | Type | Data Drift | Statistical Test | Drift Score | Status |
|---------|------|-----------|------------------|-------------|--------|
| `std_blue` | num | Not Detected | Wasserstein distance (normed) | 0.048781 | ✅ Pass |
| `contrast` | num | Not Detected | Wasserstein distance (normed) | 0.038528 | ✅ Pass |
| `mean_green` | num | Not Detected | Wasserstein distance (normed) | 0.0382 | ✅ Pass |
| `green_ratio` | num | Not Detected | Wasserstein distance (normed) | 0.036744 | ✅ Pass |
| `blue_ratio` | num | Not Detected | Wasserstein distance (normed) | 0.031279 | ✅ Pass |
| `brightness` | num | Not Detected | Wasserstein distance (normed) | 0.028552 | ✅ Pass |
| `std_green` | num | Not Detected | Wasserstein distance (normed) | 0.028333 | ✅ Pass |
| `mean_red` | num | Not Detected | Wasserstein distance (normed) | 0.026638 | ✅ Pass |
| `mean_blue` | num | Not Detected | Wasserstein distance (normed) | 0.026458 | ✅ Pass |
| `red_ratio` | num | Not Detected | Wasserstein distance (normed) | 0.023941 | ✅ Pass |
| *Additional features* | num | Not Detected | Wasserstein distance (normed) | <0.05 | ✅ Pass |

**Observations:**
- All 17 color and geometric features show minimal drift (scores <0.05)
- Wasserstein distance metric indicates stable distribution patterns
- Strong correlation preservation between reference and current datasets

### 4.3 Correlation Analysis

**Dataset Correlations:** Pearson, Spearman, Kendall, and Cramer's V correlation matrices computed for both reference and current datasets show consistent feature relationships, indicating structural stability in the data.

### 4.4 Interpretation Guidelines

- **✅ Pass Status:** Drift score <0.05 or p-value >0.05; model operates within expected parameters
- **⚠️ Warning Status:** Minor drift observed (0.05-0.1); requires monitoring but no immediate action needed
- **❌ Fail Status:** Significant drift detected (>0.1 or p-value <0.05); model retraining recommended

---

## 5. CI/CD Integration

### 5.1 Current Implementation

The workflow is integrated into the project `Makefile` for streamlined execution.

### 5.2 Future Enhancements

Planned improvements include:

1. **Automated Triggering:** Integration with GitHub Actions (`ci.yml`) to execute `make generate-drift` automatically on Pull Requests
2. **Artifact Generation:** Drift reports stored as CI/CD artifacts for historical tracking
3. **Alert Mechanism:** Automated notifications on drift threshold breaches
4. **Scheduled Monitoring:** Periodic drift analysis on production data

---

## 6. Technical Specifications

### 6.1 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| evidently | Latest | Drift detection and reporting |
| pandas | Latest | Data manipulation |
| scikit-learn | Latest | Data splitting and preprocessing |

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue:** Dashboard not loading  
**Solution:** Verify server is running on port 7000 and check `backend/monitoring/dashboard.html` exists

**Issue:** Drift calculation fails  
**Solution:** Ensure CSV files exist in `backend/data/` and contain required columns

**Issue:** Port 7000 already in use  
**Solution:** Modify `PORT` variable in `serve_dashboard.py` or terminate conflicting process

---

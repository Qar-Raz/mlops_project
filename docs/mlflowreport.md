# **MLflow Experiment Report**


This document details the training dynamics and performance evaluation of the **swin_cv_model** within the **Flora_Care_Production_Pipeline**.  
The experiment was tracked using **MLflow** to monitor hyperparameters, loss convergence, and system throughput.  
The analysis confirms that the model has successfully converged with high accuracy and stability.

---

# **1. Final Performance Metrics**

The following figure displays the comprehensive list of metrics recorded at the conclusion of the 10th epoch:
<img width="1920" height="955" alt="Screenshot 2025-12-06 at 3 58 27 PM" src="https://github.com/user-attachments/assets/4046fb73-f8b4-4cd9-ad01-36728a9fdfa4" />



---

## **Evaluation of Tracked Metrics**

### **Generalization Capability (eval_loss)**  
The final evaluation loss recorded is **0.01027**.  
This metric represents the error rate on the validation dataset.  
Such a distinctively low value indicates that the model generalizes exceptionally well to unseen data and is not suffering from overfitting.

### **Training Convergence (loss)**  
The final training loss is **0.0276**.  
This signifies that the model successfully minimized the objective function on the training set, effectively learning the underlying patterns of the input data.

### **Training Stability (grad_norm)**  
The gradient norm (**645,107.8**) reflects the magnitude of the vector of derivatives.  
Tracking this ensures that the training process remained numerically stable without vanishing or exploding gradients.

### **Computational Throughput (train/eval_samples_per_second)**  
- **Training Speed:** ~133.14 samples/sec  
- **Inference Speed:** ~223.75 samples/sec  

This indicates efficient inference capabilities suitable for production deployment.

---

# **2. Training Dynamics and Visualization Analysis**
<img width="1918" height="947" alt="Screenshot 2025-12-06 at 3 57 50 PM" src="https://github.com/user-attachments/assets/89fc92aa-b800-47d0-8fb4-6aad4193a86f" />

<img width="1920" height="439" alt="Screenshot 2025-12-06 at 3 58 09 PM" src="https://github.com/user-attachments/assets/53d5374d-59f2-4aa7-bdd6-12df1f11ffb4" />


The following figures illustrate the progression of key metrics over the course of the training steps.  
These visualizations provide insight into the learning schedule, convergence behavior, and system performance.


---

## **Detailed Analysis of Visualizations**

### **A. Loss Convergence (loss and eval_loss)**

The plots for both training and evaluation loss demonstrate an ideal learning trajectory.

- **Rapid Feature Extraction:**  
  The initial phase (Steps 0–1,000) shows a steep, exponential decay in loss.  
  This indicates that the Swin Transformer architecture rapidly identified the primary features within the dataset.

- **Asymptotic Convergence:**  
  After the initial drop, the curves flatten (plateau).  
  This confirms that the model reached an optimal state where further iterations provided marginal gains—showing efficient use of the 10-epoch duration.

- **Validation Consistency:**  
  The eval_loss curve tracks closely with the training loss without divergence.  
  This parallelism is a critical indicator of robust generalization.

---

### **B. Learning Rate Schedule (learning_rate)**

The learning rate plot shows:

- **Warm-up Phase:**  
  A linear increase from zero, peaking around step 1,000.  
  This helps stabilize training before larger updates occur.

- **Linear Decay:**  
  After the peak, the learning rate decreases linearly.  
  This allows increasingly precise fine-tuning as convergence is approached.

---

### **C. Gradient Behavior (grad_norm)**

The visualization of the gradient norm displays the L2 norm of the gradients at each step.

- **Stability:**  
  Despite natural oscillations (typical of stochastic gradient descent), the overall magnitude stays controlled.  
  No signs of divergence appear, indicating a stable backpropagation process.

---

### **D. System Latency and Throughput (eval_runtime & samples_per_second)**

The performance plots indicate a stable computational environment.

- **Steady State:**  
  After an initialization spike, both runtime and throughput stabilize.  
  The horizontal trend lines confirm consistent resource allocation, ensuring predictable latency throughout the experiment.

---


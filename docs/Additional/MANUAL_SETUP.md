# Manual Backend Setup Guide (No Docker)

Since you cannot use Docker, follow these steps to run the backend locally on your Windows machine.

## 1. Prerequisites

*   **Python 3.10 or 3.11** (You seem to have Python installed).
*   **Visual Studio Build Tools** (Required for `llama-cpp-python` if a pre-built wheel is not available).
    *   Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
    *   Select "Desktop development with C++" workload.
*   **Disk Space**: Ensure you have at least 5-10 GB of free space for models and dependencies.

## 2. Install Dependencies

Open a terminal (PowerShell or Command Prompt) and navigate to the `backend` folder:

```powershell
cd e:\Downloads\mlopsproject1\mlops_project-1\backend
```

Run the following commands:

```powershell
# Install PyTorch (CPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
# Note: If this fails with "No space left on device", check your C: drive space.
# If it fails building llama-cpp-python, ensure you have C++ Build Tools installed.
pip install -r requirements.txt
```

**Troubleshooting `llama-cpp-python`**:
If `pip install -r requirements.txt` fails on `llama-cpp-python`, try installing a pre-built wheel from [here](https://github.com/abetlen/llama-cpp-python/releases) that matches your Python version and OS, or try:
```powershell
pip install llama-cpp-python --prefer-binary --extra-index-url=https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cpu
```

## 3. Set Up Credentials

Create a file named `.env` in the `backend` folder (`e:\Downloads\mlopsproject1\mlops_project-1\backend\.env`).
Add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
MODEL_DIR=models
```

## 4. Download Models

This step fixes the "exit 3" error (which is caused by missing models).

Run the download script:

```powershell
python download_models.py
```

This will:
1.  Download the model package from S3.
2.  Download the LLM from HuggingFace.
3.  Create a `models` folder in `backend/models`.

## 5. Run the Application

Start the backend server:

```powershell
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 6. Verify

Open your browser to:
*   [http://localhost:8000/docs](http://localhost:8000/docs) - API Documentation
*   [http://localhost:8000/](http://localhost:8000/) - Health Check

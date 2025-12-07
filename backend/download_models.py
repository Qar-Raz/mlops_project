import boto3
import zipfile
import os
import shutil
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")
NLTK_DIR = os.path.join(MODEL_DIR, "nltk_data") # Keep for consistency

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(NLTK_DIR, exist_ok=True)

from optimum.onnxruntime import ORTModelForImageClassification
from transformers import AutoImageProcessor

load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

BUCKET_NAME = "mlopsmodel"
ZIP_NAME = "flora_deployment_package.zip"
GGUF_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

def clean_redundant_files():
    print("🧹 Cleaning up redundant files...")
    cv_dir = os.path.join(MODEL_DIR, "flora_cv_model")
    onnx_dir = os.path.join(MODEL_DIR, "flora_cv_onnx")
    # Delete PyTorch model if ONNX exists to save space
    if os.path.exists(onnx_dir) and os.path.exists(cv_dir):
        shutil.rmtree(cv_dir)
    # Delete Zip
    zip_path = os.path.join(MODEL_DIR, ZIP_NAME)
    if os.path.exists(zip_path):
        os.remove(zip_path)

def download_and_unzip(s3_client, bucket, zip_name, extract_to):
    # Only download if ONNX missing
    if not os.path.exists(os.path.join(extract_to, "flora_cv_onnx")):
        zip_path = os.path.join(extract_to, zip_name)
        print(f"⬇️ Downloading {zip_name}...")
        try:
            s3_client.download_file(bucket, zip_name, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        except Exception as e:
            print(f"⚠️ S3 Download Warning: {e}")

def convert_to_onnx():
    cv_dir = os.path.join(MODEL_DIR, "flora_cv_model")
    onnx_dir = os.path.join(MODEL_DIR, "flora_cv_onnx")

    if os.path.exists(onnx_dir):
        print("✅ ONNX model ready.")
        return

    if os.path.exists(cv_dir):
        print("🔄 Converting PyTorch to ONNX...")
        try:
            model = ORTModelForImageClassification.from_pretrained(cv_dir, export=True)
            processor = AutoImageProcessor.from_pretrained(cv_dir)
            model.save_pretrained(onnx_dir)
            processor.save_pretrained(onnx_dir)
        except Exception as e:
            print(f"❌ Conversion failed: {e}")

def setup_models():
    print(f"🚀 Model Directory: {MODEL_DIR}")
    s3 = boto3.client("s3")
    
    download_and_unzip(s3, BUCKET_NAME, ZIP_NAME, MODEL_DIR)
    convert_to_onnx()
    
    # LLM
    if not os.path.exists(os.path.join(MODEL_DIR, GGUF_FILE)):
        print("⬇️ Downloading GGUF...")
        hf_hub_download(repo_id=GGUF_REPO, filename=GGUF_FILE, local_dir=MODEL_DIR)
    else:
        print("✅ GGUF Found.")

    clean_redundant_files()
    print("\n✨ Setup Complete!")

if __name__ == "__main__":
    setup_models()
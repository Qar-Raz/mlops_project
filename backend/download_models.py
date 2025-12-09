import boto3
import zipfile
import os
import shutil
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

# Load .env from parent directory (project root) or current directory
load_dotenv()

BUCKET_NAME = "mlopsmodel"
ZIP_NAME = "flora_deployment_package.zip"
GGUF_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"


def clean_redundant_files():
    print("🧹 Cleaning up redundant files...")
    # Delete Zip
    zip_path = os.path.join(MODEL_DIR, ZIP_NAME)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # Delete .cache if it exists (HuggingFace sometimes leaves this)
    cache_path = os.path.join(MODEL_DIR, ".cache")
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)

    # Delete nltk_data if it exists (Legacy)
    nltk_path = os.path.join(MODEL_DIR, "nltk_data")
    if os.path.exists(nltk_path):
        shutil.rmtree(nltk_path)


def download_and_unzip(s3_client, bucket, zip_name, extract_to):
    # Only download if ONNX or RAG DB missing
    if not os.path.exists(
        os.path.join(extract_to, "flora_cv_onnx")
    ) or not os.path.exists(os.path.join(extract_to, "flora_rag_db")):
        zip_path = os.path.join(extract_to, zip_name)
        print(f"⬇️ Downloading {zip_name}...")
        try:
            s3_client.download_file(bucket, zip_name, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        except Exception as e:
            print(f"⚠️ S3 Download Warning: {e}")


def setup_models():
    print(f"🚀 Model Directory: {MODEL_DIR}")
    s3 = boto3.client("s3")

    # Expects the ZIP to contain the ALREADY CONVERTED 'flora_cv_onnx' folder
    download_and_unzip(s3, BUCKET_NAME, ZIP_NAME, MODEL_DIR)

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

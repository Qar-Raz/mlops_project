import boto3
import zipfile
import os
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from optimum.onnxruntime import ORTModelForImageClassification
from transformers import AutoImageProcessor

load_dotenv()

BUCKET_NAME = "mlopsmodel"
ZIP_NAME = "flora_deployment_package.zip"
GGUF_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# Force models to be downloaded to 'models' folder in the same directory as this script
# This ensures they are in the correct place for the Docker build (backend/models)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

print(f"📂 Model Directory set to: {MODEL_DIR}")
print(f"ℹ️  This script will download models to: {os.path.abspath(MODEL_DIR)}")

# Ensure the directory exists
os.makedirs(MODEL_DIR, exist_ok=True)


def download_and_unzip(s3_client, bucket, zip_name, extract_to):
    zip_path = os.path.join(extract_to, zip_name)
    print(f"⬇️ Downloading {zip_name} from S3...")
    s3_client.download_file(bucket, zip_name, zip_path)
    print(f"📦 Unzipping {zip_name}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)
    print(f"✅ {zip_name} extracted.")


def convert_to_onnx():
    cv_dir = os.path.join(MODEL_DIR, "flora_cv_model")
    onnx_dir = os.path.join(MODEL_DIR, "flora_cv_onnx")

    if os.path.exists(onnx_dir):
        print("✅ ONNX model already exists.")
        return

    if not os.path.exists(cv_dir):
        print(f"❌ Cannot convert: {cv_dir} not found.")
        return

    print("🔄 Converting PyTorch model to ONNX (this may take a moment)...")
    try:
        # Load the model and export it to ONNX
        model = ORTModelForImageClassification.from_pretrained(cv_dir, export=True)
        processor = AutoImageProcessor.from_pretrained(cv_dir)

        # Save the ONNX model and processor
        model.save_pretrained(onnx_dir)
        processor.save_pretrained(onnx_dir)
        print("✅ Export complete! ONNX model saved.")
    except Exception as e:
        print(f"❌ ONNX Conversion failed: {e}")
        print("⚠️ The app will fallback to the slower PyTorch model.")


def setup_models():
    print("🚀 Starting Model Setup...")
    s3 = boto3.client("s3")

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # 1. Download Base Models (CV PyTorch + RAG) from S3
    cv_path = os.path.join(MODEL_DIR, "flora_cv_model")
    rag_path = os.path.join(MODEL_DIR, "flora_rag_db")

    if os.path.exists(cv_path) and os.path.exists(rag_path):
        print("✅ Base models already present.")
    else:
        try:
            download_and_unzip(s3, BUCKET_NAME, ZIP_NAME, MODEL_DIR)
        except Exception as e:
            print(f"❌ Error downloading from S3: {e}")
            print("⚠️ Check your AWS credentials.")

    # 2. Convert CV Model to ONNX (Optimization)
    convert_to_onnx()

    # Cleanup: Remove the heavy PyTorch model after conversion to save space
    if os.path.exists(cv_path) and os.path.exists(
        os.path.join(MODEL_DIR, "flora_cv_onnx")
    ):
        print("🧹 Cleaning up raw PyTorch model to save space...")
        import shutil

        shutil.rmtree(cv_path)

    # Cleanup: Remove .cache if it exists
    cache_dir = os.path.join(MODEL_DIR, ".cache")
    if os.path.exists(cache_dir):
        import shutil

        shutil.rmtree(cache_dir)

    # 3. Download GGUF LLM (From HuggingFace)
    gguf_path = os.path.join(MODEL_DIR, GGUF_FILE)
    if os.path.exists(gguf_path):
        print("✅ GGUF Model already present.")
    else:
        print("⬇️ Downloading GGUF Model from HuggingFace...")
        try:
            hf_hub_download(
                repo_id=GGUF_REPO,
                filename=GGUF_FILE,
                local_dir=MODEL_DIR,
                local_dir_use_symlinks=False,
            )
            print("✅ GGUF Model downloaded.")
        except Exception as e:
            print(f"❌ Failed to download GGUF: {e}")


if __name__ == "__main__":
    setup_models()

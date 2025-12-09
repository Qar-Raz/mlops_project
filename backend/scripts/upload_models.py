import os
import zipfile
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = "mlopsmodel"
ZIP_NAME = "flora_deployment_package.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Look for models in ../models (relative to this script)
# i.e., backend/scripts/../models -> backend/models
MODEL_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "models")

# If MODEL_DIR doesn't exist there, try local 'models' (in case user moved it)
if not os.path.exists(MODEL_DIR):
    MODEL_DIR = os.path.join(SCRIPT_DIR, "models")

ONNX_DIR = os.path.join(MODEL_DIR, "flora_cv_onnx")
RAG_DIR = os.path.join(MODEL_DIR, "flora_rag_db")
ZIP_PATH = os.path.join(MODEL_DIR, ZIP_NAME)


def zip_folders(zip_path, folders):
    print(f"📦 Zipping files to {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder_path, folder_name in folders:
            if not os.path.exists(folder_path):
                print(f"⚠️ Warning: Folder not found: {folder_path}")
                continue

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate archive name (relative to the folder we are zipping)
                    # We want the structure inside zip to be:
                    # flora_cv_onnx/...
                    # flora_rag_db/...

                    # Rel path from the parent of the folder
                    parent = os.path.dirname(folder_path)
                    arcname = os.path.relpath(file_path, parent)

                    print(f"  Adding: {arcname}")
                    zipf.write(file_path, arcname)


def upload_to_s3(file_path, bucket, object_name):
    print(f"☁️ Uploading {os.path.basename(file_path)} to S3 bucket '{bucket}'...")
    s3 = boto3.client("s3")
    try:
        s3.upload_file(file_path, bucket, object_name)
        print("✅ Upload Successful!")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        print("Check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")


def main():
    print(f"🔍 Looking for models in: {MODEL_DIR}")

    if not os.path.exists(ONNX_DIR):
        print(f"❌ Error: ONNX model not found at {ONNX_DIR}")
        print("   Please run 'python export_onnx.py' first (requires torch/optimum).")
        return

    if not os.path.exists(RAG_DIR):
        print(f"❌ Error: RAG DB not found at {RAG_DIR}")
        return

    # 1. Zip the folders
    folders_to_zip = [(ONNX_DIR, "flora_cv_onnx"), (RAG_DIR, "flora_rag_db")]
    zip_folders(ZIP_PATH, folders_to_zip)

    # 2. Upload to S3
    upload_to_s3(ZIP_PATH, BUCKET_NAME, ZIP_NAME)

    # 3. Cleanup (Optional)
    # os.remove(ZIP_PATH)
    # print("🧹 Cleaned up local zip file.")


if __name__ == "__main__":
    main()

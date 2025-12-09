import os
from optimum.onnxruntime import ORTModelForImageClassification
from transformers import AutoImageProcessor
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to find 'models' (backend/models)
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(os.path.dirname(SCRIPT_DIR), "models"))
CV_DIR = os.path.join(MODEL_DIR, "flora_cv_model")
ONNX_DIR = os.path.join(MODEL_DIR, "flora_cv_onnx")

print(f"Exporting model from {CV_DIR} to {ONNX_DIR}...")

# Load the model and export it to ONNX
model = ORTModelForImageClassification.from_pretrained(CV_DIR, export=True)
processor = AutoImageProcessor.from_pretrained(CV_DIR)

# Save the ONNX model and processor
model.save_pretrained(ONNX_DIR)
processor.save_pretrained(ONNX_DIR)

print("Export complete! ONNX model saved.")

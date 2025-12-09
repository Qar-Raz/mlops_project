import sys
import os
from unittest.mock import MagicMock

# 1. Mock heavy dependencies BEFORE importing the app
# This is crucial because the app imports them at the top level
sys.modules["llama_cpp"] = MagicMock()
sys.modules["optimum.onnxruntime"] = MagicMock()
sys.modules["transformers"] = MagicMock()
sys.modules["langchain_community.embeddings"] = MagicMock()
sys.modules["langchain_community.vectorstores"] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["onnxruntime"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["prometheus_client"] = MagicMock()
sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()
sys.modules["psutil"] = MagicMock()
sys.modules["better_profanity"] = MagicMock()

# 2. Add project root to sys.path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 3. Import the app
from backend.app import app, sys_comps  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# 4. Disable the startup event
# We don't want to try loading real models in the CI environment
app.router.on_startup = []

client = TestClient(app)


def test_app_initialization():
    """
    Basic smoke test to ensure the app object is created correctly.
    """
    assert app.title == "Flora-Bot API"


def test_chat_endpoint():
    """
    Test the /chat endpoint with mocked LLM.
    """
    # Setup the mock LLM
    mock_llm = MagicMock()
    # The app calls llm(prompt, ...) and expects a dict with choices
    mock_llm.return_value = {"choices": [{"text": " This is a mocked response."}]}

    # Inject the mock into sys_comps
    sys_comps["llm"] = mock_llm

    payload = {
        "question": "What is this?",
        "context": "Some context about plants.",
        "diagnosis": "Healthy",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "This is a mocked response."

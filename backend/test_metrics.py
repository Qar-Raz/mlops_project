"""
Test script to verify Prometheus metrics are being collected
Run this after starting the Docker containers
"""
import requests
import time

API_URL = "http://localhost:8000"
METRICS_URL = f"{API_URL}/metrics"

def test_metrics_endpoint():
    """Test that the /metrics endpoint is accessible"""
    print("Testing /metrics endpoint...")
    response = requests.get(METRICS_URL)
    assert response.status_code == 200, "Metrics endpoint not accessible"
    print("✅ Metrics endpoint is accessible\n")
    return response.text

def check_custom_metrics(metrics_text):
    """Check if our custom metrics are present"""
    print("Checking for custom LLM metrics...")
    
    required_metrics = [
        "llm_request_duration_seconds",
        "llm_tokens_total",
        "llm_estimated_cost_total_usd",
        "rag_retrieval_duration_seconds",
        "rag_documents_retrieved",
        "guardrail_violations_total",
        "active_llm_requests",
    ]
    
    found_metrics = []
    missing_metrics = []
    
    for metric in required_metrics:
        if metric in metrics_text:
            found_metrics.append(metric)
            print(f"✅ Found: {metric}")
        else:
            missing_metrics.append(metric)
            print(f"❌ Missing: {metric}")
    
    print(f"\nFound {len(found_metrics)}/{len(required_metrics)} custom metrics")
    return len(missing_metrics) == 0

def simulate_requests():
    """Simulate some API requests to generate metrics"""
    print("\n🔄 Simulating API requests to generate metrics...")
    
    # Test chat endpoint
    chat_payload = {
        "question": "How do I treat tomato blight?",
        "context": "Tomato early blight causes dark spots on leaves.",
        "diagnosis": "Tomato___Early_blight"
    }
    
    try:
        response = requests.post(f"{API_URL}/chat", json=chat_payload)
        if response.status_code == 200:
            print("✅ Chat request successful")
        else:
            print(f"⚠️ Chat request returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Chat request failed: {e}")
    
    time.sleep(2)  # Wait for metrics to be collected

def main():
    print("=" * 60)
    print("LLM Metrics Testing Script")
    print("=" * 60 + "\n")
    
    try:
        # Test metrics endpoint
        metrics_text = test_metrics_endpoint()
        
        # Check for custom metrics
        all_present = check_custom_metrics(metrics_text)
        
        if not all_present:
            print("\n⚠️ Some metrics are missing. This is normal if no requests have been made yet.")
            print("Simulating requests...\n")
            simulate_requests()
            
            # Check again after simulation
            metrics_text = test_metrics_endpoint()
            check_custom_metrics(metrics_text)
        
        print("\n" + "=" * 60)
        print("📊 Access your dashboards at:")
        print("   Prometheus: http://localhost:9090")
        print("   Grafana:    http://localhost:3000 (admin/admin)")
        print("   Metrics:    http://localhost:8000/metrics")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Docker containers are running:")
        print("   docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
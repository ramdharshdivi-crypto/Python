"""Quick test script to verify server is working."""
import requests
import json

def test_health():
    """Test health endpoint."""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print("✅ Health check:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_agents():
    """Test agents endpoint."""
    try:
        response = requests.get('http://localhost:8000/agents', timeout=5)
        print("\n✅ Agents list:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Agents list failed: {e}")
        return False

def test_query():
    """Test query endpoint."""
    try:
        response = requests.post(
            'http://localhost:8000/query',
            json={'query': 'hello'},
            timeout=10
        )
        print("\n✅ Query test:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing Agent Hub Platform Backend...\n")
    print("="*50)
    
    success = True
    success &= test_health()
    success &= test_agents()
    success &= test_query()
    
    print("\n" + "="*50)
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check output above.")

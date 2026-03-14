"""
Script simples para testar o login no backend
"""
import requests
import json

def test_login():
    url = "http://192.168.130.10:8000/api/v1/auth/login"
    
    payload = {
        "email": "admin@pcm.local",
        "password": "Admin@123456"
    }
    
    print("="*70)
    print("TESTANDO LOGIN NO BACKEND")
    print("="*70)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-"*70)
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-"*70)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User: {data.get('user', {})}")
        else:
            print("❌ LOGIN FAILED!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Backend não está respondendo!")
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: {e}")
        print("Backend demorou muito para responder!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("="*70)

if __name__ == "__main__":
    test_login()

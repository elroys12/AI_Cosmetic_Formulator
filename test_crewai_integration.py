import httpx
import asyncio
from datetime import datetime


async def test_ml_service_crewai():
    """Test ML service dengan CrewAI"""
    ml_url = "https://novel-chemical-ml-production.up.railway.app"
    api_key = "novel_chem_ml_202501_Ef9GhIjKlMnOpQrStUvWxYz0123456789AbCdEfGhIjKlMnOp"
    
    print(f"🔍 Testing CrewAI ML Service at: {ml_url}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            # Test 1: Health check
            print("🧪 Test 1: Health check...")
            response = await client.get(f"{ml_url}/health")
            
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Health: {response.status_code}")
                print(f"   CrewAI: {health.get('crewai_enabled')}")
                print(f"   Agents: {health.get('agents')}")
                print(f"   Data files: {health.get('data_files')}")
            else:
                print(f"❌ Health failed: {response.status_code}")
                return False
            
            # Test 2: Analyze dengan CrewAI
            print("\n🧪 Test 2: CrewAI /analyze...")
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            
            analyze_data = {
                "topic": "Buatkan serum anti-aging untuk kulit sensitif"
            }
            
            response = await client.post(
                f"{ml_url}/analyze",
                json=analyze_data,
                headers=headers,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Analyze successful: {response.status_code}")
                print(f"   Success: {result.get('success')}")
                print(f"   Processing time: {result.get('processing_time')}s")
                print(f"   Result preview: {result.get('result')[:200]}...")
            else:
                print(f"❌ Analyze failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
            
            # Test 3: Structured /predict
            print("\n🧪 Test 3: Structured /predict...")
            response = await client.post(
                f"{ml_url}/predict",
                json=analyze_data,
                headers=headers,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Predict successful: {response.status_code}")
                print(f"   Data keys: {list(result.get('data', {}).keys())}")
                print(f"   Compound: {result.get('data', {}).get('nama_senyawa')}")
            else:
                print(f"❌ Predict failed: {response.status_code}")
            
            return True
            
    except httpx.TimeoutException:
        print("❌ Timeout - CrewAI needs 1-3 minutes")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_backend_with_crewai():
    """Test backend integration dengan CrewAI ML"""
    backend_url = "https://novel-chemicals-backend-production.up.railway.app"
    
    print(f"\n🔍 Testing Backend Integration at: {backend_url}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=200) as client:
            # Register
            print("🧪 Test 1: User registration...")
            register_data = {
                "email": f"crewai_{datetime.now().strftime('%H%M%S')}@example.com",
                "password": "TestPass123!",
                "full_name": "CrewAI Test User"
            }
            
            response = await client.post(
                f"{backend_url}/api/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ Registered: {token_data['user_id']}")
                
                # Analyze with CrewAI
                print("\n🧪 Test 2: Analyze with CrewAI backend...")
                analyze_data = {
                    "prompt": "Rekomendasi moisturizer untuk kulit kering"
                }
                
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.post(
                    f"{backend_url}/api/analyze",
                    json=analyze_data,
                    headers=headers,
                    timeout=200
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Analysis successful!")
                    print(f"   History ID: {result.get('history_id')}")
                    print(f"   Processing time: {result.get('processing_time')}s")
                    
                    data = result.get('data', {})
                    print(f"   Compound: {data.get('nama_senyawa')}")
                    print(f"   Formula: {data.get('formula')}")
                    
                    return True
                else:
                    print(f"❌ Analysis failed: {response.status_code}")
                    print(f"   Error: {response.text[:300]}")
                    return False
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    print("🚀 CREWAI INTEGRATION TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test ML Service
    ml_ok = await test_ml_service_crewai()
    
    if ml_ok:
        print("\n✅ ML Service (CrewAI) is working!")
        
        # Test Backend Integration
        backend_ok = await test_backend_with_crewai()
        
        if backend_ok:
            print("\n🎉 FULL INTEGRATION SUCCESS!")
            print("Backend + CrewAI ML Service working perfectly.")
        else:
            print("\n⚠️ Backend integration issues")
    else:
        print("\n❌ ML Service issues - fix before testing backend")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
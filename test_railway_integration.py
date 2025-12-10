import httpx
import asyncio
import json
from datetime import datetime


async def test_backend_railway():
    """Test backend deployed on Railway"""
    backend_url = "https://novel-chemicals-backend-production.up.railway.app"
    
    print(f"🔍 Testing Backend at: {backend_url}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test 1: Root endpoint
            print("🧪 Test 1: Root endpoint...")
            response = await client.get(f"{backend_url}/")
            if response.status_code == 200:
                print(f"✅ Backend root: {response.status_code}")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Backend root failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
            
            # Test 2: Health check
            print("\n🧪 Test 2: Health check...")
            response = await client.get(f"{backend_url}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Backend health: {response.status_code}")
                print(f"   Service: {health_data.get('service')}")
                print(f"   Status: {health_data.get('status')}")
            else:
                print(f"❌ Backend health failed: {response.status_code}")
                return False
            
            # Test 3: ML Service status
            print("\n🧪 Test 3: ML Service status...")
            response = await client.get(f"{backend_url}/api/analyze/ml-status")
            if response.status_code == 200:
                ml_status = response.json()
                print(f"✅ ML Status: {response.status_code}")
                print(f"   ML Service: {ml_status.get('ml_service')}")
                print(f"   URL: {ml_status.get('url')}")
                print(f"   Status: {ml_status.get('status')}")
            else:
                print(f"⚠️  ML Status failed: {response.status_code}")
                print(f"   This might be okay if ML service is not accessible")
            
            # Test 4: Register user
            print("\n🧪 Test 4: User registration...")
            register_data = {
                "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
                "password": "TestPass123!",
                "full_name": "Railway Test User"
            }
            
            response = await client.post(
                f"{backend_url}/api/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                token_data = response.json()
                access_token = token_data["access_token"]
                user_id = token_data["user_id"]
                print(f"✅ User registered: {response.status_code}")
                print(f"   User ID: {user_id}")
                print(f"   Token: {access_token[:50]}...")
                
                # Test 5: Analyze with AI
                print("\n🧪 Test 5: AI Analysis...")
                analyze_data = {
                    "prompt": "Buatkan serum anti-aging untuk kulit sensitif"
                }
                
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.post(
                    f"{backend_url}/api/analyze",
                    json=analyze_data,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Analysis successful: {response.status_code}")
                    print(f"   Success: {result.get('success')}")
                    print(f"   History ID: {result.get('history_id')}")
                    print(f"   Processing time: {result.get('processing_time')}")
                    
                    if "data" in result:
                        data = result["data"]
                        print(f"   Compound: {data.get('nama_senyawa')}")
                        print(f"   Formula: {data.get('formula')}")
                        
                    return True
                else:
                    print(f"❌ Analysis failed: {response.status_code}")
                    print(f"   Error: {response.text[:200]}")
                    return False
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Backend timeout - service may be slow or down")
        return False
    except httpx.RequestError as e:
        print(f"❌ Backend connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_ml_service_railway():
    """Test ML service deployed on Railway"""
    ml_url = "https://novel-chemical-ml-production.up.railway.app"
    api_key = "novel_chem_ml_202501_Ef9GhIjKlMnOpQrStUvWxYz0123456789AbCdEfGhIjKlMnOp"
    
    print(f"\n🔍 Testing ML Service at: {ml_url}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test 1: Health check
            print("🧪 Test 1: ML Service health...")
            response = await client.get(f"{ml_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ ML Service health: {response.status_code}")
                print(f"   Service: {health_data.get('service')}")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Gemini configured: {health_data.get('gemini_configured')}")
            else:
                print(f"❌ ML Service health failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
            
            # Test 2: Predict endpoint
            print("\n🧪 Test 2: Predict endpoint...")
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            
            predict_data = {
                "prompt": "Buatkan formula moisturizer untuk kulit kering"
            }
            
            response = await client.post(
                f"{ml_url}/predict",
                json=predict_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Predict successful: {response.status_code}")
                print(f"   Success: {result.get('success')}")
                print(f"   Processing time: {result.get('processing_time')}")
                
                if "data" in result:
                    data = result["data"]
                    print(f"   Compound: {data.get('nama_senyawa')}")
                    print(f"   Formula: {data.get('formula')}")
                
                return True
            else:
                print(f"❌ Predict failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("❌ ML Service timeout - AI processing may be slow")
        return False
    except httpx.RequestError as e:
        print(f"❌ ML Service connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def main():
    print("🚀 RAILWAY DEPLOYMENT INTEGRATION TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n📊 Testing both services deployed on Railway...")
    
    # Test ML Service first
    ml_ok = await test_ml_service_railway()
    
    if ml_ok:
        print("\n✅ ML Service is working on Railway!")
    else:
        print("\n❌ ML Service failed on Railway")
    
    # Test Backend
    backend_ok = await test_backend_railway()
    
    if backend_ok:
        print("\n✅ Backend is working on Railway!")
    else:
        print("\n❌ Backend failed on Railway")
    
    print("\n" + "=" * 60)
    print("📋 FINAL TEST SUMMARY:")
    print(f"  ML Service: {'✅ PASS' if ml_ok else '❌ FAIL'}")
    print(f"  Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"  Integration: {'✅ READY' if ml_ok and backend_ok else '⚠️ NEEDS FIXING'}")
    print("=" * 60)
    
    if ml_ok and backend_ok:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("Both services are working correctly on Railway.")
        print("\n✅ You can now use the API:")
        print(f"   Backend URL: https://novel-chemicals-backend-production.up.railway.app")
        print(f"   ML Service URL: https://novel-chemical-ml-production.up.railway.app")
        print("\n📚 API Documentation:")
        print(f"   Backend Docs: https://novel-chemicals-backend-production.up.railway.app/api/docs")
        print(f"   ML Service Docs: https://novel-chemical-ml-production.up.railway.app/docs")
    else:
        print("\n⚠️  DEPLOYMENT ISSUES DETECTED")
        print("Check the logs above for specific errors.")
        print("\nCommon solutions:")
        print("1. Check Railway variables are set correctly")
        print("2. Verify API keys are valid")
        print("3. Check that CSV files exist in ML service data/ folder")
        print("4. Restart services on Railway")


if __name__ == "__main__":
    asyncio.run(main())
"""
Test Backend Routes
Quick diagnostic untuk check available endpoints
"""

import httpx
import asyncio
from datetime import datetime


async def test_backend_routes():
    """Test semua kemungkinan route patterns"""
    backend_url = "https://novel-chemicals-backend-production.up.railway.app"
    
    print(f"🔍 TESTING BACKEND ROUTES")
    print(f"{'='*60}")
    print(f"Backend: {backend_url}")
    print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Test berbagai endpoint patterns
    test_routes = [
        # Root endpoints
        ("/", "GET", None, "Root endpoint"),
        ("/health", "GET", None, "Health without /api"),
        ("/api/health", "GET", None, "Health with /api"),
        
        # Docs
        ("/docs", "GET", None, "Swagger docs"),
        ("/api/docs", "GET", None, "Swagger with /api"),
        ("/redoc", "GET", None, "ReDoc"),
        
        # Auth endpoints (various patterns)
        ("/auth/register", "POST", {"email": "test@test.com", "password": "Test123!", "full_name": "Test"}, "Auth without /api"),
        ("/api/auth/register", "POST", {"email": "test@test.com", "password": "Test123!", "full_name": "Test"}, "Auth with /api"),
        ("/register", "POST", {"email": "test@test.com", "password": "Test123!", "full_name": "Test"}, "Direct register"),
        
        # Analyze endpoints
        ("/analyze", "GET", None, "Analyze without /api"),
        ("/api/analyze", "GET", None, "Analyze with /api"),
        ("/api/analyze/health", "GET", None, "Analyze health"),
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=10) as client:
        for route, method, body, description in test_routes:
            try:
                url = f"{backend_url}{route}"
                
                if method == "GET":
                    response = await client.get(url)
                else:  # POST
                    response = await client.post(
                        url, 
                        json=body,
                        headers={"Content-Type": "application/json"}
                    )
                
                status = response.status_code
                
                # Color code status
                if status == 200 or status == 201:
                    status_emoji = "✅"
                elif status == 404:
                    status_emoji = "❌"
                elif status == 422:
                    status_emoji = "⚠️"
                else:
                    status_emoji = "🔶"
                
                result = {
                    "route": route,
                    "method": method,
                    "status": status,
                    "description": description,
                    "emoji": status_emoji
                }
                
                results.append(result)
                
                print(f"{status_emoji} {status:3d} | {method:4s} | {route:30s} | {description}")
                
                # Show response preview untuk successful requests
                if status in [200, 201]:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            preview_keys = list(data.keys())[:3]
                            print(f"         Response keys: {preview_keys}")
                    except:
                        pass
                
            except httpx.ConnectError:
                print(f"🔴 FAIL | {method:4s} | {route:30s} | Connection failed")
                results.append({
                    "route": route,
                    "method": method,
                    "status": "CONN_ERROR",
                    "description": description,
                    "emoji": "🔴"
                })
            except Exception as e:
                print(f"🔴 ERR  | {method:4s} | {route:30s} | {str(e)[:30]}")
                results.append({
                    "route": route,
                    "method": method,
                    "status": "ERROR",
                    "description": description,
                    "emoji": "🔴"
                })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    working_routes = [r for r in results if r["status"] in [200, 201]]
    not_found = [r for r in results if r["status"] == 404]
    validation_errors = [r for r in results if r["status"] == 422]
    
    print(f"✅ Working routes: {len(working_routes)}")
    for r in working_routes:
        print(f"   {r['method']:4s} {r['route']}")
    
    print(f"\n❌ Not found (404): {len(not_found)}")
    for r in not_found:
        print(f"   {r['method']:4s} {r['route']}")
    
    print(f"\n⚠️  Validation errors (422): {len(validation_errors)}")
    for r in validation_errors:
        print(f"   {r['method']:4s} {r['route']}")
    
    # Diagnosis
    print(f"\n{'='*60}")
    print("🔧 DIAGNOSIS")
    print(f"{'='*60}")
    
    if len(working_routes) == 0:
        print("❌ CRITICAL: No working routes found!")
        print("   Possible causes:")
        print("   1. Backend deployment failed")
        print("   2. Server not running")
        print("   3. Railway environment issues")
    elif "/" in [r["route"] for r in working_routes]:
        print("✅ Backend is running (root endpoint works)")
        
        if not any(r["route"].startswith("/api/auth") for r in working_routes):
            print("❌ ISSUE: /api/auth routes not found")
            print("   Check:")
            print("   1. Router registration in main.py")
            print("   2. app.include_router(auth.router, prefix='/api')")
            print("   3. Railway deployment logs")
        else:
            print("✅ API routes are properly configured")
    
    print(f"\n{'='*60}")
    
    return results


async def test_openapi_spec():
    """Check OpenAPI specification"""
    backend_url = "https://novel-chemicals-backend-production.up.railway.app"
    
    print(f"\n🔍 CHECKING OPENAPI SPEC")
    print(f"{'='*60}")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Try to get OpenAPI JSON
            response = await client.get(f"{backend_url}/openapi.json")
            
            if response.status_code == 200:
                spec = response.json()
                paths = spec.get("paths", {})
                
                print(f"✅ OpenAPI spec accessible")
                print(f"📋 Available paths ({len(paths)}):")
                
                for path in sorted(paths.keys()):
                    methods = list(paths[path].keys())
                    print(f"   {path:40s} {methods}")
                
                return paths
            else:
                print(f"❌ OpenAPI spec not found: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Error getting OpenAPI spec: {e}")
        return None


async def main():
    # Test routes
    results = await test_backend_routes()
    
    # Test OpenAPI
    paths = await test_openapi_spec()
    
    # Final recommendation
    print(f"\n{'='*60}")
    print("💡 RECOMMENDATION")
    print(f"{'='*60}")
    
    working_routes = [r for r in results if r["status"] in [200, 201]]
    
    if len(working_routes) > 0:
        print("✅ Backend is partially working")
        print("\nNext steps:")
        print("1. Check Railway deployment logs:")
        print("   railway logs --service novel-chemicals-backend-production")
        print("\n2. Verify main.py router registration:")
        print("   app.include_router(auth.router)")
        print("\n3. Check if routers have correct prefixes:")
        print("   router = APIRouter(prefix='/api/auth', tags=['Authentication'])")
    else:
        print("❌ Backend appears to be completely down")
        print("\nUrgent actions:")
        print("1. Check Railway deployment status")
        print("2. View deployment logs")
        print("3. Restart the service")
        print("\nRailway commands:")
        print("   railway status")
        print("   railway logs")
        print("   railway up")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
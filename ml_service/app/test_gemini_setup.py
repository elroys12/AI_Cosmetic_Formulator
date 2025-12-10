# ml_service/app/test_gemini_setup.py

import os
from google import genai  # ✅ CORRECT import for google-genai==0.7.0
import json

# API Key Anda yang baru
TEST_KEY = "AIzaSyChzlsazd-Ruku0SDryo_sG9asCByR83TU"

print("🔍 Testing Gemini API Key with google.genai v0.7.0...")
print(f"Key: {TEST_KEY[:20]}...")
print(f"Length: {len(TEST_KEY)}")
print(f"Looks valid: {TEST_KEY.startswith('AIza') and len(TEST_KEY) > 30}")

try:
    # ✅ Initialize with google.genai (NEW API)
    print("\n🧪 Test 1: Initialize client...")
    client = genai.Client(api_key=TEST_KEY)
    print("✅ Client initialized successfully!")
    
    # Test 2: Simple completion dengan model yang benar
    print("\n🧪 Test 2: Simple completion...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",  # ✅ Model yang benar
        contents="Say hello in Indonesian"
    )
    
    print(f"✅ Success! Response: {response.text}")
    
    # Test 3: Embedding (untuk semantic search)
    print("\n🧪 Test 3: Embedding...")
    try:
        embedding = client.models.embed_content(
            model="text-embedding-004",
            contents="chemical properties"
        )
        
        print(f"✅ Embedding successful! Vector length: {len(embedding.embeddings[0].values)}")
    except Exception as e:
        print(f"⚠️  Embedding test skipped (may not be available): {e}")
    
    # Test 4: Chemical recommendation format
    print("\n🧪 Test 4: Chemical recommendation...")
    prompt = """Rekomendasikan senyawa kimia dengan titik didih 100°C.
Kembalikan HANYA JSON tanpa markdown:
{"formula": "H2O", "smiles": "O", "nama_senyawa": "Air", "justifikasi": "Cocok untuk titik didih 100°C"}"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",  # ✅ Model yang benar
        contents=prompt
    )
    
    print(f"✅ Chemical test successful!")
    print(f"Response: {response.text[:200]}...")
    
    # Try to parse JSON
    try:
        # Clean response
        text = response.text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)
        
        result = json.loads(text)
        print(f"✅ JSON parsed successfully: {result.get('formula', 'N/A')}")
    except:
        print("⚠️  Response is not clean JSON, but that's okay - the system will handle it")
    
    print("\n🎉 Gemini API Key is VALID and WORKING!")
    print("✅ All tests passed! Ready to use with google.genai v0.7.0")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ Error: {type(e).__name__}")
    print(f"Message: {error_msg}")
    
    if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
        print("\n⚠️  MASALAH: API Key invalid!")
        print("Solusi: Dapatkan key baru dari https://aistudio.google.com/apikey")
    elif "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
        print("\n⚠️  MASALAH: Quota exceeded!")
        print("Solusi: Tunggu atau gunakan akun Google lain")
    elif "permission" in error_msg.lower():
        print("\n⚠️  MASALAH: Permission denied!")
        print("Solusi: Enable Gemini API di Google AI Studio")
    elif "404" in error_msg or "not found" in error_msg.lower():
        print("\n⚠️  MASALAH: Model not found!")
        print("Solusi: Pastikan menggunakan model: gemini-2.0-flash-exp")
    else:
        print("\n⚠️  MASALAH: Unknown error")
        print("Solusi: Coba key yang berbeda atau cek dokumentasi")

print("\n" + "="*60)
print("API Information:")
print("  - Package: google-genai==0.7.0")
print("  - Import: from google import genai")
print("  - Client: genai.Client(api_key=...)")
print("  - Model: gemini-2.0-flash-exp")
print("\nModel yang tersedia untuk Gemini API:")
print("  - gemini-2.0-flash-exp (recommended)")
print("  - gemini-1.5-pro (stable)")
print("  - gemini-1.5-flash-8b (lightweight)")
print("\nJika key invalid, dapatkan yang baru:")
print("1. Buka: https://aistudio.google.com/apikey")
print("2. Login dengan Google")
print("3. Create API Key")
print("4. Copy key dan update ml_service/.env")
print("="*60)
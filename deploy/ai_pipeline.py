# ai_pipeline.py
import os
import ast
import time
from typing import Any, Dict

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

from google import genai
from google.genai.errors import ClientError

# =========================
# LOAD YOUR REAL DATA
# =========================
DATA_DIR = os.environ.get("DATA_DIR", "data")
CHEM_PATH = os.path.join(DATA_DIR, "chemicals_with_embeddings.csv")
PROD_PATH = os.path.join(DATA_DIR, "products_with_embeddings.csv")
REL_PATH = os.path.join(DATA_DIR, "relations_with_embeddings.csv")

# =========================
# API KEY & CLIENT GEMINI
# =========================
REAL_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not REAL_KEY:
    raise ValueError("GEMINI_API_KEY / GOOGLE_API_KEY belum diset di environment!")

client = genai.Client(api_key=REAL_KEY)
EMBED_MODEL = "text-embedding-004"

# =========================
# HELPERS: LOAD DATA
# =========================
def parse_embedding(val):
    """Parse kolom embedding dari string -> list[float]."""
    if pd.isna(val):
        return None
    if isinstance(val, (list, tuple)):
        return list(map(float, val))
    try:
        parsed = ast.literal_eval(str(val))
        return list(map(float, parsed))
    except Exception:
        return None


def load_df(path: str, name: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File data '{name}' tidak ditemukan di path: {path}")

    df = pd.read_csv(path)
    if "embedding" not in df.columns:
        raise ValueError(f"File '{name}' tidak punya kolom 'embedding'.")

    df["embedding"] = df["embedding"].apply(parse_embedding)
    before = len(df)
    df = df.dropna(subset=["embedding"])
    after = len(df)
    print(f"[ai_pipeline] {name} ready: {after} rows (drop {before - after})")

    return df


# Load semua dataset
chemicals = load_df(CHEM_PATH, "chemicals")
products = load_df(PROD_PATH, "products")
relations = load_df(REL_PATH, "relations")

# Mapping ID -> nama buat output lebih manusiawi
compound_id_to_name = dict(
    zip(chemicals["compound_id"].astype(str), chemicals["compound_name"].astype(str))
)
product_id_to_name = dict(
    zip(products["product_id"].astype(str), products["product_name"].astype(str))
)


def pretty_compound(cid: str) -> str:
    nm = compound_id_to_name.get(str(cid))
    return f"{cid} ({nm})" if nm and nm.lower() != "nan" else str(cid)


def pretty_product(pid: str) -> str:
    nm = product_id_to_name.get(str(pid))
    return f"{pid} ({nm})" if nm and nm.lower() != "nan" else str(pid)


# =========================
# EMBEDDING GEMINI
# =========================
def get_embedding(text: str):
    """Panggil Gemini embedding (text-embedding-004)."""
    res = client.models.embed_content(model=EMBED_MODEL, contents=text)
    return res.embeddings[0].values


# =========================
# SEMANTIC SEARCH (UMUM)
# =========================
def semantic_search(df: pd.DataFrame, query: str, top_k: int = 5) -> pd.DataFrame:
    """Hitung kemiripan cosine antara query & kolom embedding di df."""
    q_emb = get_embedding(query)

    df_temp = df.copy()
    df_temp["score"] = df_temp["embedding"].apply(
        lambda emb: cosine_similarity([q_emb], [emb])[0][0]
    )

    # Build kolom name_for_output & info_for_output sesuai tipe dataset
    if "compound_name" in df_temp.columns:
        # chemicals
        df_temp["name_for_output"] = df_temp["compound_id"]
        info_cols = [
            "compound_name",
            "molecular_formula",
            "molecular_weight",
            "logP",
            "solubility",
            "toxicity_score",
            "safety_class",
        ]
        df_temp["info_for_output"] = (
            df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    elif "product_name" in df_temp.columns:
        # products
        df_temp["name_for_output"] = df_temp["product_id"]
        info_cols = [
            "product_name",
            "category",
            "target_skin_type",
            "key_ingredients",
            "effectiveness_score",
            "safety_score",
            "popularity_index",
            "description",
        ]
        df_temp["info_for_output"] = (
            df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    elif "relation_id" in df_temp.columns:
        # relations
        df_temp["name_for_output"] = df_temp["relation_id"]
        info_cols = [
            "product_id",
            "compound_id",
            "percentage_in_formula",
            "role_in_product",
            "synergy_score",
            "interaction_type",
            "potential_new_compound",
        ]
        df_temp["info_for_output"] = (
            df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    # Sort & ambil top_k
    df_temp = df_temp.sort_values("score", ascending=False).head(top_k)

    # Standarkan kolom untuk dikembalikan
    result = df_temp[["name_for_output", "info_for_output", "score"]].rename(
        columns={
            "name_for_output": "name",
            "info_for_output": "info",
        }
    )
    return result.reset_index(drop=True)


# =========================
# CREWAI TOOLS
# =========================
def generate_real_response(topic: str) -> Dict:
    """Generate response using REAL data from YOUR CSV"""
    print(f"\n🔍 Processing: {topic}")
    print(f"📊 Using REAL data from {len(chemicals_df)} compounds")
    
    start_time = time.time()
    
    # Get main compound
    main_compound = get_real_compound(topic)
    
    if not main_compound:
        # Fallback jika tidak dapat compound
        return {
            "success": False,
            "message": "No compounds found in database",
            "processing_time": 0.1
        }
    
    # Get alternatives
    alternatives = get_alternatives(main_compound["compound_id"], 2)
    
    # Calculate properties untuk sifat_kimia
    properties = {
        "reactivity_score": main_compound.get("reactivity_score"),
        "toxicity_level": main_compound.get("toxicity_level"),
        "solubility": main_compound.get("solubility", ""),
        "stability_index": main_compound.get("stability_index"),
        "skin_absorption_rate": main_compound.get("skin_absorption_rate"),
        "ph_value": main_compound.get("ph_value"),
        "function": main_compound.get("function", ""),
        "origin": main_compound.get("origin", "")
    }
    
    # Clean None values
    properties = {k: v for k, v in properties.items() if v is not None and v != ""}
    
    # Build justifikasi berdasarkan data
    compound_name = main_compound["compound_name"]
    function = main_compound.get("function", "cosmetic ingredient")
    origin = main_compound.get("origin", "synthetic")
    
    justifikasi_text = f"{compound_name} adalah bahan {function.lower()} yang berasal dari {origin}. "
    
    if main_compound.get("toxicity_level"):
        tox_level = main_compound["toxicity_level"]
        if tox_level < 0.3:
            justifikasi_text += "Memiliki toksisitas rendah. "
        elif tox_level < 0.6:
            justifikasi_text += "Memiliki toksisitas sedang. "
        else:
            justifikasi_text += "Perlu perhatian khusus pada toksisitas. "
    
    if main_compound.get("stability_index"):
        stability = main_compound["stability_index"]
        if stability > 0.7:
            justifikasi_text += "Stabilitas tinggi. "
        elif stability > 0.4:
            justifikasi_text += "Stabilitas sedang. "
        else:
            justifikasi_text += "Perlu stabilizer. "
    
    # Build description dari text jika ada
    description = main_compound.get("text", f"{compound_name} adalah bahan {function}.")
    
    processing_time = time.time() - start_time
    
    # Build final response
    response = {
        "success": True,
        "data": {
            "formula": main_compound["molecular_formula"],
            "smiles": "",  # ✅ Main compound SMILES (empty for now, add if available)
            "nama_senyawa": compound_name,
            "sifat_kimia": properties,
            "justifikasi": justifikasi_text,
            "description": description[:500] + "..." if len(description) > 500 else description,
            "usage_guidelines": f"Gunakan sesuai formulasi kosmetik. pH optimal: {main_compound.get('ph_value', '6.0-7.0')}.",
            "dosage": "Konsentrasi rekomendasi: 0.5-5%.",
            "safety_notes": f"Skor toksisitas: {main_compound.get('toxicity_level', 'N/A')}. {'Aman untuk penggunaan topikal.' if main_compound.get('toxicity_level', 1) < 0.6 else 'Perlu pengujian keamanan lebih lanjut.'}",
            "contraindications": [
                "Hipersensitif terhadap bahan",
                "Kulit dengan luka terbuka"
            ],
            "recommendations": alternatives,  # ✅ Now with correct format
            "confidence_score": 0.9,
            "sources": ["Internal Cosmetic Database"],
            "_metadata": {
                "source": "real_csv_data",
                "compound_id": main_compound["compound_id"],
                "total_compounds_in_db": len(chemicals_df),
                "data_loaded": True,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        },
        "processing_time": round(processing_time, 2),
        "message": f"Analysis completed using {len(chemicals_df)} real compounds from database"
    }
    
    print(f"✅ Generated response for: {compound_name}")
    print(f"   Compound ID: {main_compound['compound_id']}")
    print(f"   Function: {function}")
    print(f"   Alternatives: {len(alternatives)}")
    print(f"   Processing time: {processing_time:.2f}s")
    
    return response

# =========================
# MAIN ENTRY POINT
# =========================
def run_ai(topic: str) -> Dict:
    """
    ENTRY POINT untuk FastAPI
    Menggunakan data REAL dari CSV Anda
    """
    print(f"\n{'='*60}")
    print(f"🎯 PROCESSING REQUEST")
    print(f"   Topic: {topic}")
    print(f"   Database size: {len(chemicals_df)} compounds")
    print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    # Generate response menggunakan data real
    response = generate_real_response(topic)
    
    print(f"\n✅ PROCESSING COMPLETE")
    print(f"   Success: {response.get('success')}")
    print(f"   Compound: {response.get('data', {}).get('nama_senyawa')}")
    print(f"   Source: {response.get('data', {}).get('_metadata', {}).get('source')}")
    print(f"{'='*60}")
    
    return response

@tool("search_product_tool")
def search_product_tool(query: str, top_k: int = 5) -> str:
    """
    Cari & ranking produk relevan dari dataset products.
    Input: query teks + top_k
    Output: JSON string list hasil (id, info, score, name_display).
    """
    result = semantic_search(products, query, top_k)
    result["name_display"] = result["name"].apply(pretty_product)
    return result.to_json(orient="records")


@tool("check_innovation_tool")
def check_innovation_tool(compound_id1: str, compound_id2: str) -> str:
    """
    Cek interaksi/sinergi/inovasi antar compound dari dataset relations.
    Input: 2 compound_id
    Output: JSON string record relasi kalau ada, atau pesan string kalau tidak ada.
    """
    df_filtered = relations[
        (
            (relations["compound_id"] == compound_id1)
            & relations["potential_new_compound"]
            .astype(str)
            .str.contains(compound_id2, na=False)
        )
        | (
            (relations["compound_id"] == compound_id2)
            & relations["potential_new_compound"]
            .astype(str)
            .str.contains(compound_id1, na=False)
        )
    ]

    if df_filtered.empty:
        return (
            f"Tidak ada catatan inovasi/interaksi antara "
            f"{compound_id1} dan {compound_id2}."
        )
    return df_filtered.to_json(orient="records")


# =========================
# LLM + AGENTS + TASKS + CREW
# =========================
llm = LLM(model="gemini/gemini-2.5-flash", api_key=REAL_KEY)

data_agent = Agent(
    role="Data Analyst Agent",
    goal="Mencari bahan kimia dan produk skincare yang paling relevan dari database.",
    backstory="Seorang analis data yang ahli membaca database bahan & produk kosmetik.",
    verbose=False,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool],
    llm=llm,
)

chemical_agent = Agent(
    role="Chemical Safety Agent",
    goal="Mengevaluasi keamanan, interaksi, dan potensi inovasi bahan-bahan skincare.",
    backstory=(
        "Ahli kimia kosmetik yang fokus pada keamanan kulit, interaksi bahan, "
        "dan regulasi skincare modern."
    ),
    verbose=False,
    allow_delegation=False,
    tools=[check_innovation_tool],
    llm=llm,
)

analysis_agent = Agent(
    role="Skincare Formulation Expert",
    goal=(
        "Menggabungkan data bahan, produk, dan keamanan menjadi rekomendasi formulasi "
        "skincare yang jelas, aman, dan mudah dipahami user."
    ),
    backstory=(
        "Formulator skincare berpengalaman yang mengerti kebutuhan kulit, tren produk, "
        "dan regulasi keamanan."
    ),
    verbose=False,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool, check_innovation_tool],
    llm=llm,
)

data_task = Task(
    description=(
        "Analisis permintaan user: '{topic}'. "
        "1) Identifikasi kebutuhan kulit & tujuan utama (misalnya: mencerahkan, anti-aging, acne). "
        "2) Gunakan tools untuk mencari bahan kimia dan produk yang relevan dari database. "
        "3) Kembalikan daftar bahan & produk paling relevan sebagai dasar analisis berikutnya."
    ),
    expected_output=(
        "Daftar terstruktur berisi bahan & produk relevan beserta ringkasan alasan pemilihan."
    ),
    agent=data_agent,
)

chemical_task = Task(
    description=(
        "Berdasarkan daftar bahan & produk dari Data Analyst Agent, "
        "evaluasi aspek keamanan, potensi iritasi, dan interaksi antar bahan. "
        "Gunakan 'check_innovation_tool' untuk melihat potensi sinergi/inovasi. "
        "Highlight bahan yang perlu dihindari untuk kulit sensitif atau kondisi tertentu."
    ),
    expected_output=(
        "Analisis keamanan & interaksi bahan, termasuk catatan bahan yang berisiko "
        "dan kombinasi yang sangat baik."
    ),
    agent=chemical_agent,
    context=[data_task],
)

final_task = Task(
    description=(
        "Gabungkan hasil dari Data Analyst Agent dan Chemical Safety Agent. "
        "Susun rekomendasi skincare yang jelas untuk user berdasarkan '{topic}', "
        "termasuk:\n"
        "- Bahan yang direkomendasikan\n"
        "- Bahan yang sebaiknya dihindari\n"
        "- Contoh susunan produk (basic routine) jika diperlukan\n"
        "Tulis dengan bahasa Indonesia yang ramah dan mudah dimengerti."
    ),
    expected_output="Rekomendasi final formulasi dan/atau routine skincare yang ringkas dan actionable.",
    agent=analysis_agent,
    context=[data_task, chemical_task],
)

crew = Crew(
    agents=[data_agent, chemical_agent, analysis_agent],
    tasks=[data_task, chemical_task, final_task],
    process=Process.sequential,
    verbose=False,
)


# =========================
# SAFE KICKOFF (RETRY)
# =========================
def safe_kickoff(inputs: Dict[str, Any], max_retries: int = 3, base_delay: float = 1.0):
    """
    Jalankan crew.kickoff dengan retry kalau kena rate limit / error tertentu.
    """
    delay = base_delay
    last_err: Exception | None = None

    for _ in range(max_retries):
        try:
            return crew.kickoff(inputs=inputs)
        except ClientError as e:
            last_err = e
            msg = str(e).lower()
            if "rate" in msg or "429" in msg:
                print(f"[ai_pipeline] Rate limited, retry dalam {delay} detik...")
                time.sleep(delay)
                delay *= 2
                continue
            # bukan rate-limit -> lempar langsung
            raise
        except Exception as e:
            # fallback umum (optional: bisa juga di-retry)
            raise e

    raise RuntimeError(f"Masih kena rate limit. Error terakhir: {last_err}")


# =========================
# ENTRY POINT UNTUK FASTAPI
# =========================
def run_ai(topic: str):
    """
    ENTRY POINT untuk FastAPI / backend.
    Input: pertanyaan user (topic)
    Output: hasil crew.kickoff (bisa langsung di-return ke API)
    """
    return safe_kickoff({"topic": topic})

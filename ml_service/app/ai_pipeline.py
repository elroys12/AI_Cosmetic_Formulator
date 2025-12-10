# ai_pipeline.py
import os
import ast
import time
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from google import genai
from google.genai.errors import ClientError


# =========================================================
# CONFIG PATH
# =========================================================
DATA_DIR = os.environ.get("DATA_DIR", "data")
CHEM_PATH = os.path.join(DATA_DIR, "chemicals_with_embeddings.csv")
PROD_PATH = os.path.join(DATA_DIR, "products_with_embeddings.csv")
REL_PATH  = os.path.join(DATA_DIR, "relations_with_embeddings.csv")


# =========================================================
# Setup API Key + Embedding Client
# =========================================================
REAL_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not REAL_KEY:
    raise ValueError("ENV GEMINI_API_KEY / GOOGLE_API_KEY belum diset!")

os.environ["GEMINI_API_KEY"] = REAL_KEY
os.environ["GOOGLE_API_KEY"] = REAL_KEY

client = genai.Client(api_key=REAL_KEY)
EMBED_MODEL = "text-embedding-004"


def get_embedding(text: str):
    """Ambil embedding dari Gemini"""
    try:
        res = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
        )
        return res.embeddings[0].values
    except Exception as e:
        return {"error": str(e)}


# =========================================================
# Load Dataset (Tahan CSV rusak) + Parse Embedding
# =========================================================
def safe_literal_eval(x):
    """Aman nge-parse '[0.1, 0.2,...]' jadi list float"""
    if not isinstance(x, str):
        return x
    try:
        return ast.literal_eval(x)
    except:
        return None


def load_csv_safe(path: str, tolerant=False):
    """
    tolerant=True -> parser python + skip bad lines
    buat relations yg sering ada kutip kebuka
    """
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame()
    
    try:
        if tolerant:
            return pd.read_csv(path, engine="python", on_bad_lines="skip")
        return pd.read_csv(path)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return pd.DataFrame()


print("[ai_pipeline] Loading datasets...")
chemicals = load_csv_safe(CHEM_PATH)
products  = load_csv_safe(PROD_PATH)
relations = load_csv_safe(REL_PATH, tolerant=True)

for name, df in [("chemicals", chemicals), ("products", products), ("relations", relations)]:
    if df.empty:
        print(f"[ai_pipeline] {name}: EMPTY or not found")
        continue
        
    if "embedding" in df.columns and len(df) > 0:
        if isinstance(df["embedding"].iloc[0], str):
            df["embedding"] = df["embedding"].apply(safe_literal_eval)

        before = len(df)
        df.dropna(subset=["embedding"], inplace=True)
        after = len(df)

        print(f"[ai_pipeline] {name} ready: {after} rows (dropped {before-after} bad emb)")
    else:
        print(f"[ai_pipeline] {name} ready: {len(df)} rows (no embedding col?)")


# =========================================================
# Mapping ID -> Nama
# =========================================================
compound_id_to_name = {}
product_id_to_name = {}

if not chemicals.empty and "compound_id" in chemicals.columns:
    compound_id_to_name = dict(zip(
        chemicals["compound_id"].astype(str),
        chemicals["compound_name"].astype(str)
    ))

if not products.empty and "product_id" in products.columns:
    product_id_to_name = dict(zip(
        products["product_id"].astype(str),
        products["product_name"].astype(str)
    ))

def pretty_compound(cid: str) -> str:
    cid = str(cid)
    nm = compound_id_to_name.get(cid)
    return f"{cid} ({nm})" if nm and nm != "nan" else cid

def pretty_product(pid: str) -> str:
    pid = str(pid)
    nm = product_id_to_name.get(pid)
    return f"{pid} ({nm})" if nm and nm != "nan" else pid


# =========================================================
# Semantic Search
# =========================================================
def semantic_search(df, query, top_k=5):
    if df.empty:
        return {"error": "DataFrame is empty"}
        
    q_emb_result = get_embedding(query)
    if isinstance(q_emb_result, dict) and "error" in q_emb_result:
        return {"error": q_emb_result["error"]}
    q_emb = q_emb_result

    if "embedding" not in df.columns or df["embedding"].isnull().all():
        return {"error": "DataFrame tidak punya embedding valid."}

    df_temp = df.copy()
    df_temp["score"] = df_temp["embedding"].apply(
        lambda x: cosine_similarity([q_emb], [x])[0][0] if x is not None else 0
    )

    # chemicals case
    if "compound_name" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["compound_id"]
        info_cols = [
            "compound_name",
            "molecular_formula", "molecular_weight",
            "reactivity_score", "toxicity_level",
            "solubility", "function", "origin",
            "stability_index", "skin_absorption_rate", "ph_value"
        ]
        available_cols = [col for col in info_cols if col in df_temp.columns]
        df_temp["info_for_output"] = (
            df_temp[available_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    # products case
    elif "product_name" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["product_id"]
        info_cols = [
            "product_name", "category",
            "target_skin_type", "key_ingredients",
            "effectiveness_score", "safety_score",
            "popularity_index", "description"
        ]
        available_cols = [col for col in info_cols if col in df_temp.columns]
        df_temp["info_for_output"] = (
            df_temp[available_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    # relations case
    elif "relation_id" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["relation_id"]
        info_cols = [
            "product_id", "compound_id", "percentage_in_formula",
            "role_in_product", "synergy_score",
            "interaction_type", "potential_new_compound"
        ]
        available_cols = [col for col in info_cols if col in df_temp.columns]
        df_temp["info_for_output"] = (
            df_temp[available_cols].fillna("").astype(str).agg(", ".join, axis=1)
        )

    else:
        return {"error": "Kolom name/info tidak ketemu."}

    return (
        df_temp.sort_values("score", ascending=False)
        .head(top_k)[["name_for_output", "info_for_output", "score"]]
        .rename(columns={"name_for_output": "name", "info_for_output": "info"})
    )


# =========================================================
# Tools untuk Agent
# =========================================================
@tool("search_chemical_tool")
def search_chemical_tool(query: str, top_k: int = 5) -> str:
    """Search for chemicals in database"""
    result = semantic_search(chemicals, query, top_k)
    if isinstance(result, dict) and "error" in result:
        return result["error"]

    result["name_display"] = result["name"].apply(pretty_compound)
    return result.to_json(orient="records")


@tool("search_product_tool")
def search_product_tool(query: str, top_k: int = 5) -> str:
    """Search for products in database"""
    result = semantic_search(products, query, top_k)
    if isinstance(result, dict) and "error" in result:
        return result["error"]

    result["name_display"] = result["name"].apply(pretty_product)
    return result.to_json(orient="records")


@tool("check_innovation_tool")
def check_innovation_tool(compound_id1: str, compound_id2: str) -> str:
    """Check innovation potential between two compounds"""
    if relations.empty:
        return "Relations database not available"
        
    df_filtered = relations[
        ((relations["compound_id"] == compound_id1) &
         relations["potential_new_compound"].astype(str).str.contains(compound_id2, na=False))
        |
        ((relations["compound_id"] == compound_id2) &
         relations["potential_new_compound"].astype(str).str.contains(compound_id1, na=False))
        |
        ((relations["compound_id"] == compound_id1) &
         (relations["product_id"].isin(
             relations[relations["compound_id"] == compound_id2]["product_id"]
         )))
        |
        ((relations["compound_id"] == compound_id2) &
         (relations["product_id"].isin(
             relations[relations["compound_id"] == compound_id1]["product_id"]
         )))
    ]

    if df_filtered.empty:
        return f"Tidak ada catatan inovasi/interaksi antara {compound_id1} dan {compound_id2}."
    return df_filtered.to_json(orient="records")


# =========================================================
# Setup LLM
# =========================================================
llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    api_key=REAL_KEY
)


# =========================================================
# Define Agents
# =========================================================
data_agent = Agent(
    role="Data Analyst Agent",
    goal=(
        "Mengambil data bahan/produk relevan, melakukan filtering, dan ranking kandidat terbaik. "
        "Gunakan tools maksimal 1 kali dan fokus pada top_k=5."
    ),
    backstory="Ahli database kosmetik fokus pencarian bahan sesuai kebutuhan user.",
    verbose=True,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool],
    llm=llm,
)

chemical_agent = Agent(
    role="Chemical Safety Agent",
    goal="Mengecek kompatibilitas bahan, risiko interaksi, pH ideal, dan potensi iritasi.",
    backstory="Ahli kimia kosmetik dan toksikologi yang sangat hati-hati.",
    verbose=True,
    allow_delegation=False,
    tools=[check_innovation_tool],
    llm=llm,
)

formulation_agent = Agent(
    role="Formulation Agent",
    goal="Membuat formula akhir total 100% + penjelasan + discovery jika ada.",
    backstory="Formulator skincare berpengalaman dan hanya pakai bahan terverifikasi.",
    verbose=True,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool],
    llm=llm,
)


# =========================================================
# Define Tasks
# =========================================================
task_data = Task(
    description=(
        "1) DATA AGENT TASK\n"
        "Cari data relevan untuk kebutuhan: {topic}.\n"
        "Gunakan tools:\n"
        "- search_product_tool\n"
        "- search_chemical_tool\n"
        "Outputkan shortlist Produk dan Bahan yang paling relevan.\n"
        "WAJIB jawab dalam Bahasa Indonesia."
    ),
    expected_output="Daftar produk dan bahan relevan beserta alasan.",
    agent=data_agent,
)

task_chemical = Task(
    description=(
        "2) CHEMICAL AGENT TASK\n"
        "Analisis keamanan dan interaksi dari shortlist Data Agent.\n"
        "Jika user minta gabung 2 bahan/produk, WAJIB pakai check_innovation_tool.\n"
        "WAJIB jawab dalam Bahasa Indonesia."
    ),
    expected_output="Analisis keamanan, risiko interaksi, hasil inovasi jika ada.",
    agent=chemical_agent,
    context=[task_data],
)

task_formulation = Task(
    description=(
        "3) FORMULATION AGENT TASK\n"
        "Susun rekomendasi akhir.\n"
        "Jika ada potential_new_compound → sebut sebagai PENEMUAN SENYAWA BARU.\n"
        "Jika tidak ada → sebut SINERGI FORMULA.\n"
        "WAJIB jawab dalam Bahasa Indonesia."
    ),
    expected_output="Laporan akhir rekomendasi / formula / discovery.",
    agent=formulation_agent,
    context=[task_data, task_chemical],
)


# =========================================================
# Build Crew
# =========================================================
crew = Crew(
    agents=[data_agent, chemical_agent, formulation_agent],
    tasks=[task_data, task_chemical, task_formulation],
    process=Process.sequential,
    verbose=False,
    max_rpm=10,
)


# =========================================================
# Safe kickoff
# =========================================================
def safe_kickoff(crew_inputs, max_retries=3):
    delay = 4
    last_err = None

    for _ in range(max_retries):
        try:
            return crew.kickoff(inputs=crew_inputs)
        except ClientError as e:
            last_err = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(delay)
                delay *= 2
                continue
            raise

    raise RuntimeError(f"Masih kena rate limit. Error terakhir: {last_err}")
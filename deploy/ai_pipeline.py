# ai_pipeline.py
import os, ast, time
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from google import genai
from google.genai.errors import ClientError


# =========================
# CONFIG PATH DATA
# =========================
DATA_DIR = os.environ.get("DATA_DIR", "data")
CHEM_PATH = os.path.join(DATA_DIR, "chemicals_with_embeddings.csv")
PROD_PATH = os.path.join(DATA_DIR, "products_with_embeddings.csv")
REL_PATH  = os.path.join(DATA_DIR, "relations_with_embeddings.csv")


# =========================
# API KEY
# =========================
REAL_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not REAL_KEY:
    raise ValueError("GEMINI_API_KEY / GOOGLE_API_KEY belum diset!")

client = genai.Client(api_key=REAL_KEY)
EMBED_MODEL = "text-embedding-004"


def get_embedding(text: str):
    res = client.models.embed_content(model=EMBED_MODEL, contents=text)
    return res.embeddings[0].values


# =========================
# LOAD CSV + PARSE EMB
# =========================
def safe_literal_eval(x):
    if not isinstance(x, str):
        return x
    try:
        return ast.literal_eval(x)
    except:
        return None

def load_csv_safe(path: str, tolerant=False):
    if tolerant:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    return pd.read_csv(path)

print("[ai_pipeline] Loading datasets...")
chemicals = load_csv_safe(CHEM_PATH)
products  = load_csv_safe(PROD_PATH)
relations = load_csv_safe(REL_PATH, tolerant=True)

for name, df in [("chemicals", chemicals), ("products", products), ("relations", relations)]:
    if "embedding" in df.columns:
        df["embedding"] = df["embedding"].apply(safe_literal_eval)
        before = len(df)
        df.dropna(subset=["embedding"], inplace=True)
        after = len(df)
        print(f"[ai_pipeline] {name} ready: {after} rows (drop {before-after})")


compound_id_to_name = dict(zip(
    chemicals["compound_id"].astype(str),
    chemicals["compound_name"].astype(str)
))
product_id_to_name = dict(zip(
    products["product_id"].astype(str),
    products["product_name"].astype(str)
))

def pretty_compound(cid: str) -> str:
    nm = compound_id_to_name.get(str(cid))
    return f"{cid} ({nm})" if nm and nm != "nan" else str(cid)

def pretty_product(pid: str) -> str:
    nm = product_id_to_name.get(str(pid))
    return f"{pid} ({nm})" if nm and nm != "nan" else str(pid)


# =========================
# SEMANTIC SEARCH (SATU AJA)
# =========================
def semantic_search(df, query, top_k=5):
    q_emb = get_embedding(query)

    df_temp = df.copy()
    df_temp["score"] = df_temp["embedding"].apply(
        lambda x: cosine_similarity([q_emb], [x])[0][0]
    )

    if "compound_name" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["compound_id"]
        info_cols = [
            "compound_name","molecular_formula","molecular_weight",
            "reactivity_score","toxicity_level","solubility",
            "function","origin","stability_index",
            "skin_absorption_rate","ph_value"
        ]
        df_temp["info_for_output"] = df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)

    elif "product_name" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["product_id"]
        info_cols = [
            "product_name","category","target_skin_type",
            "key_ingredients","effectiveness_score",
            "safety_score","popularity_index","description"
        ]
        df_temp["info_for_output"] = df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)

    elif "relation_id" in df_temp.columns:
        df_temp["name_for_output"] = df_temp["relation_id"]
        info_cols = [
            "product_id","compound_id","percentage_in_formula",
            "role_in_product","synergy_score",
            "interaction_type","potential_new_compound"
        ]
        df_temp["info_for_output"] = df_temp[info_cols].fillna("").astype(str).agg(", ".join, axis=1)

    return (
        df_temp.sort_values("score", ascending=False)
        .head(top_k)[["name_for_output","info_for_output","score"]]
        .rename(columns={"name_for_output":"name","info_for_output":"info"})
    )


# =========================
# TOOLS (WAJIB DOCSTRING)
# =========================
@tool("search_chemical_tool")
def search_chemical_tool(query: str, top_k: int = 5) -> str:
    """
    Cari & ranking bahan kimia relevan dari dataset chemicals.
    Input: query teks + top_k
    Output: JSON string list hasil (id, info, score, name_display).
    """
    result = semantic_search(chemicals, query, top_k)
    result["name_display"] = result["name"].apply(pretty_compound)
    return result.to_json(orient="records")


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
        ((relations["compound_id"] == compound_id1) &
         relations["potential_new_compound"].astype(str).str.contains(compound_id2, na=False))
        |
        ((relations["compound_id"] == compound_id2) &
         relations["potential_new_compound"].astype(str).str.contains(compound_id1, na=False))
    ]

    if df_filtered.empty:
        return f"Tidak ada catatan inovasi/interaksi antara {compound_id1} dan {compound_id2}."
    return df_filtered.to_json(orient="records")

# =========================
# LLM + AGENTS + TASKS + CREW
# =========================
llm = LLM(model="gemini/gemini-2.5-flash", api_key=REAL_KEY)

data_agent = Agent(
    role="Data Analyst Agent",
    goal="Cari produk/bahan relevan dari database.",
    backstory="Ahli database kosmetik.",
    verbose=False,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool],
    llm=llm,
)

chemical_agent = Agent(
    role="Chemical Safety Agent",
    goal="Cek keamanan + interaksi bahan.",
    backstory="Ahli kimia kosmetik.",
    verbose=False,
    allow_delegation=False,
    tools=[check_innovation_tool],
    llm=llm,
)

formulation_agent = Agent(
    role="Formulation Agent",
    goal="Susun rekomendasi akhir.",
    backstory="Formulator skincare.",
    verbose=False,
    allow_delegation=False,
    tools=[search_chemical_tool, search_product_tool],
    llm=llm,
)

task_data = Task(
    description="Cari data relevan untuk: {topic}.",
    expected_output="Shortlist produk/bahan relevan.",
    agent=data_agent,
)

task_chemical = Task(
    description="Analisis keamanan dan interaksi dari shortlist.",
    expected_output="Analisis keamanan.",
    agent=chemical_agent,
    context=[task_data],
)

task_formulation = Task(
    description="Buat rekomendasi akhir dalam Bahasa Indonesia.",
    expected_output="Jawaban final.",
    agent=formulation_agent,
    context=[task_data, task_chemical],
)

crew = Crew(
    agents=[data_agent, chemical_agent, formulation_agent],
    tasks=[task_data, task_chemical, task_formulation],
    process=Process.sequential,
    verbose=False,
    max_rpm=10,
)


# =========================
# SAFE KICKOFF (SATU AJA)
# =========================
def safe_kickoff(inputs, max_retries=3):
    delay = 4
    last_err = None
    for _ in range(max_retries):
        try:
            return crew.kickoff(inputs=inputs)
        except ClientError as e:
            last_err = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError(f"Masih kena rate limit. Error terakhir: {last_err}")


def run_ai(topic: str):
    """
    ENTRY POINT untuk FastAPI / BE.
    Input: pertanyaan user (topic)
    Output: hasil crew.kickoff
    """
    return safe_kickoff({"topic": topic})


import pandas as pd
from .fetch import download_pdf
from .utils import (
    save_pdf, extract_table_from_pdf,
    transform_curriculum, save_to_csv, save_to_parquet
)

PDF_URL      = "https://api.itmo.su/constructor-ep/api/v1/static/programs/10130/plan/abit/pdf"
PDF_PATH     = "data/ai_product_curriculum.pdf"
PROGRAM_NAME = "Управление ИИ‑продуктами"

def parse_ai_product_pdf_to_table() -> pd.DataFrame:
    pdf_bytes = download_pdf(PDF_URL)
    save_pdf(pdf_bytes, PDF_PATH)

    df_raw  = extract_table_from_pdf(pdf_bytes)
    df_hier = transform_curriculum(df_raw)
    # Добавляем колонку с направлением
    df_hier["program"] = PROGRAM_NAME

    save_to_csv(df_hier, "data/ai_product_hierarchical.csv")
    save_to_parquet(df_hier, "data/ai_product_hierarchical.parquet")
    return df_hier

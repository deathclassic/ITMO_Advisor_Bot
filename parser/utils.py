# parser/utils.py

import os
import io
import re
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pdfplumber
import requests

def download_pdf(url: str) -> bytes:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content

def save_pdf(data: bytes, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"✅ PDF saved to: {path}")

def extract_table_from_pdf(pdf_bytes: bytes) -> pd.DataFrame:
    rows = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if any(cell and cell.strip() for cell in row):
                        rows.append([cell.strip() if cell else "" for cell in row])
    return pd.DataFrame(rows)


def transform_curriculum(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Из сырых строк превращает только в колонки:
    mandatory (bool), semester_start (list), discipline (str), ects (int), hours (int)
    """
    records = []
    mandatory = None

    # Регекс для валидного семестра: "1" или "1,3"
    sem_re = re.compile(r'^\s*\d+(?:\s*,\s*\d+)*\s*$')

    # Флаг текущей секции
    in_mandatory_section = None  # True/False

    for _, row in df_raw.iterrows():
        sem_raw, name_raw, ects_raw, hours_raw = row[0], row[1], row[2], row[3]
        sem   = str(sem_raw or "").strip()
        name  = str(name_raw or "").strip()
        ects  = str(ects_raw or "").strip()
        hours = str(hours_raw or "").strip()

        # Обновляем флаг mandatory при встрече заголовков секций
        if sem == "" and name.startswith("Обязательные"):
            in_mandatory_section = True
            continue
        if sem == "" and (name.startswith("Пул выборных") or name.startswith("Дисциплины по выбору")):
            in_mandatory_section = False
            continue

        # Только настоящие дисциплины: валидный sem, и цифры в ects & hours
        if sem_re.match(sem) and ects.isdigit() and hours.isdigit():
            semesters = [int(x) for x in sem.split(",")]

            records.append({
                "mandatory": bool(in_mandatory_section),
                "semester_start": semesters,
                "discipline": name,
                "ects": int(ects),
                "hours": int(hours),
            })
            continue

        # всё остальное игнорируем

    return pd.DataFrame(records)


def save_to_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ CSV saved to: {path}")

def save_to_parquet(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path)
    print(f"✅ Parquet saved to: {path}")

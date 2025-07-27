# bot/recommender.py

import os
import random
from typing import List
import pandas as pd
import openai
import config

# Настройка OpenAI API‑ключа
openai.api_key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY

# Пути к данным
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PARQUET_PATH = os.path.join(BASE_DIR, "data", "combined_curriculum.parquet")
CSV_PATH = os.path.join(BASE_DIR, "data", "combined_curriculum.csv")

# Загрузка объединённого DataFrame (Parquet → CSV)
try:
    DF_ALL = pd.read_parquet(PARQUET_PATH)
except Exception:
    DF_ALL = pd.read_csv(CSV_PATH)

# Список уникальных элективных дисциплин (mandatory == False)
ELECTIVES = (
    DF_ALL
    .loc[DF_ALL["mandatory"] == False, "discipline"]
    .drop_duplicates()
    .tolist()
)


def shortlist(user_input: str, max_candidates: int = 10) -> List[str]:
    """
    Быстрая фильтрация: выбирает до max_candidates курсов,
    названия которых содержат слова из user_input.
    Если кандидатов мало — дополняет случайными элективами.
    """
    text = user_input.lower()
    # выбираем курсы, где встречается любое слово из запроса
    candidates = [
        course for course in ELECTIVES
        if any(word in course.lower() for word in text.split())
    ]
    # Ограничиваем и дополняем
    if len(candidates) >= max_candidates:
        return candidates[:max_candidates]
    others = [c for c in ELECTIVES if c not in candidates]
    random.shuffle(others)
    candidates += others[: max_candidates - len(candidates)]
    return candidates


def recommend(user_input: str, top_n: int = 5) -> List[str]:
    """
    Возвращает до top_n рекомендаций:
    1) short_list по ключевым словам
    2) уточнение через ChatGPT с узким промптом
    3) при ошибке — фоллбэк к первым top_n из shortlist
    """
    candidates = shortlist(user_input)

    # Короткий системный промпт
    system_prompt = (
            f"Ты академический рекомендационный ассистент.\n"
            f"Порекомендуй до {top_n} курсов из списка:\n\n" +
            "\n".join(f"{i + 1}. {c}" for i, c in enumerate(candidates))
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Бэкграунд и интересы абитуриента: {user_input}"}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=60
        )
        text = response.choices[0].message.content.strip()
        # Парсим ответ, фильтруя по кандидатам
        lines = [line.strip(" -*–") for line in text.splitlines() if line.strip()]
        recs = [line for line in lines if line in candidates]
        # Дополняем, если рекомендаций меньше top_n
        for c in candidates:
            if len(recs) >= top_n:
                break
            if c not in recs:
                recs.append(c)
        return recs[:top_n]
    except Exception:
        # Фоллбэк: просто первые top_n элементов shortlist
        return candidates[:top_n]

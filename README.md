# Chatbot Admission for ITMO

Telegram‑бот, который помогает абитуриентам выбирать магистерские программы ИТМО, рекомендуя элективные дисциплины на основе их бэкграунда и интересов. Данные учебных планов автоматически парсятся с сайта ITMO и сохраняются в удобном формате.

---

## 📁 Структура проекта

```
project/
├── bot.py                     # точка входа Telegram‑бота
│
├── bot/                       # вспомогательные модули бота
│   ├── recommender.py         # модуль рекомендаций (shortlist + ChatGPT + fallback)
│   └── filters.py             # (на будущее) логика фильтрации запросов
│
├── parser/
│   ├── fetch.py               # скачивание HTML и PDF
│   ├── utils.py               # общие функции: сохранение, извлечение и трансформация
│   ├── parse_ai.py            # парсинг учебного плана AI
│   └── parse_ai_product.py    # парсинг учебного плана AI‑Product
│
├── data/                      # Результаты парсинга:
│   ├── ai_curriculum.pdf      
│   ├── ai_hierarchical.csv    
│   ├── ai_hierarchical.parquet
│   ├── ai_product_curriculum.pdf
│   ├── ai_product_hierarchical.csv
│   ├── ai_product_hierarchical.parquet
│   ├── combined_curriculum.csv   
│   └── combined_curriculum.parquet
│
├── config.py                  # TELEGRAM_TOKEN, OPENAI_API_KEY, OPENAI_MODEL
├── main.py                    # точка входа для запуска парсера (parser/)
├── requirements.txt           # внешние зависимости
└── README.md                  # документация проекта
```

---

## 🛠 Установка и настройка

1. **Клонируйте репозиторий**  
   ```bash
   git clone <url>
   cd project
   ```

2. **Создайте и активируйте виртуальное окружение**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Unix/macOS
   .venv\Scriptsctivate      # Windows
   ```

3. **Установите зависимости**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Настройте `config.py`**  
   ```python
   # config.py
   TELEGRAM_TOKEN   = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"
   OPENAI_API_KEY   = "ВАШ_OPENAI_API_KEY"
   ```

---

## 🚀 Запуск

### 1. Сборка данных (парсер)

```bash
python main.py
```

- Скачивает PDF‑файлы учебных планов  
- Извлекает и трансформирует таблицы  
- Сохраняет результат в `data/*.csv` и `data/*.parquet`

### 2. Запуск Telegram‑бота

```bash
python bot.py
```

- **/start** — приветствие  
- **/help** — справка  
- Любой текст с ключевыми словами “курс”, “дисциплин”, “рекоменд”, “интерес”, “бэкграунд” → выдаёт до 5 рекомендаций элективных курсов  
- В остальных случаях бот отвечает, что может отвечать только на вопросы о курсах  

> **Важно:** бот **не сохраняет контекст** прошлых сообщений — каждый запрос обрабатывается независимо.

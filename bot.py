# bot/bot.py

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import config
from bot.recommender import recommend

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключевые слова для распознавания запросов «о курсах»
COURSE_KEYWORDS = ["курс", "дисциплин", "рекоменд", "интерес", "бэкграунд"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start
    """
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я помогу тебе выбрать элективные курсы в магистратуре ИТМО.\n"
        "Расскажи о своём бэкграунде или интересах, и я порекомендую курсы."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help
    """
    await update.message.reply_text(
        "/start — запустить бота\n"
        "/help — показать справку\n"
        "Опиши свои интересы или бэкграунд, и я порекомендую элективные курсы."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений:
    - если в тексте есть ключевые слова про курсы, выдаём рекомендации
    - иначе — сообщаем, что бот отвечает только на вопросы о курсах
    """
    text = update.message.text.strip()
    text_lower = text.lower()

    # Проверяем наличие ключевых слов
    if any(keyword in text_lower for keyword in COURSE_KEYWORDS):
        # Запрос про курсы — выдаём рекомендации
        try:
            recs = recommend(text, top_n=5)
            if recs:
                reply = "Вот курсы, которые я рекомендую:\n" + "\n".join(f"- {c}" for c in recs)
            else:
                reply = "К сожалению, я не смог подобрать подходящие курсы по твоему описанию."
        except Exception as e:
            logger.error("Ошибка при генерации рекомендаций: %s", e)
            reply = "Произошла ошибка при подборе курсов. Попробуй ещё раз."
    else:
        # Сообщение не про курсы
        reply = (
            "Извини, я могу отвечать только на вопросы о элективных курсах "
            "магистратуры ИТМО.\n"
            "Пожалуйста, опиши свои интересы или бэкграунд, "
            "и я подберу для тебя подходящие дисциплины."
        )

    await update.message.reply_text(reply)

def main() -> None:
    """
    Инициализация и запуск бота
    """
    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_TOKEN)
        .build()
    )

    # Регистрируем команды и хендлер сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            handle_message
        )
    )

    logger.info("Бот запущен. Ожидаю сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()

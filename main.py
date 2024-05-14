import telebot
from validators import *  # модуль для валидации
from yandex_gpt import ask_gpt  # модуль для работы с GPT
# подтягиваем константы из config файла
from config import *
# подтягиваем функции из database файла
from database import create_database, add_message, select_n_last_messages, insert_row
from stt import *
from tts import *

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
bot = telebot.TeleBot(TOKEN)  # создаём объект бота

def is_stt_block_limit(message, duration):
    user_id = message.from_user.id
    audio_blocks = math.ceil(duration / 15)
    all_blocks = count_all_limits(user_id, "stt_blocks") + audio_blocks

    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        bot.send_message(user_id, msg)
        return None

    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        bot.send_message(user_id, msg)
        return None

    return audio_blocks

def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)
    all_symbols = count_all_limits(user_id, "tts_symbols") + text_symbols
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text)


# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Отправь мне голосовое сообщение или текст, и я тебе отвечу!")

# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")

# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


# Декоратор для обработки голосовых сообщений, полученных ботом
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        user_id = message.from_user.id  # Идентификатор пользователя, который отправил сообщение

        # Получение информации о голосовом файле и его загрузка
        file_id = message.voice.file_id  # Идентификатор голосового файла в сообщении
        file_info = bot.get_file(file_id)  # Получение информации о файле для загрузки
        file = bot.download_file(file_info.file_path)  # Загрузка файла по указанному пути

        # Преобразование голосового сообщения в текст с помощью SpeechKit
        status_stt, stt_text = speech_to_text(file)  # Обращение к функции speech_to_text для получения текста
        if not status_stt:
            # Отправка сообщения об ошибке, если преобразование не удалось
            bot.send_message(user_id, stt_text)
            return

        # Отправка нескольких последних сообщений от пользователя в GPT для генерации ответа
        # В константе COUNT_LAST_MSG хранится количество сообщений пользователя, которые передаем
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        status_gpt, answer_gpt = ask_gpt(last_messages)  # Обращение к GPT с запросом
        if not status_gpt:
            # Отправка сообщения об ошибке, если GPT не смог сгенерировать ответ
            bot.send_message(user_id, answer_gpt)
            return

        # Преобразование текстового ответа от GPT в голосовое сообщение
        status_tts, voice_response = text_to_speech(answer_gpt)  # Обращение к функции text_to_speech для получения аудио
        if not status_tts:
            # Отправка текстового ответа GPT, если преобразование в аудио не удалось
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
        else:
            # Отправка голосового сообщения, если преобразование в аудио прошло успешно
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)

    except Exception as e:
        # Логирование ошибки
        logging.error(e)
        # Уведомление пользователя о непредвиденной ошибке
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")

@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)


def stt(message):
    user_id = message.from_user.id

    if not message.voice:
        return

    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    status, text = speech_to_text(file)
    if status:
        insert_row(user_id, text, 'stt_blocks', stt_blocks)
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)

@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщением текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)


def tts(message):
    user_id = message.from_user.id
    text = message.text

    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return

    insert_row(user_id, text, text_symbol)

    status, content = text_to_speech(text)

    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)

...

create_database()
bot.polling()
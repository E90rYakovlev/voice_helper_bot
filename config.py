TOKEN = "7104102860:AAFGwGgm0KjX3dsUslg7XPg6FWX8Q3eD6BM"  # token телеграм-бота
IAM_TOKEN = "t1.9euelZqRkcyRipmOy8-Ylo3Ix8ycme3rnpWakM6VnMmVicuUycuKz5HLzZHl8_d4LHxN-e95dXhi_d3z9zhbeU3573l1eGL9zef1656VmpHNyYqaxsrPzp3OiZLGyJzN7_zF656VmpHNyYqaxsrPzp3OiZLGyJzNveuelZqbks2YkM6bkJmOyZ2KjZTIirXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.RF2lb0O_pr_cIXbtYqJ1i2-zd8YVw_N8nt1m7LBymrabJVbIWDYMr6NO4L1ldsqxpRzLqln4Yh1ehFnlYIDECQ"
FOLDER_ID = "b1gn21mn067kri1haq1j"

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5_000  # 5 000 символов
MAX_USER_GPT_TOKENS = 2_000  # 2 000 токенов
MAX_TTS_SYMBOLS = 50


LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]
import requests


def text_to_speech(text):
    iam_token = 't1.9euelZqVm5WZns_PkM-Pjo6SyMnPx-3rnpWakM6VnMmVicuUycuKz5HLzZHl9PdbNBtO-e8gKUKd3fT3G2MYTvnvIClCnc3n9euelZrIxsqdyZyLj5qbjs6ayZaNx-_8xeuelZrIxsqdyZyLj5qbjs6ayZaNx73rnpWalpWel4ucj4-Zx8qOis3Hy8213oac0ZyQko-Ki5rRi5nSnJCSj4qLmtKSmouem56LntKMng.CURJlxqqgu6MQDBkbav1pE9ZDe2___j8GSwTIUfHU28WmBr3QJ8hgpXyKQEstwCRcQxSjZELXf8a7fpGVYgbBQ'
    folder_id = 'b1gn21mn067kri1haq1j'
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': folder_id,
    }
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content
    else:
        return False, "При запросе в SpeechKit возникла ошибка"
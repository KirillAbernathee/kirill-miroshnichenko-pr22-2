import httpx
import asyncio

class DictionaryAPI:
    def __init__(self):
        self.english_api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.yandex_api_url = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
        self.yandex_api_key = "dict.1.1.20260209T202016Z.6b722c1e1b6a0a84.b98ea8737e36899a6543ab4f4f72be1738739830"
        self.client = httpx.AsyncClient(timeout=10.0)

    def detect_language(self, word: str) -> str:
        """Определяет язык слова (русский/английский)."""
        if any('а' <= char <= 'я' or 'А' <= char <= 'Я' for char in word):
            return 'ru'
        return 'en'

    async def fetch_english_definition(self, word: str):
        """Получает определение для английского слова."""
        try:
            response = await self.client.get(self.english_api_url + word)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Ошибка при запросе к английскому API: {e}")
            return None

    async def fetch_russian_word_info(self, word: str):
        """Получает ВСЮ информацию о русском слове через Yandex (ru-en)."""
        try:
            # ru-en: получаем перевод на английский + синонимы, примеры и т.д.
            params = {
                'key': self.yandex_api_key,
                'lang': 'ru-en',  # русский → английский
                'text': word,
                'ui': 'ru'  # интерфейс на русском
            }
            response = await self.client.get(self.yandex_api_url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Ошибка при запросе к Yandex API: {e}")
            return None

    async def get_word_info(self, word: str):
        """Основной метод: получает всю информацию о слове."""
        lang = self.detect_language(word)
        
        if lang == 'en':
            data = await self.fetch_english_definition(word)
            return self.parse_english_response(data)
        else:
            data = await self.fetch_russian_word_info(word)
            return self.parse_russian_response(word, data)

    def parse_english_response(self, data):
        """Парсит ответ для английского слова (инфа на англ)."""
        if not data:
            return "Слово не найдено."
        
        result = []
        for entry in data[:2]:
            word = entry.get('word', '')
            phonetic = entry.get('phonetic', '')
            meanings = entry.get('meanings', [])
            
            result.append(f"📖 Слово: {word}")
            if phonetic:
                result.append(f"🔊 Транскрипция: [{phonetic}]")
            
            for meaning in meanings:
                part_of_speech = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                result.append(f"\n📚 Часть речи: {part_of_speech}")
                for i, definition in enumerate(definitions[:3], 1):
                    result.append(f"  {i}. {definition.get('definition', '')}")
                    example = definition.get('example')
                    if example:
                        result.append(f"     Пример: {example}")
        
        return '\n'.join(result)

    def parse_russian_response(self, russian_word, data):
        """Парсит ответ для русского слова (вся инфа на русском, но с англ переводом)."""
        if not data or 'def' not in data or not data['def']:
            return f"Слово '{russian_word}' не найдено в словаре."
        
        result = []
        result.append(f"📖 Русское слово: {russian_word}")
        result.append(f"🌍 Перевод на английский:\n")
        
        for entry in data['def'][:3]:  # берем до 3 вариантов
            pos_ru = self.translate_part_of_speech(entry.get('pos', ''))
            translations = entry.get('tr', [])
            
            if pos_ru:
                result.append(f"📚 Часть речи: {pos_ru} ({entry.get('pos', '')})")
            
            for i, translation in enumerate(translations[:4], 1):
                english_word = translation.get('text', '')
                synonyms_en = translation.get('syn', [])
                meanings_en = translation.get('mean', [])
                
                result.append(f"  {i}. Перевод: {english_word}")
                
                # Английские синонимы
                if synonyms_en:
                    syn_list = [syn.get('text', '') for syn in synonyms_en[:3]]
                    if syn_list:
                        result.append(f"     Английские синонимы: {', '.join(syn_list)}")
                
                # Дополнительные значения (на англ)
                if meanings_en:
                    mean_list = [mean.get('text', '') for mean in meanings_en[:3]]
                    if mean_list:
                        result.append(f"     Связанные слова: {', '.join(mean_list)}")
                
                # Примеры использования (русский + английский)
                examples = translation.get('ex', [])
                if examples:
                    result.append(f"     Примеры использования:")
                    for ex in examples[:2]:
                        ex_text = ex.get('text', '')  # русский пример
                        ex_translation = ""
                        if ex.get('tr'):
                            ex_translation = ex['tr'][0].get('text', '')  # англ перевод примера
                        result.append(f"       «{ex_text}»")
                        if ex_translation:
                            result.append(f"       → «{ex_translation}»")
                
                result.append("")  # пустая строка для разделения
            
            if translations:
                result.append("-" * 50 + "\n")
        
        # Если есть дополнительные формы (склонения) - на русском
        if data['def'][0].get('fl'):
            result.append(f"\n📝 Форма слова: {data['def'][0]['fl']}")
        
        # Добавляем общую справку
        result.append(f"\nℹ️  Информация представлена на русском языке.")
        result.append(f"   Перевод и синонимы даны на английском.")
        
        return '\n'.join(result)

    def translate_part_of_speech(self, pos_abbr):
        """Переводит сокращения частей речи с англ на русский."""
        pos_map = {
            'noun': 'существительное',
            'verb': 'глагол',
            'adjective': 'прилагательное',
            'adverb': 'наречие',
            'pronoun': 'местоимение',
            'preposition': 'предлог',
            'conjunction': 'союз',
            'interjection': 'междометие',
            'numeral': 'числительное',
            'participle': 'причастие',
            '': 'не указано'
        }
        return pos_map.get(pos_abbr.lower(), pos_abbr)

    async def close(self):
        """Закрывает HTTP-клиент."""
        await self.client.aclose()
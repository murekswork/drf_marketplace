import datetime
import time

from articles.models import Article

def time_logger(func):

    def wrapper():
        start = datetime.datetime.now()
        func()
        end = datetime.datetime.now()
        print(str(end - start))
        return
    return wrapper

class BadWordsValidator:

    BANNED_WORDS = open('articles/services/banwords.txt', mode='r', encoding='utf-8').read()

    def __init__(self, obj) -> None:
        self.obj = obj

    def _validate_field(self, content: str) -> bool:
        content = content.lower().split(' ')
        print(content)
        return all((content not in self.BANNED_WORDS for content in content))

    def _validate_obj(self) -> bool:
        fields = (self._validate_field(val) for val in self.obj.__dict__.values() if isinstance(val, str))
        print(fields)
        # fields = [self._validate_field(field) for field in (self.article.title, self.article.content)]
        return all(fields)

    def validate_bad_words(self) -> bool:
        validation = self._validate_obj()
        return validation
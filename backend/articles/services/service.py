from utils.validate_service import BadWordsValidator

from articles.models import Article

class ArticleBadWordsValidator(BadWordsValidator):

    def publish(self) -> Article:
        self.obj.published = True
        self.obj.save()
        return self.obj

class Mock:

    def __init__(self, title, content, amount):
        self.title = title
        self.content = content
        self.amount = amount
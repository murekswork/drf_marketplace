from articles.models import Article
from utils_.validation.badwords_validation import EntityBadWordsValidationService


class ArticleBadwordsValidationService(EntityBadWordsValidationService):

    def publish(self) -> Article:
        self.obj.published = True
        self.obj.save()
        return self.obj

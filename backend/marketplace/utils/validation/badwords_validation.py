class EntityBadWordsValidationService:

    BANNED_WORDS = open('../../articles/services/banwords.txt', encoding='utf-8').read()

    def __init__(self, obj) -> None:
        self.obj = obj

    def _validate_field(self, content: str) -> bool:
        words_of_content = content.lower().split(' ')
        return all(word not in self.BANNED_WORDS for word in words_of_content)

    def _validate_obj(self) -> bool:
        fields = (
            self._validate_field(val)
            for val in self.obj.__dict__.values()
            if isinstance(val, str)
        )
        return all(fields)

    def validate(self) -> bool:
        validation = self._validate_obj()
        return validation

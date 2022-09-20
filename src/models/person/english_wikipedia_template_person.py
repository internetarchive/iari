from src.models.person import Person
from src.models.wikimedia.wikipedia.references.enums import (
    EnglishWikipediaTemplatePersonRole,
)


class EnglishWikipediaTemplatePerson(Person):
    role: EnglishWikipediaTemplatePersonRole

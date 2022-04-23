from src.models.person import Person
from src.models.wikimedia.wikipedia.templates.enums import (
    EnglishWikipediaTemplatePersonRole,
)


class EnglishWikipediaTemplatePerson(Person):
    role: EnglishWikipediaTemplatePersonRole

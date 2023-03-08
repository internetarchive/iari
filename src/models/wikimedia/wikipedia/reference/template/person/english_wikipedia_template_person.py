from src.models.wikimedia.wikipedia.reference.enums import (
    EnglishWikipediaTemplatePersonRole,
)
from src.models.wikimedia.wikipedia.reference.template.person import Person


class EnglishWikipediaTemplatePerson(Person):
    role: EnglishWikipediaTemplatePersonRole

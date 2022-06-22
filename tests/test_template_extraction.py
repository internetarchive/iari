from collections import OrderedDict
from unittest import TestCase

from src.helpers.template_extraction import (
    extract_templates_and_params,
    remove_comments,
)


class TestTemplateExtraction(TestCase):
    def test_remove_comments_from_template(self):
        data = (
            "{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}"
        )
        # print(extract_templates_and_params(data, True))
        assert extract_templates_and_params(data, True) == [
            (
                "url",
                OrderedDict(
                    [("1", "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7")]
                ),
            )
        ]

    def test_remove_comments(self):
        text = (
            "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 "
            "<!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->"
        )
        assert (
            remove_comments(text)
            == "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7"
        )

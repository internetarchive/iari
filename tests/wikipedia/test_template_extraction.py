from unittest import TestCase


# FIXME update to changes in model
class TestTemplateExtraction(TestCase):
    pass
    # def test_remove_comments_from_template(self):
    #     data = (
    #         "{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}"
    #     )
    #     # print(extract_templates_and_params(data, True))
    #     assert extract_templates_and_params(data, True) == [
    #         (
    #             "url",
    #             OrderedDict(
    #                 [("1", "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7")]
    #             ),
    #             (
    #                 "{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 "
    #                 "<!--|alternate-full-text-url=https://babel.hathitrust.org/cgi/pt?id"
    #                 "=mdp.39015027915100&view=1up&seq=11 -->}}",
    #             ),
    #         )
    #     ]
    #
    # def test_remove_comments(self):
    #     text = (
    #         "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 "
    #         "<!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->"
    #     )
    #     assert (
    #         remove_comments(text)
    #         == "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7"
    #     )
    #
    # def test_cite_book_with_comment_in_url(self):
    #     data = (
    #         "{{cite book |last=von Mach |first=Edmund |author-link=Edmund von Mach "
    #         "|title=Official Diplomatic Documents Relating to the Outbreak of the European War: "
    #         "With Photographic Reproductions of Official Editions of the Documents "
    #         "(Blue, White, Yellow, Etc., Books) |url=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 "
    #         "<!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 --> "
    #         "|year=1916 |publisher=Macmillan |page=7 |location=New York |oclc=651023684 "
    #         "|lccn=16019222 |access-date=2020-12-03 |archive-date=2021-07-23 "
    #         "|archive-url=https://web.archive.org/web/20210723163014/"
    #         "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 |url-status=live }}"
    #     )
    #     # print(extract_templates_and_params(data, True))
    #     assert extract_templates_and_params(data, True) == [
    #         (
    #             "cite book",
    #             OrderedDict(
    #                 [
    #                     ("last", "von Mach"),
    #                     ("first", "Edmund"),
    #                     ("author-link", "Edmund von Mach"),
    #                     (
    #                         "title",
    #                         (
    #                             "Official Diplomatic Documents Relating to the Outbreak of the European War: "
    #                             "With Photographic Reproductions of Official Editions of the Documents (Blue, White, Yellow, Etc., Books)"
    #                         ),
    #                     ),
    #                     (
    #                         "url",
    #                         "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7",
    #                     ),
    #                     ("year", "1916"),
    #                     ("publisher", "Macmillan"),
    #                     ("page", "7"),
    #                     ("location", "New York"),
    #                     ("oclc", "651023684"),
    #                     ("lccn", "16019222"),
    #                     ("access-date", "2020-12-03"),
    #                     ("archive-date", "2021-07-23"),
    #                     (
    #                         "archive-url",
    #                         "https://web.archive.org/web/20210723163014/https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7",
    #                     ),
    #                     ("url-status", "live"),
    #                 ]
    #             ),
    #             (
    #                 "{{cite book |last=von Mach |first=Edmund |author-link=Edmund von Mach "
    #                 "|title=Official Diplomatic Documents Relating to the Outbreak of the European War: "
    #                 "With Photographic Reproductions of Official Editions of the Documents "
    #                 "(Blue, White, Yellow, Etc., Books) |url=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 "
    #                 "<!--|alternate-full-text-url="
    #                 "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 --> "
    #                 "|year=1916 |publisher=Macmillan |page=7 |location=New York |oclc=651023684 "
    #                 "|lccn=16019222 |access-date=2020-12-03 |archive-date=2021-07-23 "
    #                 "|archive-url=https://web.archive.org/web/20210723163014/"
    #                 "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 |url-status=live }}"
    #             ),
    #         )
    #     ]

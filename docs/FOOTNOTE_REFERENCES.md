# Footnote reference subtypes we have identified in the wild
1) **mixed reference with an ISBN template** - reference with plain text and a {{isbn}} template
2) **mixed reference with a URL template** - reference with plain text and a URL (these are very rare)
3) **ISBN template reference** - reference with only a {{isbn}} template
4) **URL template reference** - reference with only a {{url}} template
5) **Plain text reference with a cs1 template** - reference as above but where part of the
information is structured and part of it is not (theoretical so far, we presume it exists)
(defined as: begins with {{ and ends with }})
6) **multiple template reference with Google books template** -
(defined as: contains multiple templates according to mwparserfromhell)
E.g. {{cite book|url={{google books|123456}}}}
7) **multiple template reference with url and bare url x template** -
E.g. `<ref>Muller Report, p12 {{url|http://example.com}} {{bare url inline}}</ref>`
8) **reference with a Bare URL template** - as above, but with one of the {{bare url x}} templates
9) **Plain text reference with a URL outside a template** - as above, but with no other identifier than the URL
10) **Short citation reference** aka plain text reference without a URL or identifier -
special type of plain text reference. e.g. reference to a book only by author and title. e.g. "Muller Report, p12".
See https://en.wikipedia.org/w/index.php?title=Wikipedia:CITETYPE
![image](https://user-images.githubusercontent.com/68460690/208091737-abc20b6e-8102-4acd-b0fa-409aa72d9ae8.png)
11) **General reference with a template** - reference outside of <ref>.
E.g. part of further reading- or bibliography section that uses a template
12) **multiple template reference** - (defined as: contains multiple templates according to mwparserfromhell)

These two are similar but appear in different contexts. Both require a trained machine learning model to recognize
what they are referring to.
1) **General reference without a template** - reference outside of <ref>.
E.g. part of further reading- or bibliography section.
2) **Plain text reference without a template**: references inside <ref> tags, but without ANY template.

These bundled references are rare (<200 transclusions in enwiki)
* **Bundled reference** - multiple references in one <ref> see
https://en.wikipedia.org/w/index.php?title=Wikipedia:CITEBUNDLE
* **Unbulleted list citebundle reference** - type of nested reference with multiple templates inside,
see https://en.wikipedia.org/wiki/Template:Unbulleted_list_citebundle


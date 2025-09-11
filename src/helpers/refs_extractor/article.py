"""
This module provides utility functions for extracting references from Wikipedia articles.

This is originally from James Hare's code
"""

import mwparserfromhell
import re
import sys

from .testmodule import get_test
from .wikilist import extract_list_items
from .wikiapi import get_current_timestamp, get_wikipedia_article

reference_sections = [
    "references",
    "further reading",
    "external links",
    "bibliography",
    "works cited",
    "books",
    "articles"]


def extract_urls_from_text(text):
    url_regex = re.compile(r'(?:git|https?|ftps?)://[^\s\]\|\}]+')
    result = set(url_regex.findall(text))
    return result


def extract_references(wikitext):
    """
    parses from wikicode:
    - <ref> elements from text
    - Sfn templates
    - links from list-style sections
    - any urls not yet caught in other categories
    """
    wikicode = mwparserfromhell.parse(wikitext)
    references = []
    found_urls = set()

    # Extract <ref> tags content
    for tag in wikicode.filter_tags(matches=lambda node: node.tag == "ref"):
        for url in extract_urls_from_text(str(tag)):
            found_urls.add(url)


        references.append(str(tag))

        # Remove to prevent confusion later in the process
        try:
            wikicode.remove(tag)
        except ValueError:  # Already removed, somehow
            pass



    # Extract all {{Sfn}} templates in the body of the article
    for template in wikicode.filter_templates():
        if template.name.matches("Sfn"):
            for url in extract_urls_from_text(str(template)):
                found_urls.add(url)
            references.append(str(template))
            wikicode.remove(template)

    # Extract all list items with links, or list items in certain sections
    # regardless of link presence
    for section in wikicode.get_sections(levels=[2], include_lead=True):
        section_title = section.filter_headings()
        if section_title:
            title_text = section_title[0].title.strip_code().strip()
        else:
            title_text = ""
        for line in extract_list_items(section):
            if line.strip().startswith('*') or line.strip().startswith('#'):
                extracted_urls = extract_urls_from_text(str(line))
                if len(extracted_urls) > 0 or title_text.lower() in reference_sections:
                    for url in extracted_urls:
                        found_urls.add(url)
                    if line.strip() not in references:
                        references.append(line.strip())

    # Extract external link nodes not attached to any other reference type
    for external_link in wikicode.filter_external_links():
        if str(external_link.url) not in found_urls:
            references.append(str(external_link))

    return references


def extract_references_enhanced(wikitext):
    """
    parses from wikicode:
    - <ref> elements from text:
            {
                "wikitext": str(template),
                "urls": set(),
                "context": ""
            }

    - Sfn templates
    - links from list-style sections
    - any urls not yet caught in other categories
    """
    wikicode = mwparserfromhell.parse(wikitext)
    references = []  # array of {ref} dicts
    found_urls = set()

    # parse citations from <ref> tags templates
    parse_ref_citations(wikicode, references, found_urls)

    # parse Sfn templates : "Short Footnote"
    parse_sfn(wikicode, references, found_urls)

    # catch any other ref links we might have
    parse_others(wikicode, references, found_urls)


    # Extract external link nodes not attached to any other reference type
    for external_link in wikicode.filter_external_links():
        if str(external_link.url) not in found_urls:
            references.append(str(external_link))

    return references


def extract_references_from_page(title, domain="en.wikipedia.org", as_of=None):
    # old version of parser - returns only wikitext for each reference
    if as_of is None:
        as_of = get_current_timestamp()
    title = title.replace(" ", "_")
    page_id, revision_id, revision_timestamp, wikitext = get_wikipedia_article(domain, title, as_of)
    return {
        "page_id": page_id,
        "revision_id": revision_id,
        "revision_timestamp": revision_timestamp,
        "references": extract_references(wikitext)
    }


def extract_references_from_page_enhanced(title, domain="en.wikipedia.org", as_of=None):
    """
    returns a dict for each reference from extract_references_enhanced that includes:
    {
        wikitext: str
        urls: []
        context: str (if any)
    }
    """
    if as_of is None:
        as_of = get_current_timestamp()
    title = title.replace(" ", "_")
    page_id, revision_id, revision_timestamp, wikitext = get_wikipedia_article(domain, title, as_of)
    return {
        "page_id": page_id,
        "revision_id": revision_id,
        "revision_timestamp": revision_timestamp,
        "references": extract_references_enhanced(wikitext)
    }

def parse_sfn(wikicode, refs, urls):
    """
    sfn stands for Shortened Footnote Template
    """
    # Extract all {{Sfn}} templates in the body of the passed in wikicode
    for template in wikicode.filter_templates():
        if template.name.matches("Sfn"):
            my_ref = {
                "wikitext": str(template),
                "urls": [],
                "context": ""
            }

            # NB TODO do node by node so we can back track for claim

            for url in extract_urls_from_text(str(template)):
                urls.add(url)
                my_ref["urls"].append(url)

            refs.append(my_ref)
            # wikicode.remove(template)


def parse_ref_citations(wikicode, refs, urls):
    # Iterate through all the nodes
    nodes = list(wikicode.nodes)

    for i, node in enumerate(nodes):
        if isinstance(node, mwparserfromhell.nodes.tag.Tag) and node.tag == "ref":

            wt = str(node)

            my_ref = {
                "wikitext": wt,
                "urls": [],
                "context": "",
                "section": "",
            }

            # process the url links in this ref
            # NB may want to process templates iteratively here...
            # ...process_templates_in_node(my_node)
            # can recurse template within template, etc.
            for url in extract_urls_from_text(wt):
                my_ref["urls"].append(url)
                urls.add(url)

            # try to get the text referring to this citation, which is usually the previous node
            if i > 0 and isinstance(nodes[i - 1], mwparserfromhell.nodes.text.Text):
                referring_text = nodes[i - 1].value.strip()
                my_ref["context"] = referring_text

                # print(f"Referring text: {referring_text}")
                # print(f"Citation: {node.contents}")

            refs.append(my_ref)


def parse_others(wikicode, refs, urls):
    # Extract all list items with links, or list items in certain sections
    # regardless of link presence

    for section in wikicode.get_sections(levels=[2], include_lead=True):
        section_title = section.filter_headings()
        if section_title:
            title_text = section_title[0].title.strip_code().strip()
        else:
            title_text = ""
        for line in extract_list_items(section):
            if line.strip().startswith('*') or line.strip().startswith('#'):
                extracted_urls = extract_urls_from_text(str(line))

                if len(extracted_urls) > 0 or title_text.lower() in reference_sections:
                    for url in extracted_urls:
                        urls.add(url)

                    # check if reference is included already
                    if line.strip() not in refs:
                        my_ref = {
                            "wikitext": str(line.strip()),
                            "urls": [],
                            "context": ""
                        }

                        refs.append(my_ref)
    # pass


if __name__ == "__main__":
    page_title = "Easter Island"
    as_of = None
    if len(sys.argv) >= 2:
        page_title = sys.argv[1]
        if len(sys.argv) == 3:
            as_of = sys.argv[2]

    for ref in extract_references_from_page(page_title, as_of=as_of):
        print(ref, end="\n\n")

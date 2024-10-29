from typing import Any, Dict, List, Optional
import re
import logging

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

# from src.models.exceptions import MissingInformationError
from src.models.v2.analyzers import IariAnalyzer

from src.helpers.refs_extractor.wikiapi import get_current_timestamp, get_wikipedia_article
from src.helpers.refs_extractor.article import \
    extract_references_from_page as extract_references_from_page_old,\
    extract_urls_from_text

logger = logging.getLogger(__name__)


class WikiAnalyzerV2(IariAnalyzer):
    """
    Implements IariAnalyzer base class

    logic for obtaining statistics from wiki page

    what we need:
    page spec or wikitext

    what we return:
    json formatted data of refs
    later: more stat data from refs

    """

    # @staticmethod
    # def get_page_data(page_spec) -> Dict[str, Any]:
    #
    #     # NB WTF TODO the goal: return self.article_statistics.dict()
    #
    #     # return info from james's ref extractor for page_spec
    #
    #     # init return_data
    #     return_data = {
    #         "media_type": "wiki_article"
    #     }
    #     return_data.update(page_spec) # append page_spec data to return data
    #     # for key in page_spec:
    #     #     return_data[key] = page_spec[key]
    #
    #     # extract reference data
    #     ref_data_simple = extract_references_from_page(page_spec["page_title"], page_spec["domain"], page_spec["as_of"])
    #     ref_data = extract_references_from_page_enhanced(page_spec["page_title"], page_spec["domain"],
    #                                                      page_spec["as_of"])
    #
    #     # convert revision_id to a string
    #     return_data["page_id"] = str(ref_data["page_id"])
    #     return_data["revision_id"] = str(ref_data["revision_id"])
    #
    #     # process the references
    #
    #     # go thru each reference and process:
    #
    #     # # add "wikitext" element
    #     # # extract urls from each reference
    #
    #     refs = []
    #     for ref in ref_data["references"]:
    #         urls = list(extract_urls_from_text(ref))
    #         my_ref = {
    #             "wikitext": ref,
    #             "urls": urls,
    #         }
    #         refs.append(my_ref)
    #
    #     return_data["references"] = refs
    #     return_data["reference_count"] = len(refs)
    #
    #
    #     # from src import app
    #     # app.logger.debug(f"get_page_data {return_data}")
    #     #
    #     return return_data


    @staticmethod
    def get_page_data(page_spec) -> Dict[str, Any]:

        # seed return data with page specs
        return_data = {
            "media_type": "wiki_article"
        }
        return_data.update(page_spec) # append page_spec fields to return data

        # this is the "old" extraction technique from James - it just returns the raw wikitext for each reference
        ref_data_old = get_references_old(page_spec)
        # extract reference data
        ref_data = extract_references_from_page(page_spec["page_title"],
                                                page_spec["domain"],
                                                page_spec["as_of"])

        # ref_data has refs array with:
        # [ wikitext, name, etc, templates, urls, section_name, context, ..other? ]
        #

        # process the reference data
        """
        here is where templates, urls, are extracted...??? 
        """

        # fill fields in return data and return
        return_data["page_id"] = str(ref_data["page_id"])
        return_data["revision_id"] = str(ref_data["revision_id"])
        return_data["section_names"] = ref_data["section_names"]
        return_data["reference_count"] = len(ref_data["references"])
        return_data["references"] = ref_data["references"]
        return_data["references_old"] = ref_data_old

        return return_data


def extract_references_from_page(title, domain="en.wikipedia.org", as_of=None):
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

    sections = extract_sections(wikitext)  # section is a wikicode
    refs = []
    # for section in sections:
    #     refs.append(extract_references_from_section(section))

    return {
        "page_id": page_id,
        "revision_id": revision_id,
        "revision_timestamp": revision_timestamp,
        "section_names": get_section_names(sections),
        "references": refs
    }


def extract_sections(wikitext):
    from src import app

    sections: List[Dict[str, Any]] = []

    wikicode = mwparserfromhell.parse(wikitext)
    wiki_sections = wikicode.get_sections(
        levels=[2],
        include_headings=True,
    )

    if not wiki_sections:
        # return one section representing whole article
        app.logger.debug("No level 2 sections detected, creating root section")
        sections.append({
            "name": "root",
            "wikicode": str(wikicode)
        })

    else:
        # extract first "section-less" part as "root" section
        root_section = extract_root_section(wikitext)
        sections.append({"name": "root", "wikicode": root_section})

        for section in wiki_sections:
            name = section.get(0).title if section.get(0).title else "No title"
            sections.append({
                "name": section.get(0).title if section.get(0).title else "No title",
                "wikicode": str(section)
            })

        return sections


def extract_root_section(wikitext):
    """This extracts the root section from the beginning until the first level 2 heading"""
    # Split at the first occurrence of a section header (== Section ==)
    sections = re.split(r"\n==[^=]+==\n", wikitext, maxsplit=1)
    # The first section is before the first header
    root = sections[0].strip()  # Use .strip() to remove any leading/trailing whitespace
    return root


def get_section_names(sections):
    for section in sections:
        print(f"section: {section['name']}")
    return [str(section["name"]).strip() for section in sections]


def extract_references_from_section(wikicode):
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
    # wikicode = mwparserfromhell.parse(wikitext)
    references = []  # array of {ref} dicts
    found_urls = set()

    # parse citations from <ref> tags templates
    parse_ref_citations(wikicode, references, found_urls)

    # # parse Sfn templates : "Short Footnote"
    # parse_sfn(wikicode, references, found_urls)
    #
    # # catch any other ref links we might have
    # parse_others(wikicode, references, found_urls)


    # Extract external link nodes not attached to any other reference type
    for external_link in wikicode.filter_external_links():
        if str(external_link.url) not in found_urls:
            references.append(str(external_link))

    return references


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


# =========================================================================

def get_references_old(page_spec):
    """
    returns array of refs with just wikitext and urls for each reference
    """
    all_refs = extract_references_from_page_old(page_spec["page_title"], page_spec["domain"], page_spec["as_of"])

    # process the references

    refs = []
    for ref in all_refs["references"]:
        urls = list(extract_urls_from_text(ref))

        my_ref = {
            "wikitext": ref,
            "urls": urls,
        }

        refs.append(my_ref)

    return refs

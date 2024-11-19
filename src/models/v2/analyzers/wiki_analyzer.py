from typing import Any, Dict, List, Optional
import re
import logging
import requests

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from src.models.exceptions import MissingInformationError
from src.models.v2.analyzers import IariAnalyzer

from iarilib.parse_utils import extract_cite_refs

from src.helpers.refs_extractor.wikiapi import get_current_timestamp, get_wikipedia_article
from src.helpers.refs_extractor.article import \
    extract_references_from_page as extract_references_from_page_old, \
    extract_urls_from_text


class WikiAnalyzerV2(IariAnalyzer):
    """
    "Implements" IariAnalyzer base class

    logic for obtaining statistics from wiki page

    what we need:
    page spec or wikitext

    what we return:
    json formatted data of refs
    later: more stat data from refs

    """

    @staticmethod
    def get_page_data(page_spec) -> Dict[str, Any]:

        # seed return data with page specs
        return_data = {
            "media_type": "wiki_article"
        }
        return_data.update(page_spec)  # append page_spec fields to return data

        # extract reference data
        # ref_data is array of references, each one like:
        # { wikitext, name, [etc], templates, urls, section_name, claim, ...other? }
        ref_data = extract_references_from_page(page_spec["page_title"],
                                                page_spec["domain"],
                                                page_spec["as_of"])

        cite_refs = extract_citerefs_from_page(page_spec["page_title"],
                                               page_spec["domain"],
                                               page_spec["as_of"])

        # process the reference data
        # TODO here is where templates, urls, et al., are extracted into aggregate properties...???

        # fill fields in return data and return
        return_data["page_id"] = str(ref_data["page_id"])
        return_data["revision_id"] = str(ref_data["revision_id"])
        return_data["section_names"] = ref_data["section_names"]
        return_data["reference_count"] = len(ref_data["references"])
        return_data["references"] = ref_data["references"]
        return_data["url_count"] = len(ref_data["urls"])
        return_data["urls"] = ref_data["urls"]
        return_data["cite_refs_count"] = len(cite_refs)
        return_data["cite_refs"] = cite_refs

        return return_data


def extract_references_from_page(title, domain="en.wikipedia.org", as_of=None):
    """
    returns a dict for each reference:
    {
        wikitext: str
        urls: []
        claim: str (if any)
        <others>
        NB TODO should we make a ref class to contain these fields?
    }
    """
    if as_of is None:
        as_of = get_current_timestamp()
    title = title.replace(" ", "_")

    page_id, revision_id, revision_timestamp, wikitext = get_wikipedia_article(domain, title, as_of)

    sections = extract_sections(wikitext)  # sections are Wikicode objects

    """
    my_ref = {
        "wikitext": wt,
        "urls": [],
        "claim": "",
        "section": "",
    }
    """
    refs = []
    for section in sections:
        section_refs = get_refs_from_section(section)
        refs.extend(section_refs)

    [found_urls] = post_process_refs(refs)

    return {
        "page_id": page_id,
        "revision_id": revision_id,
        "revision_timestamp": revision_timestamp,

        "section_names": [get_section_title(section) for section in sections],
        "urls": list(found_urls),
        "references": refs
    }


def extract_sections(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    wiki_sections = wikicode.get_sections(
        levels=[2],
        include_headings=True,
        include_lead=True
    )

    return wiki_sections


def get_section_title(section):
    try:
        # Attempt to get the first line as the title
        first_line = section.splitlines()[0]
        if first_line.startswith("=="):
            # Strip '==' to get the title
            return first_line.strip("=").strip()
        else:
            # Handle case for lead section or untitled section
            return "Lead Section"

    except IndexError:
        # Handle case where the section is empty or malformed
        return "Section is empty or malformed."


def get_refs_from_section(section: Wikicode) -> List[object]:
    """
    generic.py::__extract_templates_and_parameters__ - gets templates
    """
    from src import app

    nodes = list(section.nodes)
    refs = []
    section_name = get_section_title(section)

    # Iterate through all the nodes
    for i, node in enumerate(nodes):

        if isinstance(node, mwparserfromhell.nodes.tag.Tag) and node.tag == "ref":

            wt = str(node)

            my_ref = {
                "wikitext": wt,
                "name": get_ref_attribute(node, "name"),  # fetch the name of the ref, if any
                "urls": [],
                "claim": "",
                "section": section_name,
                "templates": get_templates_from_ref(node),
            }

            # process the url links in this ref
            # NB may want to process templates iteratively here...
            #   e.g.: process_templates_in_node(my_node)
            #   can recurse template within template, etc.
            for url in extract_urls_from_text(wt):
                my_ref["urls"].append(url)

            [claim_text, claim_array] = get_claim(i, nodes)
            my_ref["claim_array"] = claim_array
            my_ref["claim"] = claim_text

            refs.append(my_ref)

        # check for sfn template
        if isinstance(node, mwparserfromhell.nodes.template.Template) and node.name.strip().lower() == "sfn":
            app.logger.debug("Found sfn template:", node)
            # what to do?
            # we can save as reference, with SFN type, and parameters
            # ref is a "pointer" to another ref
            # in my lingo, a "citation" to a reference
            # citation: place in article
            # reference: source to link to
            # references can have a cite_array - where in the article it is referenced

    return refs


def get_ref_attribute(ref, attr_name):
    """
    assumes ref is a wikicode node.
    returns value of ref attribute or None if not found
    """
    for attr in ref.attributes:
        if attr.name.strip() == attr_name:
            return attr.value.strip()
    return None


def get_templates_from_ref(ref):
    """
    extract templates from ref.
    ref should be wikicode
    """

    if not ref:
        raise MissingInformationError("get_templates_from_ref: ref is None")

    # assume node is a <ref> Tag node
    raw_templates = ref.contents.ifilter_templates(
        matches=lambda t: not t.name.lstrip().startswith("#"),  # #-started templates not processed
        recursive=True,
    )

    templates = []
    for t in raw_templates:
        template_name = t.name.strip().lower()
        params = {param.name.strip(): param.value.strip() for param in t.params}
        templates.append(
            {
                "name": template_name,
                "parameters": params
            }
        )

    return templates


def get_claim(node_number, nodes):
    # # try to get the claim text referring to this citation, which is usually the previous node
    # if i > 0 and isinstance(nodes[i - 1], mwparserfromhell.nodes.text.Text):
    #
    #     # get the last 5 nodes before ref to try claims
    #     claim_array = []
    #     for offset in range(1, 5):
    #         if (i - offset) < 0:
    #             break
    #         claim_array.append(nodes[i - 1].value.strip())
    #
    #     referring_text = nodes[i - 1].value.strip()
    #
    #     my_ref["claim"] = referring_text
    #     my_ref["claim_array"] = claim_array
    #
    #     # print(f"Referring text: {referring_text}")
    #     # print(f"Citation: {node.contents}")

    claim_array = []
    claim_text = ""
    terminal_found = False  # condition to stop back-looking for claim
    offset = 0
    max_back_nodes = 12

    while (offset < max_back_nodes) and not terminal_found:
        offset += 1

        # stop if we past start of node list
        if (node_number - offset) < 0:
            break

        nindex = node_number - offset
        node = nodes[nindex]
        node_text = ""

        if isinstance(node, mwparserfromhell.nodes.text.Text):
            node_text = str(node.value)
        elif isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
            node_text = str(node.title) if not node.text else str(node.text)
        else:
            node_text = str(node.value) if hasattr(node, 'value') else ""

        """
        terminate if period followed by whitespace is found in display_val snippet.
        end_of_sentence_pattern regex: r"\.\s|\.$"
            - Matches a period followed by whitespace OR
            - a period at the end of the string
        """
        end_of_sentence_pattern = r"\.\s"
        terminal_found = re.search(end_of_sentence_pattern, node_text)

        # claim_array is for debugging
        claim_array.append(f"[{type(nodes[nindex])}] {node_text}")

        # append current node_text to beginning of claim_text,
        # because we are searching backwards from the <ref> node
        claim_text = node_text + claim_text


    # just use LAST sentence of claim text
    claim_sentences = re.split(r'\.\s+', claim_text)
    claim_text = claim_sentences[-1] if claim_sentences else claim_text

    return [claim_text, claim_array]


def post_process_refs(refs):
    """
    returns extracted data from refs
    for now:
        - urls: a set() of collated urls to ensure unique entries

    may do in the future:
    - top-level list for template_names in ref
    - top-level list for titles in ref
    """

    found_urls = set()
    for ref in refs:
        # add ref's urls to global url set
        for url in ref["urls"]:
            found_urls.add(url)

        # any other processing for ref

        ref["template_names"] = [template["name"] for template in ref["templates"] ]
        # ref["titles"] = [parameters["title"] for param in ref["templates"]["parameters"] ]
        ref["titles"] = [
            template["parameters"].get("title") for template in ref["templates"] if "title" in template["parameters"]
        ]
        # if
        #                          "templates" in ref and "template_name" in template["parameters"]]

    return [found_urls]


def extract_citerefs_from_page(title, domain="en.wikipedia.org", as_of=None):
    html_source = fetch_page_html(title, domain, as_of)
    return extract_cite_refs(html_source)


def fetch_page_html(title, domain="en.wikipedia.org", as_of=None):
    """
    Get html for latest version of page, from which we extract
    links in the article where the cite-ref's for each reference
    """
    from src import app

    # page request url for html source:
    # example: https://en.wikipedia.org/w/rest.php/v1/page/Earth/with_html
    user_agent = "IARI, see https://github.com/internetarchive/iari"
    url = (
        f"https://{domain}/"
        f"w/rest.php/v1/page/{title}/with_html"
    )

    html_markup = ""

    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)

    # console.print(response.json())
    if response.status_code == 200:
        data = response.json()
        html_markup = data["html"]

    elif response.status_code == 404:
        # self.found_in_wikipedia = False
        app.logger.error(
            f"Could not fetch page html from {title} because of 404. See {url}"
        )
    else:
        raise Exception(
            f"Could not fetch page html from {title}. Got {response.status_code} from {url}"
        )

    return html_markup

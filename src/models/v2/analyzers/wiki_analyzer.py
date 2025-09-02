from typing import Any, Dict, List, Optional
import re
import logging
import requests

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.analyzers import IariAnalyzer

from iarilib.parse_utils import extract_cite_refs

from src.helpers.refs_extractor.wikiapi import \
    get_current_timestamp, \
    get_wikipedia_article
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
        results = {
            "media_type": "wiki_article"
        }
        results.update(page_spec)  # append page_spec fields to return_data

        # extract reference data
        # ref_data is array of references, each one like:
        # { wikitext, name, [etc], templates, urls, section_name, claim, ...other? }

        # ref_data uses James Hare's reference extraction code
        ref_data = extract_references_from_page(page_spec["page_title"],
                                                page_spec["domain"],
                                                page_spec["as_of"])

        # cite_refs uses local iarilib's extract_cite_refs
        cite_refs = extract_citerefs_from_page(page_spec["page_title"],
                                               page_spec["domain"],
                                               page_spec["as_of"])



        # handle error from ref_data here
        # if ref_data.errors then
        # return error stuff (check iare calling)



        # process the reference data
        # TODO here is where templates, urls, et al., are extracted into aggregate properties...???
        # NB: this is what is currently done on the IARE client side
        #   this needs to be brought into here...
        #   generate alist of tasks that must be done here

        # fill fields in return data and return
        results["page_id"] = str(ref_data["page_id"])
        results["revision_id"] = str(ref_data["revision_id"])

        results["section_names"] = ref_data["section_names"]

        results["reference_count"] = len(ref_data["references"])
        results["references"] = ref_data["references"]

        results["url_count"] = len(ref_data["urls"])
        results["urls"] = ref_data["urls"]

        results["cite_refs_count"] = len(cite_refs)
        results["cite_refs"] = cite_refs

        return results


def extract_references_from_page(title, domain="en.wikipedia.org", as_of=None):
    """
    raises Exception if error anywhere along way

    returns a dict describing page and references
    {
        "page_id": page_id,
        "revision_id": revision_id,
        "revision_timestamp": revision_timestamp,

        "section_names": [get_section_title(section) for section in sections],
        "urls": list(found_urls),
        "references": array of refs:
            [
                {
                    wikitext: str
                    urls: []
                    claim: str (if any)
                    <others>
                    NB TODO should we make a ref class to contain these fields?
                }, ....
            ]

    }

    if errors, returns a dict:
    {
        "errors": errors,
    }

    """
    from src import app

    if as_of is None:
        as_of = get_current_timestamp()

    title = title.replace(" ", "_")

    # page_id, revision_id, revision_timestamp, wikitext = (
    #     get_wikipedia_article(domain, title, as_of)
    # )
    try:
        results = get_wikipedia_article(domain, title, as_of)

    except Exception as e:
        app.logger.debug("Results from get_wikipedia_article:")
        app.logger.debug(f"page_id: {results.get('page_id')}")
        app.logger.debug(f"rev_id: {results.get('rev_id')}")
        app.logger.debug(f"rev_timestamp: {results.get('rev_timestamp')}")
        app.logger.debug(
            f"wikitext: {results.get('wikitext')[:100] if results.get('wikitext') else ''}")  # First 100 chars
        app.logger.debug(f"errors: {results.get('errors')}")

        raise WikipediaApiFetchError(f"Error while get_wikipedia_article {e}")

        # TODO ERR
        #   if page_id None, check another field for errors...
        #   if errors here, return appropriate field values indicating such
        # otherwise continue...

    if results["errors"]:
        app.logger.debug(f"#### wiki_analyzer::extract_references_from_page: results['errors'] is true!")

        err = results["errors"][0]
        app.logger.debug(f"#### wiki_analyzer::extract_references_from_page: err = {err}")
        app.logger.debug(f"#### wiki_analyzer::extract_references_from_page: err.details = {err['details']}")

        app.logger.debug(f"####")
        app.logger.debug(f"#### wiki_analyzer::extract_references_from_page: right before raise Error")
        app.logger.debug(f"####")

        raise WikipediaApiFetchError(err["details"])
        # raise WikipediaApiFetchError(err["details"])

    # no errors, so expect the following fields:
    # page_id,
    # rev_id,
    # rev_timestamp and
    # wikitext fields

    # ...and parse the sections out of the received wikitext
    sections = mw_extract_sections(results.wikitext)  # sections are Wikicode objects
    # TODO make sections a collection of Section objects that are passed the mwPFH section object,
    #   these Section objects should have active methods as well, like extract_refs, et al.

    """
    my_ref = {
        "wikitext": <wikitext goes here>,
        "urls": [],
        "claim": "",
        "section": "",
    }
    """
    refs = []

    for section in sections:
        section_refs = get_refs_from_section(section)
        # TODO replace with "section.get_refs" when section becomes an object with a "get_refs" method
        refs.extend(section_refs)

    [found_urls] = post_process_refs(refs)

    return {
        "page_id": results.page_id,
        "revision_id": results.rev_id,
        "revision_timestamp": results.rev_timestamp,

        "section_names": [get_section_title(section) for section in sections],
        "urls": list(found_urls),
        "references": refs
    }


def mw_extract_sections(wikitext):
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

    # Iterate through all the nodes, special casing on "ref" nodes and "sfn nodes

    for i, node in enumerate(nodes):

        if isinstance(node, mwparserfromhell.nodes.tag.Tag) and node.tag == "ref":

            wt = str(node)

            my_ref = {
                "wikitext": wt,
                "name": get_ref_attribute(node, "name"),  # fetch the name of the ref, if any
                "urls": [],
                "claim": "",
                "claim_array": [],
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
            app.logger.debug(f"Found sfn template: {str(node)}")
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
        matches=lambda x: not x.name.lstrip().startswith("#"),  # #-started templates not processed
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
    """
    things to check:
    if immediate left tag is a reftag, "skip over" reftag and try to get claim text
    - could get claim text of that to-the-left claim tag

    The left boundary of a claim text could be another ref itself,
    as the preceeding ref comes AFTER the preceedingref's claim text's terminbating period

    many refs in a row, as in [85][86][87][88][89] K Rosa, e.g.

    This:
    In the first half of the 20th century, steam reportedly came out of the
     Rano Kau crater wall. This was photographed by the island's manager, Mr. Edmunds.
    (Mr. stops it!)
    (If terminating period's preceeding text is one of accepted abbreviations, continue on)

    """

    """
    If you want to handle tags more robustly (e.g., extract attributes or process nested contents), here are some useful properties and methods:

    node.tag: Returns the name of the tag (e.g., "b" for <b>).
    node.attributes: Returns the tag's attributes as a dictionary-like object.
    str(node): Returns the entire tag as a string, including its opening and closing tags.

    """

    # piece together the claim text referring to the citation at node_number.
    # The citation can be all the previous nodes before the last full stop.

    claim_array = []
    claim_text = ""
    terminal_found = False  # condition to stop back-looking for claim
    offset = 0
    max_back_nodes = 12

    while (offset < max_back_nodes) and not terminal_found:
        offset += 1

        n_index = node_number - offset

        # stop if at beginning of node list
        if n_index < 0:
            break

        node = nodes[n_index]
        node_text = ""

        if isinstance(node, mwparserfromhell.nodes.text.Text):
            node_text = str(node.value)

        elif isinstance(node, mwparserfromhell.nodes.tag.Tag):
            node_text = str(node.contents)
            # node_text = str(node)
            # NB  the node may contain other nodes that need to be processed

        elif isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
            node_text = str(node.title) if not node.text else str(node.text)

        elif isinstance(node, mwparserfromhell.nodes.html_entity.HTMLEntity):
            node_text = str(node)

        else:
            node_text = str(node.value) if hasattr(node, 'value') else ""



        """
        terminate if period followed by whitespace is found in display_val snippet.
        end_of_sentence_pattern regex: r"\.\s|\.$"
            - Matches a period followed by whitespace OR
            - a period at the end of the string

        # end_of_sentence_pattern = r"\.\s"
        """
        end_of_sentence_pattern = r"^\s*\n|\.\s"
        terminal_found = re.search(end_of_sentence_pattern, node_text)

        # claim_array is for debugging
        claim_array.append(f"[{type(nodes[n_index])}] {node_text}")

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
    - isBook?
    - isDoi?
    """

    found_urls = set()
    for ref in refs:
        # add ref's urls to global url set
        for url in ref["urls"]:
            found_urls.add(url)

        # any other processing for ref

        ref["template_names"] = list({template["name"] for template in ref["templates"]})  # only list unique

        ref["titles"] = [
            template["parameters"].get("title") for template in ref["templates"] if "title" in template["parameters"]
        ]

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

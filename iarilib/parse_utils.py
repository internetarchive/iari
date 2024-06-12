# parse_utils.py
import re

from bs4 import BeautifulSoup

# logging.basicConfig(level=config.loglevel)
import logging
logger = logging.getLogger(__name__)


def extract_cite_refs(html):

    # NB TODO we could do a citod here, and see what we get backfrom the raw html...

    soup = BeautifulSoup(html, "html.parser")
    # for link in soup.find_all("a"):
    #     print(link.get("href"))

    ref_wrapper = soup.find("div", class_="mw-references-wrap")

    refs = []

    if ref_wrapper:

        references_list = ref_wrapper.find("ol", class_="references")

        ref_counter = 0
        for ref in references_list.find_all("li"):

            cite_html = None
            span_html = None
            urls = []
            page_refs = []

            ref_counter += 1

            for link in ref.find_all("a"):
                # span.mw-linkback-text children should have a citeref link
                if link.find("span", class_="mw-linkback-text"):
                    page_refs.append(
                        {
                            "href": link.get("href"),
                            "id": link.get("id"),
                        }
                    )

            span_link = ref.find("span", class_="mw-reference-text")
            raw_data = None

            if span_link:

                # logger.info("yes span_link")

                link_data = span_link.find("link")
                if link_data:
                    raw_data = link_data.get("data-mw")

                # extract entire <cite> html
                cite = span_link.find("cite")

                if cite:
                    cite_html = cite.prettify()  # marked up html

                    # extract urls from <a> tags from <cite>
                    a_tags = cite.find_all('a')
                    for a in a_tags:
                        href = a.get('href')
                        if re.match(r"^https?://", href) is not None:
                            urls.append(href)

#
            if not cite_html:
                span_html = span_link.prettify()

            refs.append(
                {
                    "id": ref.get("id"),
                    # "ref_index": ref_counter,
                    "raw_data": raw_data,
                    "page_refs": page_refs,
                    "cite_html": cite_html,
                    "span_html": span_html,
                    "urls": urls,
                }
            )

    return refs

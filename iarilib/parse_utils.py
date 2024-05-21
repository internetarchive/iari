# parse_utils.py
from bs4 import BeautifulSoup


def extract_cite_refs(html):

    soup = BeautifulSoup(html, "html.parser")
    # for link in soup.find_all("a"):
    #     print(link.get("href"))

    ref_wrapper = soup.find("div", class_="mw-references-wrap")

    refs = []

    if ref_wrapper:

        references_list = ref_wrapper.find("ol", class_="references")

        ref_counter = 0
        for ref in references_list.find_all("li"):
            ref_counter += 1
            page_refs = []
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
                link_data = span_link.find("link")
                if link_data:
                    raw_data = link_data.get("data-mw")

            refs.append(
                {
                    "id": ref.get("id"),
                    # "ref_index": ref_counter,
                    "raw_data": raw_data,
                    "page_refs": page_refs,
                }
            )

    return refs

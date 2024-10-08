from typing import Any, Dict, List, Optional
import logging

# from src.models.exceptions import MissingInformationError
from src.models.v2.analyzers import IariAnalyzer

from src.helpers.refs_extractor.article import extract_references, extract_urls_from_text, extract_references_from_page


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

    # @property
    # def article_found(self) -> bool:
    #     if not self.article:
    #         raise MissingInformationError("self.article was None")
    #     return self.article.found_in_wikipedia

    # returns dict of article data ( self.article_statistics.dict() )


    @staticmethod
    def get_page_data(page_spec) -> Dict[str, Any]:

        # NB WTF TODO the goal: return self.article_statistics.dict()

        # return info from james's ref extractor for page_spec

        # init return_data
        return_data = {
            "media_type": "wiki_article"
        }
        return_data.update(page_spec) # append page_spec data to return data
        # for key in page_spec:
        #     return_data[key] = page_spec[key]

        # extract reference data
        ref_data = extract_references_from_page(page_spec["page_title"], page_spec["domain"], page_spec["as_of"])
        # convert revision_id to a string
        return_data["page_id"] = str(ref_data["page_id"])
        return_data["revision_id"] = str(ref_data["revision_id"])

        # process the references

        # go thru each reference and process:

        # # add "wikitext" element
        # # extract urls from each reference

        new_refs = []
        for ref in ref_data["references"]:
            urls = list(extract_urls_from_text(ref))
            new_ref = {
                "wikitext": ref,
                "urls": urls,
            }
            new_refs.append(new_ref)

        return_data["references"] = new_refs
        return_data["reference_count"] = len(new_refs)


        # from src import app
        # app.logger.debug(f"get_page_data {return_data}")
        #
        return return_data

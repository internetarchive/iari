// Adds a link to the article in IA-Sandbox
// Author: So9q
// Date: 2022
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js

function addPortletLink(){
          mw.util.addPortletLink(
          "p-tb",
          "http://18.217.22.248/v1/wikidata-qid/" + mw.config.get("wgWikibaseItemId") ,
          "IA-Sandbox item for this article",
          "tb-sandbox-link",
          "Link to the item for this article in IA-Sandbox"
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
}


// [[Category:Wikipedia scripts]]

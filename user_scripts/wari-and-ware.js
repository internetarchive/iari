// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

function get_article_url(refresh){
    let url = "http://18.217.22.248/v2/statistics/article"+
          "?lang=en&site=wikipedia&title=" +
          encodeURIComponent(mw.config.get( 'wgPageName' ))
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}


function addPortletLink(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(false),
          "Get WARI article statistics",
          "tb-wari-get-stats",
          "View the statistics for this article by the WARI API."
          );
}
function addPortletLinkRefresh(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(true),
          "Get refreshed WARI article statistics",
          "tb-wari-get-stats-ref",
          "View fresh statistics for this article by the WARI API. "
          );
}
function addPortletWare(){
          mw.util.addPortletLink(
          "p-tb",
          "http://mojomonger.com/assets/jview/",
          "Go to WARE",
          "tb-ware",
          "View statistics for this article in WARE."
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
    $(addPortletLinkRefresh);
    $(addPortletWare);
}


// [[Category:Wikipedia scripts]]

// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

function get_url(refresh){
    let pagename = encodeURIComponent(mw.config.get( 'wgPageName' ))
    let url = "http://18.217.22.248/v1/get-statistics"+
          "?lang=en&site=wikipedia&title=" + pagename
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
          get_url(false),
          "Get wcdimportbot statistics",
          "tb-wcdimportbot-get-stats",
          "View the statistics for this article by wcdimportbot API. Note: "
          + "if they are not cached it could take a minute or two before you get a response"
          );
}
function addPortletLinkRefresh(){
          mw.util.addPortletLink(
          "p-tb",
          get_url(true),
          "Get refreshed wcdimportbot statistics",
          "tb-wcdimportbot-get-stats-ref",
          "View fresh statistics for this article by wcdimportbot API. "
          + "Note: It can take a couple of minutes before you get a response"
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
    $(addPortletLinkRefresh);
}


// [[Category:Wikipedia scripts]]

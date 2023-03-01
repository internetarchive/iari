// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

function get_article_url(refresh){
    let url = "http://18.217.22.248/v1/get-statistics"+
          "?lang=en&site=wikipedia&title=" +
          encodeURIComponent(mw.config.get( 'wgPageName' ))
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}

function get_urls_url(refresh, subset){
    let url = "http://18.217.22.248/v1/get-urls"+
          "?lang=en&site=wikipedia&title=" +
          encodeURIComponent(mw.config.get( 'wgPageName' ))
    if (refresh) {
        url = url + "&refresh=true"
    }
    else {
        url = url + "&refresh=false"
    }
    if (subset === "not_found") {
        console.log("got not_found")
        url = url + "&subset=not_found"
    }
    else if (subset === "malformed") {
        console.log("got malformed")
        url = url + "&subset=malformed"
    }
    return url
}

function addPortletLink(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(false),
          "Get WARI statistics",
          "tb-wari-get-stats",
          "View the statistics for this article by the WARI API. Note: "
          + "if they are not cached it could take a minute or two before you get a response"
          );
}
function addPortletLinkRefresh(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(true),
          "Get refreshed WARI statistics",
          "tb-wari-get-stats-ref",
          "View fresh statistics for this article by the WARI API. "
          + "Note: It can take a couple of minutes before you get a response"
          );
}
function addPortletLinkUrlAll(){
          mw.util.addPortletLink(
          "p-tb",
          get_urls_url(false, null),
          "Get all URL statistics from WARI",
          "tb-wari-get-stats-urls-all",
          "View statistics for this article by the WARI API. "
          + "Note: It can take a couple of minutes before you get a response"
          );
}
function addPortletLinkUrlNotFound(){
          mw.util.addPortletLink(
          "p-tb",
          get_urls_url(false, "not_found"),
          "Get 404 URL statistics from WARI",
          "tb-wari-get-stats-urls-404",
          "View statistics for this article by the WARI API. "
          + "Note: It can take a couple of minutes before you get a response"
          );
}
function addPortletLinkUrlMalformed(){
          mw.util.addPortletLink(
          "p-tb",
          get_urls_url(false, "malformed"),
          "Get malformed URL statistics from WARI",
          "tb-wari-get-stats-urls-malformed",
          "View statistics for this article by the WARI API. "
          + "Note: It can take a couple of minutes before you get a response"
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
    $(addPortletLinkRefresh);
    $(addPortletLinkUrlAll);
    $(addPortletLinkUrlNotFound);
    $(addPortletLinkUrlMalformed);
}


// [[Category:Wikipedia scripts]]

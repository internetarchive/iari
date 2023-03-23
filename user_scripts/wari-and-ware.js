// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

let api_url = "https://archive.org/services/context/wari/"
let version = "v2"

function get_article_url(refresh){
    let url = api_url + version + "/statistics/article"+
          "?url=" + encodeURIComponent(window.location.href)
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}

function get_all_url(refresh){
    let url = api_url + version + "/statistics/all"+
          "?url=" + encodeURIComponent(window.location.href)
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}


function addPortletLinkAll(){
          mw.util.addPortletLink(
          "p-tb",
          get_all_url(false),
          "Get WARI statistics",
          "tb-wari-get-all-stats",
          "View the statistics for this article by the WARI all API endpoint."
          );
}
function addPortletLinkAllRefresh(){
          mw.util.addPortletLink(
          "p-tb",
          get_all_url(true),
          "Get WARI statistics (force refresh)",
          "tb-wari-get-all-stats",
          "View fresh statistics for this article by the WARI all API endpoint."
          );
}
function addPortletLinkArticle(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(false),
          "Get WARI article statistics",
          "tb-wari-get-stats",
          "View the statistics for this article by the WARI article API endpoint."
          );
}
function addPortletLinkArticleRefresh(){
          mw.util.addPortletLink(
          "p-tb",
          get_article_url(true),
          "Get WARI article statistics (force refresh)",
          "tb-wari-get-stats-ref",
          "View fresh statistics for this article by the WARI API. "
          );
}
function addPortletWare(){
          mw.util.addPortletLink(
          "p-tb",
          "https://archive.org/services/context/ware/",
          "Go to WARE",
          "tb-ware",
          "View statistics for this article in WARE."
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLinkAll);
    $(addPortletLinkAllRefresh);
    $(addPortletLinkArticle);
    $(addPortletLinkArticleRefresh);
    $(addPortletWare);
}


// [[Category:Wikipedia scripts]]

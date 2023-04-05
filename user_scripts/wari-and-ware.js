// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

let wari_url = "https://archive.org/services/context/wari/"
let ware_staging_url = "https://internetarchive.github.io/ware/"
let ware_production_url = "https://archive.org/services/context/ware/"
let wari_version = "v2"

function get_article_url(refresh){
    let url = wari_url + wari_version + "/statistics/article"+
          "?url=" + encodeURIComponent(window.location.href)
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}

function get_all_url(refresh){
    let url = wari_url + wari_version + "/statistics/all"+
          "?url=" + encodeURIComponent(window.location.href)
    if (refresh) {
        return url + "&refresh=true"
    }
    else {
        return url + "&refresh=false"
    }
}

function get_ware_url(version){
    if (version == "staging") {
        return ware_staging_url + "?url=" + encodeURIComponent(window.location.href)
    }
    else {
        return ware_production_url + "?url=" + encodeURIComponent(window.location.href)
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
function addPortletWareStaging(){
          mw.util.addPortletLink(
          "p-tb",
          get_ware_url("staging"),
          "Go to WARE (staging)",
          "tb-ware",
          "View statistics for this article in the staging version of WARE."
          );
}

function addPortletWareProduction(){
          mw.util.addPortletLink(
          "p-tb",
          get_ware_url(),
          "Go to WARE",
          "tb-ware",
          "View statistics for this article in the production version of WARE."
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletWareProduction);
    $(addPortletWareStaging);
    $(addPortletLinkAll);
    $(addPortletLinkAllRefresh);
    $(addPortletLinkArticle);
    $(addPortletLinkArticleRefresh);
}


// [[Category:Wikipedia scripts]]

// Title: Get statistics for this article from wcdimportbot API
// Author: So9q
// Date: 2023
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// Note: This user script was created as part of wcdimportbot, see https://www.wikidata.org/wiki/Q115252313

function addPortletLink(){
          mw.util.addPortletLink(
          "p-tb",
          "http://18.217.22.248/v1/get-statistics?lang=en&site=wikipedia&title=" + encodeURIComponent(mw.config.get( 'wgPageName' )) ,
          "Get wcdimportbot statistics",
          "tb-wcdimportbot-get-stats",
          "View the statistics for this article by wcdimportbot API"
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
}


// [[Category:Wikipedia scripts]]

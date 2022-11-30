// Title: Add new job for this article to wcdimportbot
// Author: So9q
// Date: 2022
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js

function addPortletLink(){
          mw.util.addPortletLink(
          "p-tb",
          "http://18.217.22.248/v1/add-job?lang=en&site=wikipedia&title=" + mw.config.get( 'wgPageName' ) ,
          "Add wcdimportbot job",
          "tb-wcdimportbot-add-job",
          "Add new job for this article to wcdimportbot"
          );
}

if(mw.config.values.wgNamespaceNumber === 0) {
    $(addPortletLink);
}


// [[Category:Wikipedia scripts]]

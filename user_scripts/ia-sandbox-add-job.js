// Title: Add new job for this article to wcdimportbot
// Author: So9q
// Date: 2022
// Inspired by https://en.wikipedia.org/wiki/User:Dipankan001/New_pages.js
// TODO: add check for namespace == 0 (article)

function addNewpages(){
          mw.util.addPortletLink(
          "p-tb",
          "http://18.217.22.248/v1/add-job?lang=en&site=wikipedia&title=" + mw.config.get( 'wgPageName' ) ,
          "Add wcdimportbot job",
          "tb-wcdimportbot-add-job",
          "Add new job for this article to wcdimportbot"
          );
}

$(addNewpages);


// [[Category:Wikipedia scripts]]

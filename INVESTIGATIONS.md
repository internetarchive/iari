# User script investigation
Todo

# Citation generation helpers services and scripts
These scripts and services play a central role in 
generating valid CS1 templates to be inserted on (English) Wikipedia 

Some of them were supported by grants.

## [Citoid](https://www.wikidata.org/wiki/Q21679984)
Mediawiki extension. This is already the default in the visual editor.
https://en.wikipedia.org/wiki/User:BrandonXLF/Citoid

## [Web2cit](https://www.wikidata.org/wiki/Q115473545) (launched in september 2022)
This is not the default but way more accurate and customizeable than citoid it seems.
It was made by Diego de la hara who seems competent at writing JavaScript and got a grant
for creating Web2Cit in 2022
It currently has 
[only 11 active users on English Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:User_scripts/Most_imported_scripts) which is suprisingly few.
https://en.wikipedia.org/wiki/User:Diegodlh/Web2Cit/script
https://meta.wikimedia.org/wiki/Web2Cit
https://commons.wikimedia.org/wiki/File:How_to_use_Web2Cit.webm
https://commons.wikimedia.org/wiki/File:How_Web2Cit_works.webm
https://commons.wikimedia.org/wiki/Category:Web2Cit

## Proveit
ProveIt (/ˈpruːvɪt/) is a gadget that makes it easy to find, edit, add, and cite 
references when editing Wikipedia articles. Referencing is a key task at Wikipedia, 
but the process is often difficult because the citation templates (such as 
Template:Cite book) are complex. ProveIt simplifies the process by adding a smart 
and simple graphical user interface when editing any article. You deal with the interface, 
and ProveIt deals with the wikitext. 
https://en.wikipedia.org/wiki/Wikipedia:ProveIt

# References in Wikipedia

## Many references are lacking any template = big issue
These are completely ignore by wcdimportbot because we only support references 
entered in one of the currently 30 templates we support.

We currently do not try to analyze all references <ref>...</ref> which lack templates, 
but we could start doing that since we download all the wikitext anyway (and throw away 
everything data in of of the supported templates).

See https://commons.wikimedia.org/wiki/File:Wikipedia%27s_references_and_citation_templates_shift.png
for a graphical overview.
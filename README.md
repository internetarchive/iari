# WikiCitations Import Bot
This bot is capable of fetching and storing 
reference information from Wikipedia pages as structured data 
in a Wikibase instance. 

This bot has been developed by James Hare (version 1.0.0) 
and Dennis Priskorn (version 2) as part of the 
Turn All References Blue project which is led by 
Mark Graham head of The 
Wayback Machine department of the Internet Archive.

A Wikibase with millions of references and edges between 
them and the Wikipedia page(s) they are used on is useful
 for both Wiki(p|m)edians and researchers who wish to understand
 which websites are linked to which pages and used as references.

This is part of a wider initiative help raise the quality of sources in 
Wikipedia to and enable everyone in the world to make
 decisions based on trustworthy information that is sourced by 
trustworthy sources.

# What is Wikibase?
Wikibase is a FLOSS graph database which enables users to store large
amounts of information and query them using SPARQL.
Wikibase has been created by Wikimedia Deutchland and is 
maintained by them as of this writing.

# Why store the data about references in a graph database?
The advantages of having access to this data in a graph are many.
* Overview and visualization of references across (whole categories) of Wikipedia pages becomes possible.
* Overview of most cited websites in the world
* Using SPARQL it becomes easy to e.g. pinpint pages with less trustworthy sources
* Using the data over time can help follow and understand changes in patterns of referencing.
* and more...

# Supported templates
There are a lot of templates in use in the different Wikipedias. For now 
the bot only supports templates and parameters from English Wikipedia 
but intention is to code it in a way that avoids hardcoding of 
enwp specific templates and parameters.

## English Wikipedia templates
English Wikipedia has hundreds of special reference templates in use 
and a handful of widely used generic templates.

Currently the focus is on supporting the most widely used reference 
templates in English Wikipedia.

### List of currently supported templates
supported_templates = [
    "citation",  # see https://en.wikipedia.org/wiki/Template:Citation
    "cite q",
    "citeq",
    "isbn",
    "url",
    # CS1 templates:
    "cite arxiv",
    "cite av media notes",
    "cite av media",
    "cite biorxiv",
    "cite book",
    "cite cite seerx",
    "cite conference",
    "cite encyclopedia",
    "cite episode",
    "cite interview",
    "cite journal",
    "cite magazine",
    "cite mailing list" "cite map",
    "cite news",
    "cite newsgroup",
    "cite podcast",
    "cite press release",
    "cite report",
    "cite serial",
    "cite sign",
    "cite speech",
    "cite ssrn",
    "cite techreport",
    "cite thesis",
    "cite web",
]

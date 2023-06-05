# Internet Archive Reference Inventory [IARI](https://www.wikidata.org/wiki/Q117023013)

This API is capable of fetching, extracting, transforming and storing
reference information from Wikipedia articles as [structured data](https://www.wikidata.org/wiki/Q26813700).

The endpoints make it possible to get structured data about the references 
from any Wikipedia article in any language version.

# Background
There are [at least 200 million references in at least 40 million articles](
https://ieeexplore.ieee.org/abstract/document/9908858)
and together with the article text in the Wikipedias
one of the most valuable collections of knowledge ever made by humans,
see [size comparison](https://en.wikipedia.org/wiki/Wikipedia:Size_comparisons).

Wikimedia movement currently does not have good and effective tools 
to help editors keep up the quality of references over time. 
The references are stored in templates that differ between language versions of Wikipedia 
which makes it hard for tool developers to develop good tools that work well 
across different language versions.

# Author
IARI has been developed by [Dennis Priskorn](https://www.wikidata.org/wiki/Q111016131) as part of the
[Turn All References Blue project](https://www.wikidata.org/wiki/Q115136754) which is led by
Mark Graham, head of The
[Wayback Machine](https://www.wikidata.org/wiki/Q648266) department of the
[Internet Archive](https://www.wikidata.org/wiki/Q461). 

# Goals
The endpoint providing a detailed analysis of a Wikipedia article and it's references
enable wikipedians to get an overview of the state of the references and using the API it is
possible for the Wikimedia tech-community to build tools that help make it easier to curate 
and improve the references.

This is part of a wider initiative help raise the quality of references in
Wikipedia to enable everyone in the world to make decisions
based on trustworthy knowledge
that is derived from trustworthy sources.

# Stepping stone for a (graph) database of all references 
This project is a part of the [Wikicite initiative](http://wikicite.org/).

On the longer term Turn All References Blue project is planning on populating a database
based on the data we extract. 
This part of the effort is led by [James Hare](https://www.wikidata.org/wiki/Q23041486).

The end goal is a large database with all references from all Wikipedias. 
We call it the Wikipedia Citations Database (WCD).

# Features

IARI features a number of endpoints that help patrons
get structured data about references in a Wikipedia article:

* an _article_ endpoint which analyzes a given article and returns basic statistics about it
* a _references_ endpoint which gives back all ids of references found
* a _reference_ endpoint which gives back all details about a reference including templates and wikitext
* a _check-url_ endpoint which looks up the URL and gives back
  standardized information about its status
* a _check-doi_ endpoint which looks up the DOI and gives back
  standardized information about it from [FatCat](https://fatcat.wiki/), OpenAlex and Wikidata
  including abstract, retracted status, and more.
* a _pdf_ endpoint which extracts links both from annotations and free text from PDFs.
* a _xhtml_ endpoint which extracts links both from any XHTML-page.

# Limitations

See known limitations under each endpoint below.

# Supported Wikipedias

Currently we support a handful of the 200+ language versions of Wikipedia
but we plan on extending the support to all Wikipedia language versions
and you can help us by submitting sections to search for references in issues and
pull requests.

We also would like to support non-Wikimedia wikis using MediaWiki in the future
and perhaps also any webpage on the internet with outlinks (e.g. news articles).

## Wikipedia templates

English Wikipedia for example has hundreds of special reference templates in use
and a handful of widely used generic templates.
WARI exposes them all when found in a reference.

## Reference types detected by the ArticleAnalyzer

We support detecting the following types. A reference cannot have multiple types.
We distinguish between two main types of references:

1) **named reference** - type of reference with only a name and no content e.g. '<ref name="INE"/>' (Unsupported
   beyond counting because we have not decided if they contain any value)
2) **content reference** - reference with any type of content
    1) **general reference** - subtype of content reference which is outside a <ref></ref> and usually found in
       sections called "Further reading" or "Bibliography"
       (unsupported but we want to support it, see
       https://github.com/internetarchive/wcdimportbot/labels/general%20reference)
       ![image](https://user-images.githubusercontent.com/68460690/208092363-ba4b5346-cad7-495e-8aff-1aa4f2f0161e.png)
    2) **footnote reference** - subtype of content reference which is inside a <ref> (supported partially, see below)

Example of a URL-template reference:
`<ref>Mueller Report, p12 {{url|http://example.com}} {{bare url inline}}</ref>`
This is a content reference -> a footnote reference -> a mixed reference with a URL template.

Example of an plain text reference:
`<ref>Muller Report, p12</ref>`
This is a footnote reference -> content reference -> Short citation reference aka naked named footnote.

# Endpoints

## Checking endpoints

### Check URL

the check-url endpoint accepts the following parameters:

* url (mandatory)
* refresh (optional)
* testing (optional)
* timeout (optional)

On error it returns 400.

#### Known limitations

Sometimes we get back a 403 because an intermediary like Cloudflare detected that we are not a person behind a browser
doing the request. We don't have any ways to detect these soft200s.

Also sometimes a server returns status code 200 but the content is an error page or any other content than what the
person asking for the information wants. These are called soft404s and we currently do not make any effort to detect
them.

You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

## Statistics

### article

the statistics/article endpoint accepts the following parameters:

* url (mandatory)
* refresh (optional)
* testing (optional)

On error it returns 400. On timeout it returns 504 or 502
(this is a bug and should be reported).

It will return json similar to:

```
{
    "wari_id": "en.wikipedia.org.999263",
    "lang": "en",
    "page_id": 999263,
    "dehydrated_references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "titles": [],
            "section": "History"
        },
        {
            "id": "1db10c83",
            "template_names": [
                "citation"
            ],
            "type": "footnote",
            "footnote_subtype": "content",
            "flds": [
                "hydroretro.net"
            ],
            "urls": [
                "http://www.hydroretro.net/etudegh/sncase.pdf"
            ],
            "titles": [
                "Les r\u00e9alisations de la SNCASE"
            ],
            "section": "History"
        }
    ],
    "reference_statistics": {
        "named": 10,
        "footnote": 20,
        "content": 21,
        "general": 1
    },
    "served_from_cache": false,
    "site": "wikipedia.org",
    "timestamp": 1684217693,
    "isodate": "2023-05-16T08:14:53.932785",
    "timing": 0,
    "title": "SNCASO",
    "fld_counts": {
        "aviafrance.com": 3,
        "flightglobal.com": 2,
        "gouvernement.fr": 1,
        "jewishvirtuallibrary.org": 1,
        "hydroretro.net": 1,
        "google.com": 1
    },
    "urls": [
        "http://www.hydroretro.net/etudegh/sncase.pdf",
        "http://www.aviafrance.com/aviafrance1.php?ID_CONSTRUCTEUR=1145&ANNEE=0&ID_MISSION=0&CLE=CONSTRUCTEUR&MOTCLEF=",
        "https://www.gouvernement.fr/partage/9703-vol-historique-du-premier-avion-a-reaction-francais-le-so-6000-triton",
        "https://books.google.com/books?id=3y0DAAAAMBAJ&pg=PA128",
        "http://www.flightglobal.com/pdfarchive/view/1953/1953%20-%201657.html",
        "https://www.flightglobal.com/pdfarchive/view/1959/1959%20-%201053.html",
        "http://xplanes.free.fr/so4000/so4000-5.htm",
        "http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour",
        "http://www.aviafrance.com/constructeur.php?ID_CONSTRUCTEUR=1145",
        "http://www.aviafrance.com"
    ],
    "ores_score": {
        "prediction": "GA",
        "probability": {
            "B": 0.3001074961272599,
            "C": 0.2989581851995906,
            "FA": 0.03238239107761332,
            "GA": 0.33793161511968084,
            "Start": 0.0251506380008608,
            "Stub": 0.005469674474994447
        }
    }
}
```

#### Known limitations

* the general references parsing relies on 2 things:
    * a manually supplied list of sections to search using the 'regex' to the article and all endpoints. The list is
      case insensitive and should be delimited by the '|' character.
    * that every line with a general reference begins with a star character (*)

Any line that doesn't begin with a star is ignored.

### references

the statistics/references endpoint accepts the following parameters:

* wari_id (mandatory, str) (this is obtained from the article endpoint)
* all (optional, boolean) (default: false)
* offset (optional, int) (default: 0)
* chunk_size (optional, int) (default: 10)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:

```
{
    "total": 31,
    "references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "wikitext": "<ref name = \"Hartmann1\" />",
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "templates": [],
            "titles": [],
            "section": "History",
            "served_from_cache": true
        },
    ]
}
```

#### Known limitations

None

### reference

the statistics/reference/id endpoint accepts the following parameters:

* id (mandatory) (this is unique for each reference and is obtained from the article or references endpoint)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:

```
{
    "id": "cfa8b438",
    "template_names": [],
    "wikitext": "<ref name = \"Hartmann1\" />",
    "type": "footnote",
    "footnote_subtype": "named",
    "flds": [],
    "urls": [],
    "templates": [],
    "titles": [],
    "section": "History",
    "served_from_cache": true
}
```

#### Known limitations

None

### PDF

the statistics/pdf endpoint accepts the following parameters:

* url (mandatory)
* refresh (bool, optional)
* testing (bool, optional)
* timeout (int, optional)
* debug (bool, optional) Note: you have to set refresh=true to be sure to get debug output

On error it returns 404 or 415. The first is when we could not find/fetch the url
and the second is when it is not a valid PDF.

If not given debug=true it will return json similar to:

```
{
    "words_mean": 213,
    "words_max": 842,
    "words_min": 41,
    "annotation_links": [
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://judiciary.house.gov/media/press-releases/chairman-jim-jordan-subpoenas-big-tech-executives",
            "page": 0
        },
        {
            "url": "https://rumble.com/v1gx8h7-dhss-foreign-to-domestic-disinformation-switcheroo.html",
            "page": 1
        },
        {
            "url": "https://web.archive.org/web/20230224163731/cisa.gov/mdm",
            "page": 3
        },
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformation",
            "page": 3
        },
        {
            "url": "https://report.foundationforfreedomonline.com/8-29-22.html",
            "page": 3
        }
    ],
    "links_from_original_text": [
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-",
            "page": 3
        }
    ],
    "links_from_text_without_linebreaks": [
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformationAll",
            "page": 3
        }
    ],
    "links_from_text_without_spaces": [
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-",
            "page": 3
        }
    ],
    "url": "https://www.foundationforfreedomonline.com/wp-content/uploads/2023/03/FFO-FLASH-REPORT-REV.pdf",
    "timeout": 2,
    "pages_total": 6,
    "detected_language": "en",
    "detected_language_error": false,
    "detected_language_error_details": "",
    "debug_text_original": {
        "1": "In this first screenshot, the MDM page describes how DHS used to only be involved in\ncensorship work against foreign-based social media opinions. Then, the Countering\nForeign Influence Task Force changed its name to generic \u201cMis, Dis and\nMalinformation,\u201d which included domestic-based social media opinions.\nfoundationforfreedomonline.org\n2\nF L A S H  R E P O R T\nFOUNDATION FOR\nFREEDOM ONLINE\nFFO has previously covered the Foreign-To-Domestic Censorship Switcheroo\ndescribed in this video found here.\nThe CISA site plainly stated it believed it could take action to neutralize domestic\nspeech online by classifying purveyors of domestic misinformation as \u201cdomestic threat\nactors\u201d on par with someone conducting a traditional cyber-attack.\n",
        "2": "foundationforfreedomonline.org\n3\nThe former CISA site went on to proudly tout its role in coordinating the private sector\ncensorship of domestic citizens\u2019 Covid-19 narratives as well:\nF L A S H  R E P O R T\nFOUNDATION FOR\nFREEDOM ONLINE\n",
        "3": "foundationforfreedomonline.org\n4\nBut sometime last week, between Friday, Feb. 24 at 4:37 p.m. and Sunday, Feb. 26\nat 5:55 a.m., CISA\u2019s once loud-and-proud declaration of long-arm jurisdiction over\ndomestic opinions online seems to have been walked back.\nThe site page for cisa.gov/mdm now redirects to a generic, foreign-only focused\ncounter-disinfo page:\nhttps://www.cisa.gov/topics/election-security/foreign-influence-operations-and-\ndisinformation\nAll references to the word or concept of \u201cdomestic\u201d inward-facing role of CISA have\nbeen carefully scrubbed:\nF L A S H  R E P O R T\nFOUNDATION FOR\nFREEDOM ONLINE\nFFO extensively covered CISA\u2019s domestic censorship of Covid-19 in this report.\nThis is how an obscure cybersecurity subagency tucked within DHS justified making\ncensorship instructional videos like the one pictured below.\n",
        "4": "foundationforfreedomonline.org\n5\nThe references to CISA\u2019s censorship of Covid and 2020 election claims have\ndisappeared as well.\nPerhaps CISA hopes to reverse what is now several years of outright government\ncensorship of domestic speech of American citizens. Or perhaps they are simply\nhoping no one will notice, or people will forget.\nF L A S H  R E P O R T\nFOUNDATION FOR\nFREEDOM ONLINE\nYou can see here the term \u201cdomestic threat actors\u201d has disappeared altogether:\n",
        "5": "The public-private domestic censorship operation coordinated by the federal\ngovernment has quietly been organized to quell the online opinions of everyday\nAmericans. Although DHS began to tout their coordination of such efforts publicly on\ntheir website, groups like Foundation for Freedom Online have exposed the\nbackbone of this taxpayer-funded domestic censorship apparatus. As a result, it is\nno surprise that DHS appears to be backtracking on the public display of their\ndomestic censorship efforts. \nCONCLUSION\nF L A S H  R E P O R T\nFOUNDATION FOR\nFREEDOM ONLINE\nfoundationforfreedomonline.org\n6\n"
    },
    "debug_text_without_linebreaks": {
        "0": "DHS Quietly Purges CISA \"Mis, Dis andMalinformation\" Website To RemoveDomestic Censorship ReferencesSince May 1, 2021, CISA.gov/mdm had stood with an open public declaration that itclassified domestic opinions deemed domestic \u201cmisinformation\u201d as an attack on\u201cdemocratic institutions,\u201d and therefore as a category of cyber threat to be neutralizedby DHS\u2019s cyber division, the Cybersecurity and Infrastructure Security Agency (CISA).Provided below are highlighted screenshots of CISA.gov/mdm snapped by theWayback Machine on May 1, 2021. foundationforfreedomonline.org1F L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINEKEY TAKEAWAYST H E  D E P A R T M E N T  O F  H O M E L A N DS E C U R I T Y \u2019 S( D H S )P R I M A R Y  C E N S O R S H I P  C O O R D I N A T I N GA G E N C YH A SQ U I E T L Y  P U R G E D  W H A T  F O R  T W O  Y E A R S  H A D  S T O O D  A S  AP U B L I C  C O N F E S S I O N  O F  T A R G E T I N G  U SC I T I Z E N S\u2013\u201c D O M E S T I C  T H R E A T  A C T O R S \u201d  \u2013  W H O  P O S T  \u201c M I S ,  D I S  O RM A L I N F O R M A T I O N \u201d  ( M D M )  O N  S O C I A L  M E D I A  A B O U T  C O V I D -1 9 ,  U S  E L E C T I O N  I S S U E S ,  A N D  O T H E R  C O N T R O V E R S I A LT O P I C S .A  F O U N D A T I O N  F O R  F R E E D O M  O N L I N E  I N V E S T I G A T I O NO F  W A Y B A C K  M A C H I N EA R C H I V E S  H A S  D E T E R M I N E DT H A T  L A T E  L A S T  W E E K ,  D H S  S C R U B B E D  A N D  R E -D I R E C T E D  A  L O N G S T A N D I N G  W E B S I T E  L I N K  T H A T  W A SH O M E  T O  T H E  D H S  C E N S O R S H I P  T E A M  T H A TC O O R D I N A T E S  P R I V A T ES E C T O R  \u201c C O U N T E R - D I S I N F O \u201dF I R M S  T O  M A S S - F L A G  S O C I A L  M E D I A  A C C O U N T S  U S I N GD H S \u2019 S  \u201c D O M E S T I C  D I S I N F O R M A T I O N  S W I T C H B O A R D . \u201dT H E  S C R U B B I N G  C O M E SA G A I N S T  T H E  B A C K D R O P  O FM O U N T I N G  P U B L I CA W A R E N E S SA N DP R O A C T I V EC O N G R E S S I O N A L  I N Q U I R Y  A N D  S U B P O E N A S  I N T O  T H EF E D E R A L  G O V E R N M E N T \u2019 S  R O L E  I N  D O M E S T I CC E N S O R S H I P1.2.3.FINDINGS",
        "1": "In this first screenshot, the MDM page describes how DHS used to only be involved incensorship work against foreign-based social media opinions. Then, the CounteringForeign Influence Task Force changed its name to generic \u201cMis, Dis andMalinformation,\u201d which included domestic-based social media opinions.foundationforfreedomonline.org2F L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINEFFO has previously covered the Foreign-To-Domestic Censorship Switcheroodescribed in this video found here.The CISA site plainly stated it believed it could take action to neutralize domesticspeech online by classifying purveyors of domestic misinformation as \u201cdomestic threatactors\u201d on par with someone conducting a traditional cyber-attack.",
        "2": "foundationforfreedomonline.org3The former CISA site went on to proudly tout its role in coordinating the private sectorcensorship of domestic citizens\u2019 Covid-19 narratives as well:F L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINE",
        "3": "foundationforfreedomonline.org4But sometime last week, between Friday, Feb. 24 at 4:37 p.m. and Sunday, Feb. 26at 5:55 a.m., CISA\u2019s once loud-and-proud declaration of long-arm jurisdiction overdomestic opinions online seems to have been walked back.The site page for cisa.gov/mdm now redirects to a generic, foreign-only focusedcounter-disinfo page:https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformationAll references to the word or concept of \u201cdomestic\u201d inward-facing role of CISA havebeen carefully scrubbed:F L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINEFFO extensively covered CISA\u2019s domestic censorship of Covid-19 in this report.This is how an obscure cybersecurity subagency tucked within DHS justified makingcensorship instructional videos like the one pictured below.",
        "4": "foundationforfreedomonline.org5The references to CISA\u2019s censorship of Covid and 2020 election claims havedisappeared as well.Perhaps CISA hopes to reverse what is now several years of outright governmentcensorship of domestic speech of American citizens. Or perhaps they are simplyhoping no one will notice, or people will forget.F L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINEYou can see here the term \u201cdomestic threat actors\u201d has disappeared altogether:",
        "5": "The public-private domestic censorship operation coordinated by the federalgovernment has quietly been organized to quell the online opinions of everydayAmericans. Although DHS began to tout their coordination of such efforts publicly ontheir website, groups like Foundation for Freedom Online have exposed thebackbone of this taxpayer-funded domestic censorship apparatus. As a result, it isno surprise that DHS appears to be backtracking on the public display of theirdomestic censorship efforts. CONCLUSIONF L A S H  R E P O R TFOUNDATION FORFREEDOM ONLINEfoundationforfreedomonline.org6"
    },
    "debug_text_without_spaces": {
        "2": "foundationforfreedomonline.org\n3\nTheformerCISAsitewentontoproudlytoutitsroleincoordinatingtheprivatesector\ncensorshipofdomesticcitizens\u2019Covid-19narrativesaswell:\nFLASHREPORT\nFOUNDATIONFOR\nFREEDOMONLINE\n",
        "3": "foundationforfreedomonline.org\n4\nButsometimelastweek,betweenFriday,Feb.24at4:37p.m.andSunday,Feb.26\nat5:55a.m.,CISA\u2019sonceloud-and-prouddeclarationoflong-armjurisdictionover\ndomesticopinionsonlineseemstohavebeenwalkedback.\nThesitepageforcisa.gov/mdmnowredirectstoageneric,foreign-onlyfocused\ncounter-disinfopage:\nhttps://www.cisa.gov/topics/election-security/foreign-influence-operations-and-\ndisinformation\nAllreferencestothewordorconceptof\u201cdomestic\u201dinward-facingroleofCISAhave\nbeencarefullyscrubbed:\nFLASHREPORT\nFOUNDATIONFOR\nFREEDOMONLINE\nFFOextensivelycoveredCISA\u2019sdomesticcensorshipofCovid-19inthisreport.\nThisishowanobscurecybersecuritysubagencytuckedwithinDHSjustifiedmaking\ncensorshipinstructionalvideosliketheonepicturedbelow.\n",
        "4": "foundationforfreedomonline.org\n5\nThereferencestoCISA\u2019scensorshipofCovidand2020electionclaimshave\ndisappearedaswell.\nPerhapsCISAhopestoreversewhatisnowseveralyearsofoutrightgovernment\ncensorshipofdomesticspeechofAmericancitizens.Orperhapstheyaresimply\nhopingnoonewillnotice,orpeoplewillforget.\nFLASHREPORT\nFOUNDATIONFOR\nFREEDOMONLINE\nYoucanseeheretheterm\u201cdomesticthreatactors\u201dhasdisappearedaltogether:\n",
        "5": "Thepublic-privatedomesticcensorshipoperationcoordinatedbythefederal\ngovernmenthasquietlybeenorganizedtoquelltheonlineopinionsofeveryday\nAmericans.AlthoughDHSbegantotouttheircoordinationofsucheffortspubliclyon\ntheirwebsite,groupslikeFoundationforFreedomOnlinehaveexposedthe\nbackboneofthistaxpayer-fundeddomesticcensorshipapparatus.Asaresult,itis\nnosurprisethatDHSappearstobebacktrackingonthepublicdisplayoftheir\ndomesticcensorshipefforts.\nCONCLUSION\nFLASHREPORT\nFOUNDATIONFOR\nFREEDOMONLINE\nfoundationforfreedomonline.org\n6\n"
    },
    "debug_url_annotations": {
        "0": [
            {
                "kind": 2,
                "xref": 130,
                "from": "Rect(112.01813507080078, 691.85791015625, 117.26372528076172, 706.8453369140625)",
                "uri": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 131,
                "from": "Rect(117.26372528076172, 691.85791015625, 192.20074462890625, 706.8453369140625)",
                "uri": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 132,
                "from": "Rect(347.7430419921875, 264.389404296875, 438.4168395996094, 277.8780517578125)",
                "uri": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 133,
                "from": "Rect(119.93448638916016, 294.3642578125, 361.231689453125, 307.8529052734375)",
                "uri": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 134,
                "from": "Rect(119.93448638916016, 579.2968139648438, 494.6195983886719, 594.2842407226562)",
                "uri": "https://judiciary.house.gov/media/press-releases/chairman-jim-jordan-subpoenas-big-tech-executives",
                "id": ""
            }
        ],
        "1": [
            {
                "kind": 2,
                "xref": 51,
                "from": "Rect(249.50668334960938, 665.026123046875, 281.7295837402344, 680.0134887695312)",
                "uri": "https://rumble.com/v1gx8h7-dhss-foreign-to-domestic-disinformation-switcheroo.html",
                "id": ""
            }
        ],
        "3": [
            {
                "kind": 2,
                "xref": 53,
                "from": "Rect(280.970703125, 459.9183654785156, 442.0852966308594, 474.90576171875)",
                "uri": "https://web.archive.org/web/20230224163731/cisa.gov/mdm",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 54,
                "from": "Rect(75.64327239990234, 575.3213500976562, 543.9996337890625, 606.794921875)",
                "uri": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformation",
                "id": ""
            },
            {
                "kind": 2,
                "xref": 55,
                "from": "Rect(460.0701904296875, 78.75225830078125, 535.756591796875, 93.73968505859375)",
                "uri": "https://report.foundationforfreedomonline.com/8-29-22.html",
                "id": ""
            }
        ]
    },
    "characters": 5161,
    "timestamp": 1685903956,
    "isodate": "2023-06-04T20:39:16.906306",
    "id": "a07f3f88",
    "refreshed_now": true
}
```

Using the debug and refresh parameter, all the text before and after cleaning is exposed as well as the link-annotations
before url extraction.

Note: Setting debug=true parameter without refresh=true will often not yield any debug output since we don't have it
stored in the cache.

This output permits the data consumer to count number of links per page, which links or domains appear most, number of
characters in the pdf, etc.

#### Known limitations

The extraction of URLs from unstructured text in any random PDF is a
difficult thing to do reliably. This is because
PDF is not a structured data format with clear boundaries between different type of information.

We currently use PyMuPDF to extract all the text as it appears on the page. 
We clean the text in various ways to get the links out via a regex. 
This approach results in some links containing information that was part of the
text after the link ended but we have yet to find a way to reliably determine 
the end boundary of links.

We are currently investigating if using the html output of PyMuPdf or 
using advanced Machine Learning could improve the output.

You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

### XHTML

the statistics/pdf endpoint accepts the following parameters:

* url (mandatory)
* refresh (optional)
* testing (optional)

On error it returns 400.

It will return json similar to:

```
{
    "links": [
        {
            "context": "<a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a>",
            "parent": "<p><a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a> The link contain inline markup (<code>&lt;acronym&gt;</code>), has a title and an accesskey \u2018t\u2019.</p>",
            "title": "The main page of this test suite",
            "href": "http://www.hut.fi/u/hsivonen/test/xhtml-suite/"
        },
        {
            "context": "<a href=\"base-target\">This is a relative link.</a>",
            "parent": "<p><a href=\"base-target\">This is a relative link.</a> If the link points to http://www.hut.fi/u/hsivonen/test/base-test/base-target, the user agent supports <code>&lt;base/&gt;</code>. if it points to http://www.hut.fi/u/hsivonen/test/xhtml-suite/base-target, the user agent has failed the test.</p>",
            "title": "",
            "href": "base-target"
        }
    ],
    "links_total": 2,
    "timestamp": 1682497512,
    "isodate": "2023-04-26T10:25:12.798840",
    "id": "fc5aa88d",
    "refreshed_now": false
}
```

#### Known limitations

None

# Installation

Clone the git repo:

`$ git clone https://github.com/internetarchive/iari.git && cd iari`

We recommend checking out the latest release before proceeding.

## Requirements

* python pip
* python gunicorn
* python poetry

## Setup

We use pip and poetry to set everything up.

`$ pip install poetry gunicorn && poetry install`

Lastly setup the directories for the json cache files

`$ ./setup_json_directories.sh`

## Run

Run these commands in different shells or in GNU screen.

Start GNU screen (if you want to have a persisting session)

`$ screen -D -RR`

### Development mode

Run it with
`$ ./run-debug-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:5000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

### Production mode

Run it with
`$ ./run-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:8000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

# Deployed instances

See [KNOWN_DEPLOYED_INSTANCES.md](KNOWN_DEPLOYED_INSTANCES.md)

# Diagrams

## IARI

### Components

![image](diagrams/components.png)

# History of this repo

* version 1.0.0 a proof of concept import tool based on WikidataIntegrator (by James Hare)
* version 2.0.0+ a scalable ETL-framework with an API and capability of reading EventStreams (by Dennis Priskorn)
* version 3.0.0+ WARI, a host of API endpoints that returns statistics
  about a Wikipedia article and its references. (by Dennis Priskorn)
* version 4.0.0+ IARI, a host of API endpoints that returns statistics
  about both Wikipedia articles and its references and can extract links from any PDF or XHTML page. (by Dennis Priskor

# License

This project is licensed under GPLv3+. Copyright Dennis Priskorn 2022
The diagram PNG files are CC0.

# Further reading and installation/setup

See the [development notes](DEVELOPMENT_NOTES.md)

# import json
# import requests
# import sys
# from wikidataintegrator import wdi_core, wdi_login
# from wikidataintegrator.wdi_config import config as wdi_config
# from config import *
#
# login = wdi_login.WDLogin(
#     user=user,
#     pwd=pwd,
#     mediawiki_api_url=mediawiki_api_url,
#     mediawiki_index_url=mediawiki_index_url)
#
# wdi_config['WIKIBASE_URL'] = wiki
# wdi_config['MEDIAWIKI_API_URL'] = mediawiki_api_url
# wdi_config['MEDIAWIKI_INDEX_URL'] = mediawiki_index_url
# wdi_config['SPARQL_ENDPOINT_URL'] = sparql_endpoint_url
#
# sparql_query = wdi_core.WDItemEngine.execute_sparql_query
#
# def get_enwiki_pageids(filename):
#     pageids = []
#     with open(filename) as f:
#         for line in f:
#             pageids.append(line.strip())
#     return pageids
#
# def get_wcd_item_id(pageid):
#     prefix = 'prefix wcd: <http://wikipediacitations.wiki.opencura.com/entity/> prefix wdt:
#     <http://www.wikidata.org/prop/direct/>'
#     q = f'select ?i where {{ ?i wdt:P1433 wcd:Q2 . ?i wdt:P9675 "{pageid}" . }}'
#
#     #lookup_stem = sparql_endpoint_url + '?format=json&query='
#     #lookup = lookup_stem + q
#     #print(f'QUERY URL: {lookup_stem}{urllib.parse.quote_plus(q)}')
#     #r = requests.get(lookup)
#
#     #try:
#     #    r = r.json()
#     #except Exception as e:
#     #    print(q)
#     #    print(r)
#     #    raise Exception(e)
#
#     #print(f'DEBUG: {prefix}\n{q}')
#
#     r = sparql_query(q, prefix=prefix, endpoint=sparql_endpoint_url)
#     if len(r['results']['bindings']) > 0:
#         return r['results']['bindings'][0]['i']['value']
#         .replace('http://wikipediacitations.wiki.opencura.com/entity/', '')
#     else:
#         return None
#
# def get_page_title(pageid):
#     q = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=&pageids={0}'
#     r = requests.get(q.format(pageid))
#     r = r.json()
#     try:
#         if 'missing' in r['query']['pages'][pageid]:
#             return None
#     except:
#         print(r)
#     try:
#         return r['query']['pages'][pageid]['title']
#     except:
#         print(r)
#
# def approve_new_item(wcd_qid):
#     if wcd_qid is None:
#         return True
#     return False
#
# def main(pageids):
#     for pageid in pageids:
#         wcd_qid = get_wcd_item_id(pageid)
#         #print(f'Page ID {pageid} corresponds to WCD QID {wcd_qid}')
#         #if wcd_qid is not None:
#         #    print(f'Page ID {pageid} has wcd:{wcd_qid}. Skipping.')
#         #    continue
#         title = get_page_title(pageid)
#         if title is None:
#             continue
#
#         itemdata =[]
#
#         # MediaWiki page ID (P9675)
#         itemdata.append(
#             wdi_core.WDString(value=pageid,
#                               prop_nr='P9675'))
#
#         # Title (P1476)
#         itemdata.append(
#             wdi_core.WDMonolingualText(value=title,
#                               language='en',
#                               prop_nr='P1476'))
#
#         # Published in (P1433): English Wikipedia (Q2)
#         itemdata.append(
#             wdi_core.WDItemID(value='Q2', prop_nr='P1433'))
#
#         # URL (P2699): page ID-based
#         itemdata.append(wdi_core.WDUrl(value='https://en.wikipedia.org/w/index.php?curid=' + pageid,
#                                 prop_nr='P2699'))
#
#         # URL (P2699): title-based
#         itemdata.append(wdi_core.WDUrl(value='https://en.wikipedia.org/wiki/' + title.replace(' ', '_'),
#                                 prop_nr='P2699'))
#
#         # Create the item!
#         item = wdi_core.WDItemEngine(
#             mediawiki_api_url=mediawiki_api_url,
#             sparql_endpoint_url=sparql_endpoint_url,
#             wikibase_url=wiki,
#             wd_item_id=wcd_qid,
#             new_item=approve_new_item(wcd_qid),
#             data=itemdata)
#
#             #fast_run=True,
#             #fast_run_base_filter={'P1433': 'Q2'})
#
#         # Label
#         item.set_label(title.strip()[:250])
#
#         # Description
#         item.set_description('article on English Wikipedia')
#
#         # Description
#         item.set_aliases(['enwiki#' + pageid])
#
#         try:
#             new_wb_id = item.write(login, bot_account=True)
#             print(new_wb_id)
#         except Exception as e:
#             print(e)
#
#
# if __name__ == '__main__':
#     pageids = get_enwiki_pageids(sys.argv[1])
#     main(pageids)

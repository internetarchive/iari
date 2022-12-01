from src import IASandboxWikibase, WorkQueue

wq = WorkQueue(wikibase=IASandboxWikibase())
wq.__setup_cache__()
wq.listen_to_queue()

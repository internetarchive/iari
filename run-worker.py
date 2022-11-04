from src import IASandboxWikibase, WorkQueue

wq = WorkQueue(wikibase=IASandboxWikibase())
wq.listen_to_queue()

from src import WorkQueue, SupportedWikibase

wq = WorkQueue(target_wikibase=SupportedWikibase.IASandboxWikibase)
wq.listen_to_queue()

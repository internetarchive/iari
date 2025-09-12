from pydantic import BaseModel

'''
This ensures each and every job (i.e. each endpoint) can handle a "refresh" and a "testing" url parameter
'''
class JobV2(BaseModel):
    refresh: bool = False
    testing: bool = False
    hydrate: bool = False

# Add wikibase property
* add entry in src/models/wikibase/dictionaries.py 
* run `$ python  setup_all_properties_and_items_on_new_wikibase.py -p`
* copy the new line with the property to both src/models/wikibase/ia_sandbox_wikibase.py and src/models/wikibase/ia_sandbox_wikibase.py
* update also src/models/wikibase/__init__.py
* populate the new property in src/models/wikibase/crud/__init__.py
* add tests for it
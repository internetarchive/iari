# Add wikibase property
* add entry in src/models/wikibase/dictionaries.py 
* run `$ python  setup_all_properties_and_items_on_new_wikibase.py -p`
* copy the new line with the property to the relevant model
* update also 
* populate the new property in src/models/wikibase/crud/__init__.py
* add test for it
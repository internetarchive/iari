# from typing import List
#
# from src import WcdBaseModel
# from src.models.wikibase import dictionaries
#
#
# class Properties(WcdBaseModel):
#     """This has all the logic needed for handling our properties"""
#
#     properties = {
#         **dictionaries.wcd_externalid_properties,
#         **dictionaries.wcd_item_properties,
#         **dictionaries.wcd_quantity_properties,
#         **dictionaries.wcd_string_properties,
#         **dictionaries.wcd_time_properties,
#         **dictionaries.wcd_url_properties,
#     }
#
#     def get_all_property_names(self) -> List[str]:
#         """Get all labels of properties formatted with underscore and uppercase"""
#         return [
#             str(wikibase_property_name) for wikibase_property_name in self.properties
#         ]
#
#     def get_all_property_labels(self) -> List[str]:
#         """Get all labels of properties formatted with space and titlecase"""
#         return [
#             str(wikibase_property_label.replace("_", " ").title())
#             for wikibase_property_label in self.properties
#         ]

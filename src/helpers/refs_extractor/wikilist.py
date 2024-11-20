import mwparserfromhell
# from .testcases.easter_island import wikitext
# from testcases.easter_island import wikitext

template_marker = "℻℻"
template_count = 0

def replace_templates_recursively(wikicode, templates, template_count):
    for template in wikicode.filter_templates(recursive=False):
        # Replace the innermost template with a placeholder
        template_id = f"{{{{{template_marker}_{template_count}}}}}"
        templates[template_id] = str(template)
        wikicode.replace(template, template_id)
        template_count += 1
    return wikicode, template_count

def extract_list_items(wikitext):
    global template_count
    wikicode = mwparserfromhell.parse(wikitext)
    list_items = []
    current_item = ""
    templates = {}

    # Step 1: Recursively replace templates with placeholders and store them
    wikicode, template_count = replace_templates_recursively(wikicode, templates, template_count)

    # Step 2: Extract list items
    lines = str(wikicode).split("\n")
    inside_list_item = False

    for line in lines:
        if line.startswith('*') or line.startswith('#'):
            if current_item:
                list_items.append(current_item)
            current_item = line
            inside_list_item = True
        elif inside_list_item and line.startswith(" "):
            current_item += "\n" + line  # Preserve the original formatting
        elif not line.startswith(" ") and not line.startswith('*') and not line.startswith('#'):
            inside_list_item = False
            if current_item:
                list_items.append(current_item)
                current_item = ""

    if current_item:
        list_items.append(current_item)

    # Step 3: Restore the templates back into the list items
    restored_items = []
    for item in list_items:
        for template_id, template_content in templates.items():
            item = item.replace(template_id, template_content)
        restored_items.append(item)

    return restored_items

# if __name__ == "__main__":
#     list_items = extract_list_items(wikitext)
#     for item in list_items:
#         print(item, end="\n\n")

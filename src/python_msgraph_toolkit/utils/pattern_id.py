import re

def is_id_type(value : str):
    """
    Returns the type of the value and returns:\n

    "sharepoint_id" for a sharepoint location ID\n
    "file_path" for a file path\n
    "url" for http 
    "unknown" for all other edge cases
    """
    # check is guid
    guid_pattern = re.compile(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    if guid_pattern.match(value):
        return 'sharepoint_id'

    # check is folder path
    if "/" in value:
        return 'file_path'

    # check is url
    if value.startswith('http') and "//" in value:
        return 'url'

    # else return unknown
    return "unknown"
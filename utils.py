def get_items_from_paginated_result(endpoint) -> list:
    result: dict = endpoint()
    items: list = result["items"]
    if result["totalPage"] > 1:
        for page_number in range(2, result["totalPage"] + 1):
            items.extend(endpoint(currentPage=page_number)["items"])
    return items

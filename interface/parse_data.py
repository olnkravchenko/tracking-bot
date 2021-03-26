def parse_category_equipment_data(source: list) -> str:
    """
    Parse data from category table from DB in format
    \nn. equipment_name
        \nowner
        \nholder
        \ndescrition
    """
    transformed_data = [f"<b>{i+1}. {value['name']}</b>\nВладелец техники @{value['owner']['username']}\nСейчас техника у @{value['holder']['username']}\nОписание: {value['description']}" for i, value in enumerate(source)]
    return '\n\n'.join(transformed_data), len(transformed_data)

from sqlmodel import SQLModel


def update_partially(item: SQLModel, new_data: SQLModel) -> SQLModel:
    new_data_dict = new_data.model_dump(
        exclude_defaults=True, exclude_none=True, exclude_unset=True
    )
    item_dict = item.model_dump()
    item_dict.update(**new_data_dict)
    return item.copy(update=item_dict)


def parse_integrity_error(err: str) -> str:
    err_messages = err.split("\n")
    for msg in err_messages:
        if msg.startswith("DETAIL"):
            return " " + msg.replace("DETAIL", "").strip(": \n")
    return ""

from pydantic import BaseModel, StringConstraints
from typing import Annotated


class ReceiptItem(BaseModel):
    shortDescription: Annotated[str, StringConstraints(min_length=1)]
    price: Annotated[str, StringConstraints(pattern=r'\d+.\d\d')]


class ReceiptsPayload(BaseModel):
    retailer: str
    purchaseDate: Annotated[str, StringConstraints(pattern=r'\d\d\d\d-\d\d-\d\d')]
    purchaseTime: Annotated[str, StringConstraints(pattern=r'\d\d:\d\d')]
    items: list[ReceiptItem]
    total: str

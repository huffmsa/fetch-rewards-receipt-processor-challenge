class DBObject():
    id: str
    points: int


class DB():
    receipts: dict[str, DBObject]

    def __init__(self):
        self.receipts = {}

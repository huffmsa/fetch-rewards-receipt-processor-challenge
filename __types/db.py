class DBObject():
    id: str
    points: int


class DB():
    receipts: dict[str, DBObject]
    receipts_cache: dict[str, str]
    def __init__(self):
        self.receipts = {}
        self.receipts_cache = {}

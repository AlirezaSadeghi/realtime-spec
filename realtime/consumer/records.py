import faust


class InteractionRecord(faust.Record):
    timestamp: str
    user: str
    action: str

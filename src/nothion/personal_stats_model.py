from attrs import define


@define
class PersonalStats:
    """Represents a personal stats row in Notion.

    Attributes:
        date: The date of the stats in format YYYY-MM-DD.
        work_time: Personal work time.
        leisure_time: Personal leisure time.
        focus_time: Personal focus time.
        weight: Personal weight.
    """
    date: str
    work_time: float
    leisure_time: float
    focus_time: float
    weight: float = 0.0

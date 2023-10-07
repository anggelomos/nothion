from attrs import define


@define
class TimeStats:
    """ Represents the time stats of a personal stats row in Notion.

    Attributes:
        work_time: Personal work time.
        leisure_time: Personal leisure time.
        focus_time: Personal focus time.
    """
    work_time: float
    leisure_time: float
    focus_time: float


@define
class PersonalStats:
    """Represents a personal stats row in Notion.

    Attributes:
        date: The date of the stats in format YYYY-MM-DD.
        time_stats: The time stats of the row.
        weight: Personal weight.
    """
    date: str
    time_stats: TimeStats
    weight: float = 0.0

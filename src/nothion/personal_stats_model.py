from attrs import define


@define
class PersonalStats:
    """Represents a personal stats row in Notion.

    Attributes:
        date: The date of the stats in format YYYY-MM-DD.
        all other attributes are self-explanatory.
    """
    date: str
    focus_total_time: float
    focus_active_time: float
    work_time: float
    leisure_time: float
    sleep_time_amount: float = 0.0
    fall_asleep_time: float = 0.0
    sleep_score: float = 0.0
    weight: float = 0.0
    steps: float = 0.0
    water_cups: int = 0

from attrs import define


@define
class PersonalStats:
    """Represents a personal stats row in Notion.

    Attributes:
        date: The date of the stats in format YYYY-MM-DD.
        all other attributes are self-explanatory.
    """
    date: str
    focus_total_time: float | None
    focus_personal_time: float | None
    focus_work_time: float | None
    work_time: float | None
    leisure_time: float | None
    sleep_time_amount: float | None = 0.0
    sleep_deep_amount: float | None = 0.0
    sleep_rem_amount: float | None = 0.0
    fall_asleep_time: float | None = 0.0
    sleep_score: float | None = 0.0
    weight: float | None = 0.0
    steps: float | None = 0.0
    water_cups: int | None = None

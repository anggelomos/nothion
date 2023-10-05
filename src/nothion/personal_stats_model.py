from attrs import define


@define
class TimeStats:
    work_time: float
    leisure_time: float
    focus_time: float


@define
class PersonalStats:
    date: str  # format: YYYY-MM-DD
    time_stats: TimeStats
    weight: float = 0.0

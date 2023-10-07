from attrs import define


@define
class ExpenseLog:
    """Represents a Ticktick task.

    Attributes:
        fecha: The title of the task, in format YYYY-MM-DD.
        egresos: The amount of money spent.
        producto: The product or service bought.
    """
    fecha: str
    egresos: float
    producto: str

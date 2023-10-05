from attrs import define


@define
class ExpenseLog:
    fecha: str
    egresos: float
    producto: str

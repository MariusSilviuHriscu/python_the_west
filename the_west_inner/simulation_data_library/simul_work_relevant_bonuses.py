import typing

class Work_bonuses:
    
    def __init__(self, product_drop: int = 0, item_drop: int = 0, exp_bonus: int = 0, salary_bonus: int = 0):
        self.product_drop = product_drop
        self.item_drop = item_drop
        self.exp_bonus = exp_bonus
        self.salary_bonus = salary_bonus
    
    def __add__(self, other: typing.Any) -> typing.Any:
        if not isinstance(other, Work_bonuses):
            raise TypeError("Addition operand must be of type 'Work_bonuses'")
        return Work_bonuses(
            product_drop=self.product_drop + other.product_drop,
            item_drop=self.item_drop + other.item_drop,
            exp_bonus=self.exp_bonus + other.exp_bonus,
            salary_bonus=self.salary_bonus + other.salary_bonus
        )
    
    def __mul__(self, other: int) -> typing.Any:
        if not isinstance(other, int):
            raise TypeError("Multiplication operand must be an integer")
        return Work_bonuses(
            product_drop=self.product_drop * other,
            item_drop=self.item_drop * other,
            exp_bonus=self.exp_bonus * other,
            salary_bonus=self.salary_bonus * other
        )
    def mult_bonus(self, attribute: str, factor: int | float) -> None:
        if attribute not in ["product_drop", "item_drop", "exp_bonus", "salary_bonus"]:
            raise ValueError("Invalid attribute name")
        if not isinstance(factor, (int, float)):
            raise TypeError("Factor must be an integer or float")
        setattr(self, attribute, getattr(self, attribute) * factor)
    def add_mult_attribute_list(self, attribute_list : typing.List[str], factor : typing.Union[int, float]) -> None:
        for attribute in attribute_list:
            self.mult_bonus(attribute, factor)
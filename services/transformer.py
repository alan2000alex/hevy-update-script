from enum import Enum


class CorrectionMode(str, Enum):
    divide = "divide"
    multiply = "multiply"


def transform_weight(weight_kg: float | None, mode: CorrectionMode) -> float | None:
    if weight_kg is None:
        return None
    if not isinstance(weight_kg, (int, float)):
        return weight_kg
    if weight_kg == 0:
        return 0.0
    if mode == CorrectionMode.divide:
        return round(weight_kg / 2, 4)
    return round(weight_kg * 2, 4)

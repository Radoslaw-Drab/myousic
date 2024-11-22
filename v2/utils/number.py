def clamp(value: int | float, minValue: int | float, maxValue: int | float):
  return max(min(value, maxValue), minValue)
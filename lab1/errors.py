class ColorError(Exception):
    """Базовое исключение для всех ошибок, связанных с цветом."""
    pass

class InvalidColorValueError(ColorError):
    """Вызывается, когда значение компоненты цвета выходит за допустимые границы."""
    def __init__(self, component: str, value: float, min_val: float, max_val: float):
        super().__init__(f"Компонента '{component}' имеет некорректное значение {value}. Допустимый диапазон: [{min_val}, {max_val}].")
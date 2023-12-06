class StatusNames(list):
    VALUES = [
        "Пользователь",
        "Администратор",
    ]

    def __init__(self):
        super().__init__(self.VALUES)

    @classmethod
    def get_value(cls, value_id: int = None):
        if value_id == 0:
            emoji = "👤"
        elif value_id == 1:
            emoji = "👨‍💻"
        else:
            emoji = "👤"

        return f"{emoji} {cls.VALUES[value_id]}"

class MenuParseError(Exception):
    def __init__(self, menu: str, message: str) -> None:
        self.menu = menu
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Error on parsing menu: {self.menu}\n{self.message}"

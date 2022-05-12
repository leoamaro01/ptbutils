class MenuParseError(Exception):
    def __init__(self, menu: str, message: str) -> None:
        self.menu = menu
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Error on parsing menu: {self.menu}\n{self.message}"


class PromptParseError(Exception):
    def __init__(self, prompt: str, message: str) -> None:
        self.prompt = prompt
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Error on parsing prompt: {self.prompt}\n{self.message}"

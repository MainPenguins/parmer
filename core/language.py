class Language:
    def __init__(self, code="auto"):
        self.code = code

    def is_auto(self):
        return self.code == "auto"

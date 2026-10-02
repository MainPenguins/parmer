class Checker:
    def __init__(self, engine=None):
        self.engine = engine

    def check(self, context):
        if not context.text.strip():
            return []

        if self.engine is None:
            return []

        return self.engine.check(
            context.text,
            language=context.language,
        )

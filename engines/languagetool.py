import requests

from core.suggestions import Suggestion


class LanguageToolEngine:
    def __init__(self):
        self.url = "https://api.languagetool.org/v2/check"

    def check(self, text, language="en-US"):
        if not text.strip():
            return []

        response = requests.post(
            self.url,
            data={
                "text": text,
                "language": language,
            },
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        suggestions = []

        for match in data.get("matches", []):
            replacements = [
                replacement["value"]
                for replacement in match.get("replacements", [])
            ]

            suggestions.append(
                Suggestion(
                    message=match.get("message", ""),
                    start=match["offset"],
                    end=match["offset"] + match["length"],
                    replacements=replacements,
                )
            )

        return suggestions

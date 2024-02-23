from pathlib import Path

import jinja2


DOC_PATH = Path("static/ENDPOINT.j2")
JINJA_ENV = jinja2.Environment()


def create(
    description: str, notes: list[str] | None = None, usage: str | None = None
) -> str:
    template = JINJA_ENV.from_string(DOC_PATH.read_text(encoding="utf-8"))
    text = template.render(description=description, restrictions=notes, usage=usage)
    return text

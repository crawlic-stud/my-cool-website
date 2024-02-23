from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str

    @classmethod
    def get_docs(cls, status_code: int, description: str | None = None):
        if description is not None:
            return {status_code: {"model": cls, "description": description}}
        return {status_code: {"model": cls}}

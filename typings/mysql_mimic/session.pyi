from typing import Any

from mysql_mimic.results import AllowedResult

class Query:
    expression: Any
    sql: str
    async def next(self) -> AllowedResult: ...

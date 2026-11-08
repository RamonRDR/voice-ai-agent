"""Small allowlist of real tools with Pydantic-validated arguments."""

import ast
import operator
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, ValidationError

from .errors import VoiceError
from .schemas import ToolExecution
from .sessions import SessionStore


class EmptyArgs(BaseModel):
    model_config = {"extra": "forbid"}


class CalculateArgs(BaseModel):
    model_config = {"extra": "forbid"}
    expression: str = Field(min_length=1, max_length=100)


class NoteArgs(BaseModel):
    model_config = {"extra": "forbid"}
    text: str = Field(min_length=1, max_length=250)


ARGUMENTS: dict[str, type[BaseModel]] = {
    "get_current_time": EmptyArgs,
    "calculate": CalculateArgs,
    "create_note": NoteArgs,
    "list_notes": EmptyArgs,
    "get_session_summary": EmptyArgs,
}

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_calculate(expression: str) -> str:
    try:
        root = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise VoiceError("Invalid arithmetic expression") from exc

    def walk(node: ast.AST, depth: int = 0) -> Decimal:
        if depth > 12:
            raise VoiceError("Arithmetic expression too complex")
        if isinstance(node, ast.Expression):
            return walk(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            val = walk(node.operand, depth + 1)
            return val if isinstance(node.op, ast.UAdd) else -val
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left = walk(node.left, depth + 1)
            right = walk(node.right, depth + 1)
            if abs(left) > 1_000_000_000 or abs(right) > 1_000_000_000:
                raise VoiceError("Operand exceeds permitted range")
            try:
                result = OPS[type(node.op)](left, right)
            except (ZeroDivisionError, InvalidOperation) as exc:
                raise VoiceError("Invalid arithmetic operation") from exc
            if not result.is_finite() or abs(result) > 1_000_000_000:
                raise VoiceError("Result exceeds permitted range")
            return result
        raise VoiceError("Only basic arithmetic operators are permitted")

    result = walk(root)
    if not result.is_finite() or abs(result) > 1_000_000_000:
        raise VoiceError("Result exceeds permitted range")
    return format(result.normalize(), "f")


class ToolRegistry:
    def __init__(self, store: SessionStore, timezone: str = "UTC") -> None:
        self.store = store
        try:
            self.timezone = ZoneInfo(timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Unrecognized timezone") from exc

    async def execute(
        self, name: str, arguments: dict[str, object], session_id: str
    ) -> ToolExecution:
        schema = ARGUMENTS.get(name)
        if schema is None:
            raise VoiceError("Tool is not permitted", status_code=403)
        try:
            params = schema.model_validate(arguments)
        except ValidationError as exc:
            raise VoiceError("Invalid tool arguments") from exc
        if name == "get_current_time":
            result: dict[str, object] = {
                "time": datetime.now(self.timezone).isoformat(),
                "timezone": str(self.timezone),
            }
        elif name == "calculate":
            assert isinstance(params, CalculateArgs)
            result = {"value": safe_calculate(params.expression)}
        elif name == "create_note":
            assert isinstance(params, NoteArgs)
            index = await self.store.add_note(session_id, params.text)
            result = {"created": True, "note_number": index}
        elif name == "list_notes":
            result = {"notes": await self.store.list_notes(session_id)}
        else:
            history = await self.store.history(session_id)
            result = {
                "turns": len(history) // 2,
                "recent_user_messages": [x.content[:100] for x in history if x.role == "user"][-3:],
            }
        return ToolExecution(name=name, ok=True, result=result)


TOOL_SPECS: list[dict[str, object]] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Read the current time in the configured timezone",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "maxLength": 100}},
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Save one short note for this session, after explicit user request",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "maxLength": 250}},
                "required": ["text"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "List notes saved in this session",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_summary",
            "description": "Summarize recent user interactions without inventing context",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]

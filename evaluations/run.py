"""Offline deterministic evaluation of the scripted router (not a model benchmark)."""

import asyncio
import json
from pathlib import Path

from voice_ai_agent.providers import RulesLLM


async def run() -> int:
    scenarios = json.loads((Path(__file__).parent / "scenarios.json").read_text())
    model = RulesLLM()
    assert len(scenarios) >= 20
    failures = []
    for item in scenarios:
        result = await model.respond(item["input"], [])
        success = (
            result.tool_name == item["expected_tool"]
            and (
                item["expected_phrase"] is None
                or item["expected_phrase"] in (result.content or "")
            )
        )
        if not success:
            failures.append(item["id"])
    print(json.dumps({
        "kind": "deterministic scripted-routing tests (not real STT, LLM or TTS)",
        "scenario_count": len(scenarios),
        "passed": len(scenarios) - len(failures),
        "failed": failures,
    }, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))

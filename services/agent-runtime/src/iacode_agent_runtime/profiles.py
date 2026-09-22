"""Agent and team profiles: what an agent is, and what a team does, as versioned configuration.

An **agent profile** is a role. It names the prompt template that gives the role its instructions,
the number of turns the role is allowed, the tool names it may ask for, and a default route. It is
not a model and not a provider: which model serves a turn is the gateway's decision, made from the
route or from the caller's explicit choice.

A **team profile** is an ordered list of stages. Each stage names an agent profile, the inputs it
receives and the name its output is stored under, so a later stage can refer to an earlier one's
result by name rather than by position. That is the whole language. There is no branching, no
condition and no loop, because Gate 2 has to *prove* a multi-agent run rather than provide a
workflow DSL, and every construct added now is a construct with no test behind it.

Nothing here composes a team dynamically. `docs/GATE-2-CHECKLIST.md` row 7.3 is explicit: a model
does not choose which agents run in this Gate, and a runtime that invented a team would be claiming
a capability it cannot evidence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.prompts import PromptTemplate, load_template

__all__ = [
    "AgentProfile",
    "TeamProfile",
    "TeamStage",
    "definition_hash",
    "load_agent_profile",
    "load_team_profile",
]

#: What a stage may name as an input. ``task`` is the original instruction; anything else must be
#: the output name of an earlier stage, which :meth:`TeamProfile.validate` checks.
TASK_INPUT = "task"

PROFILE_SCHEMA_VERSION = "1.0.0"


def definition_hash(payload: dict[str, Any]) -> str:
    """A stable digest of a definition, so a bootstrap can tell "unchanged" from "edited"."""
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AgentProfile:
    """One agent role, loaded and validated."""

    agent: str
    name: str
    role: str
    description: str
    version: str
    template: PromptTemplate
    default_route: str | None = None
    max_turns: int = 4
    allowed_actions: tuple[str, ...] = ()
    enabled: bool = True
    source_path: str = ""
    definition_digest: str = ""

    def permits(self, tool_name: str) -> bool:
        """Whether this role may ask for a tool.

        The default is an empty set, which permits nothing. A role that has not been given a tool
        cannot acquire one by asking, and in this Gate no builtin profile is given one at all —
        the tool lifecycle is exercised by fixtures, because Gate 2 executes nothing.
        """
        return tool_name in self.allowed_actions

    def summary(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "version": self.version,
            "defaultRoute": self.default_route,
            "maxTurns": self.max_turns,
            "allowedActions": list(self.allowed_actions),
            "promptTemplate": self.template.path,
            "promptTemplateVersion": self.template.version,
            "promptTemplateHash": self.template.content_hash,
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class TeamStage:
    """One step of a team: who runs, what they are given, and what their answer is called."""

    index: int
    name: str
    agent: str
    inputs: tuple[str, ...] = (TASK_INPUT,)
    output_name: str = "output"

    def summary(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "agent": self.agent,
            "inputs": list(self.inputs),
            "outputName": self.output_name,
        }


@dataclass(frozen=True)
class TeamProfile:
    """An ordered, versioned team."""

    team: str
    name: str
    description: str
    version: str
    stages: tuple[TeamStage, ...]
    enabled: bool = True
    source_path: str = ""
    definition_digest: str = ""

    def validate(self) -> None:
        """Refuse a team that cannot execute, before a run is created rather than during one."""
        if not self.stages:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"team {self.team!r} declares no stage",
                details={"team": self.team})
        produced = {TASK_INPUT}
        names: set[str] = set()
        for stage in self.stages:
            if stage.name in names:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_REQUEST,
                    f"team {self.team!r} declares two stages named {stage.name!r}",
                    details={"team": self.team, "stage": stage.name})
            names.add(stage.name)
            missing = [item for item in stage.inputs if item not in produced]
            if missing:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_REQUEST,
                    f"stage {stage.name!r} of team {self.team!r} reads "
                    f"{', '.join(missing)}, which no earlier stage produces",
                    details={"team": self.team, "stage": stage.name})
            produced.add(stage.output_name)

    def summary(self) -> dict[str, Any]:
        return {
            "team": self.team,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "stages": [stage.summary() for stage in self.stages],
        }


def _require(payload: dict[str, Any], key: str, path: Path) -> Any:
    if key not in payload:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} declares no {key!r}",
            details={"definition": path.name})
    return payload[key]


def _read_definition(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} is not valid JSON: {error.msg}",
            details={"definition": path.name}) from error
    if not isinstance(payload, dict):
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} must declare an object",
            details={"definition": path.name})
    declared = payload.get("schemaVersion")
    if declared != PROFILE_SCHEMA_VERSION:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} declares schemaVersion {declared!r}, not {PROFILE_SCHEMA_VERSION!r}",
            details={"definition": path.name})
    return payload


def load_agent_profile(root: Path, path: Path) -> AgentProfile:
    """Read and validate one agent profile."""
    payload = _read_definition(path)
    template = load_template(root, str(_require(payload, "promptTemplate", path)))
    actions = tuple(str(item) for item in payload.get("allowedActions") or ())
    max_turns = int(payload.get("maxTurns", 4))
    if max_turns < 1:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} declares maxTurns {max_turns}, which would execute nothing",
            details={"definition": path.name})
    profile = AgentProfile(
        agent=str(_require(payload, "agent", path)),
        name=str(_require(payload, "name", path)),
        role=str(_require(payload, "role", path)),
        description=str(payload.get("description", "")),
        version=str(_require(payload, "version", path)),
        template=template,
        default_route=payload.get("defaultRoute"),
        max_turns=max_turns,
        allowed_actions=actions,
        enabled=bool(payload.get("enabled", True)),
        source_path=str(path.relative_to(root)).replace("\\", "/"),
        definition_digest=definition_hash(payload),
    )
    if profile.agent != path.stem:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} declares agent {profile.agent!r}; the file name must match it",
            details={"definition": path.name})
    return profile


def load_team_profile(root: Path, path: Path) -> TeamProfile:
    """Read and validate one team profile."""
    payload = _read_definition(path)
    raw_stages = _require(payload, "stages", path)
    if not isinstance(raw_stages, list):
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} must declare stages as a list",
            details={"definition": path.name})
    stages: list[TeamStage] = []
    for index, item in enumerate(raw_stages):
        if not isinstance(item, dict):
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"stage {index} of {path.name} is not an object",
                details={"definition": path.name})
        stages.append(TeamStage(
            index=index,
            name=str(item.get("name") or item.get("agent") or f"stage-{index}"),
            agent=str(_require(item, "agent", path)),
            inputs=tuple(str(value) for value in item.get("inputs") or (TASK_INPUT,)),
            output_name=str(item.get("outputName") or "output"),
        ))
    team = TeamProfile(
        team=str(_require(payload, "team", path)),
        name=str(_require(payload, "name", path)),
        description=str(payload.get("description", "")),
        version=str(_require(payload, "version", path)),
        stages=tuple(stages),
        enabled=bool(payload.get("enabled", True)),
        source_path=str(path.relative_to(root)).replace("\\", "/"),
        definition_digest=definition_hash(payload),
    )
    if team.team != path.stem:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"{path.name} declares team {team.team!r}; the file name must match it",
            details={"definition": path.name})
    team.validate()
    return team


@dataclass
class ProfileSet:
    """Everything the registry loaded, kept together so a caller resolves both from one object."""

    agents: dict[str, AgentProfile] = field(default_factory=dict)
    teams: dict[str, TeamProfile] = field(default_factory=dict)

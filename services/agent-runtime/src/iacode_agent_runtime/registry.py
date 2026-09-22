"""The registry: which agents and which teams this repository declares.

Definitions live in ``agents/`` — profiles in ``agents/profiles/``, teams in ``agents/teams/`` and
prompt templates in ``agents/prompts/``. The registry reads them, validates them together (a team
that names an agent nobody declares is refused here, not discovered mid-run) and caches the result
by the modification time of the directory tree, so an operator who edits a profile sees the change
without restarting the process.

Bootstrapping into the database is separate and idempotent. It writes a row when there is none,
updates a row whose definition digest has changed, and **leaves a customised row alone**: an
operator who edited a profile in the database did so on purpose, and a start-up that silently
reverted it would be a start-up that loses work. The delta is returned rather than logged, so a
caller can assert that running it twice changes nothing the second time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.profiles import (
    AgentProfile,
    TeamProfile,
    load_agent_profile,
    load_team_profile,
)

__all__ = ["AgentRegistry", "BootstrapOutcome", "ProfileRecord", "TeamRecord"]

PROFILE_DIRECTORY = Path("agents") / "profiles"
TEAM_DIRECTORY = Path("agents") / "teams"


@dataclass(frozen=True)
class ProfileRecord:
    """An agent profile as a store keeps it."""

    agent: str
    name: str
    role: str
    description: str
    version: str
    role_contract: str
    default_route: str | None
    max_turns: int
    allowed_actions: tuple[str, ...]
    prompt_template: str
    prompt_template_version: str
    prompt_template_hash: str
    definition_hash: str
    enabled: bool


@dataclass(frozen=True)
class TeamRecord:
    """A team profile as a store keeps it."""

    team: str
    name: str
    description: str
    version: str
    stages: tuple[dict[str, Any], ...]
    definition_hash: str
    enabled: bool


@dataclass(frozen=True)
class BootstrapOutcome:
    """What one bootstrap changed. An idempotent second run returns all zeros."""

    agents_created: int = 0
    agents_updated: int = 0
    agents_unchanged: int = 0
    agents_customised: int = 0
    teams_created: int = 0
    teams_updated: int = 0
    teams_unchanged: int = 0
    teams_customised: int = 0

    @property
    def changed(self) -> bool:
        return bool(self.agents_created or self.agents_updated
                    or self.teams_created or self.teams_updated)

    def to_dict(self) -> dict[str, int]:
        return {
            "agentsCreated": self.agents_created,
            "agentsUpdated": self.agents_updated,
            "agentsUnchanged": self.agents_unchanged,
            "agentsCustomised": self.agents_customised,
            "teamsCreated": self.teams_created,
            "teamsUpdated": self.teams_updated,
            "teamsUnchanged": self.teams_unchanged,
            "teamsCustomised": self.teams_customised,
        }


class AgentRegistry:
    """Every declared agent and team, loaded from the repository."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._agents: dict[str, AgentProfile] | None = None
        self._teams: dict[str, TeamProfile] | None = None
        self._fingerprint: tuple[tuple[str, float], ...] | None = None

    # -- loading -------------------------------------------------------------------------------

    def _tree_fingerprint(self) -> tuple[tuple[str, float], ...]:
        """Modification times of every definition, so an edit invalidates the cache.

        A timestamp is a weak freshness signal in general; here it answers a narrower question —
        "has a file on this disk been written since we read it" — which is exactly what a
        modification time is for.
        """
        entries: list[tuple[str, float]] = []
        for directory in (PROFILE_DIRECTORY, TEAM_DIRECTORY, Path("agents") / "prompts"):
            base = self._root / directory
            if not base.is_dir():
                continue
            for path in sorted(base.iterdir()):
                if path.is_file():
                    entries.append((str(path), path.stat().st_mtime))
        return tuple(entries)

    def _load(self) -> None:
        fingerprint = self._tree_fingerprint()
        if self._agents is not None and self._teams is not None \
                and fingerprint == self._fingerprint:
            return

        agents: dict[str, AgentProfile] = {}
        directory = self._root / PROFILE_DIRECTORY
        if not directory.is_dir():
            raise AgentRuntimeError(
                AgentRuntimeErrorType.PROFILE_NOT_FOUND,
                f"no agent profile directory at {PROFILE_DIRECTORY.as_posix()}",
                details={"directory": PROFILE_DIRECTORY.as_posix()})
        for path in sorted(directory.glob("*.json")):
            profile = load_agent_profile(self._root, path)
            agents[profile.agent] = profile

        teams: dict[str, TeamProfile] = {}
        team_directory = self._root / TEAM_DIRECTORY
        if not team_directory.is_dir():
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TEAM_NOT_FOUND,
                f"no team profile directory at {TEAM_DIRECTORY.as_posix()}",
                details={"directory": TEAM_DIRECTORY.as_posix()})
        for path in sorted(team_directory.glob("*.json")):
            team = load_team_profile(self._root, path)
            for stage in team.stages:
                if stage.agent not in agents:
                    raise AgentRuntimeError(
                        AgentRuntimeErrorType.PROFILE_NOT_FOUND,
                        f"team {team.team!r} stage {stage.name!r} names agent "
                        f"{stage.agent!r}, which no profile declares",
                        details={"team": team.team, "agent": stage.agent})
            teams[team.team] = team

        self._agents = agents
        self._teams = teams
        self._fingerprint = fingerprint

    # -- reading -------------------------------------------------------------------------------

    def agents(self) -> dict[str, AgentProfile]:
        self._load()
        assert self._agents is not None
        return dict(self._agents)

    def teams(self) -> dict[str, TeamProfile]:
        self._load()
        assert self._teams is not None
        return dict(self._teams)

    def agent(self, slug: str) -> AgentProfile:
        profiles = self.agents()
        if slug not in profiles:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.PROFILE_NOT_FOUND,
                f"no agent profile named {slug!r}",
                details={"agent": slug, "available": sorted(profiles)})
        return profiles[slug]

    def team(self, slug: str) -> TeamProfile:
        teams = self.teams()
        if slug not in teams:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TEAM_NOT_FOUND,
                f"no team profile named {slug!r}",
                details={"team": slug, "available": sorted(teams)})
        team = teams[slug]
        if not team.enabled:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TEAM_NOT_FOUND,
                f"team {slug!r} is disabled",
                details={"team": slug})
        return team

    # -- records a store can persist -----------------------------------------------------------

    def agent_records(self) -> list[ProfileRecord]:
        return [
            ProfileRecord(
                agent=profile.agent,
                name=profile.name,
                role=profile.role,
                description=profile.description,
                version=profile.version,
                role_contract=profile.source_path,
                default_route=profile.default_route,
                max_turns=profile.max_turns,
                allowed_actions=profile.allowed_actions,
                prompt_template=profile.template.path,
                prompt_template_version=profile.template.version,
                prompt_template_hash=profile.template.content_hash,
                definition_hash=profile.definition_digest,
                enabled=profile.enabled,
            )
            for profile in sorted(self.agents().values(), key=lambda item: item.agent)
        ]

    def team_records(self) -> list[TeamRecord]:
        return [
            TeamRecord(
                team=team.team,
                name=team.name,
                description=team.description,
                version=team.version,
                stages=tuple(stage.summary() for stage in team.stages),
                definition_hash=team.definition_digest,
                enabled=team.enabled,
            )
            for team in sorted(self.teams().values(), key=lambda item: item.team)
        ]

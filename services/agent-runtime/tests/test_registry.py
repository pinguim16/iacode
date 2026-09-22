"""The declared agents, the declared teams and the versioned prompts that instruct them."""

from __future__ import annotations

import json

import pytest
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.profiles import (
    TeamProfile,
    TeamStage,
    load_agent_profile,
    load_team_profile,
)
from iacode_agent_runtime.prompts import load_template, template_version
from iacode_agent_runtime.registry import AgentRegistry
from runtime_doubles import repository_root

ROOT = repository_root()

#: The four the Gate needs to prove the runtime. A profile for a capability this Gate does not
#: exercise would be configuration with nothing behind it.
DECLARED_AGENTS = {"engineering-lead", "generalist", "planner", "reviewer"}
DECLARED_TEAMS = {"single-agent", "planner-reviewer"}


def registry() -> AgentRegistry:
    return AgentRegistry(ROOT)


class AgentProfileContractTests:
    """A profile is a versioned role with a prompt, a turn limit and permitted actions."""

    def test_every_declared_field_is_present(self) -> None:
        profile = registry().agent("planner")
        summary = profile.summary()
        assert set(summary) == {
            "agent", "name", "role", "description", "version", "defaultRoute", "maxTurns",
            "allowedActions", "promptTemplate", "promptTemplateVersion", "promptTemplateHash",
            "enabled"}
        assert summary["version"]
        assert summary["maxTurns"] >= 1

    def test_a_profile_names_no_provider_and_no_model(self) -> None:
        """A role is not a model. Which model serves a turn is the gateway's decision."""
        for profile in registry().agents().values():
            body = json.dumps(profile.summary()).lower()
            for forbidden in ("openai", "anthropic", "devworld", "gpt-", "claude-", "gemini"):
                assert forbidden not in body, f"{profile.agent} names {forbidden}"

    def test_a_profile_permits_nothing_by_default(self) -> None:
        profile = registry().agent("generalist")
        assert profile.allowed_actions == ()
        assert not profile.permits("shell.exec")

    def test_a_malformed_profile_is_refused_when_it_is_loaded(self, tmp_path) -> None:
        path = tmp_path / "broken.json"
        path.write_text(json.dumps({"schemaVersion": "1.0.0", "agent": "broken"}),
                        encoding="utf-8")
        with pytest.raises(AgentRuntimeError):
            load_agent_profile(tmp_path, path)

    def test_a_profile_whose_name_disagrees_with_its_file_is_refused(self, tmp_path) -> None:
        (tmp_path / "agents" / "prompts").mkdir(parents=True)
        (tmp_path / "agents" / "prompts" / "x.v1.md").write_text("# {role}\n{description}\n",
                                                                 encoding="utf-8")
        path = tmp_path / "mismatched.json"
        path.write_text(json.dumps({
            "schemaVersion": "1.0.0", "agent": "other", "name": "Other", "role": "other",
            "version": "1.0.0", "promptTemplate": "agents/prompts/x.v1.md"}), encoding="utf-8")
        with pytest.raises(AgentRuntimeError):
            load_agent_profile(tmp_path, path)


def test_builtin_profiles_are_exactly_the_declared_set() -> None:
    assert set(registry().agents()) == DECLARED_AGENTS


class TeamProfileContractTests:
    """A team is an ordered list of stages with input mappings and output names."""

    def test_a_team_declares_ordered_stages(self) -> None:
        team = registry().team("planner-reviewer")
        assert [stage.name for stage in team.stages] == ["plan", "review"]
        assert [stage.index for stage in team.stages] == [0, 1]
        assert team.stages[1].inputs == ("task", "plan")
        assert team.stages[0].output_name == "plan"

    def test_a_stage_reading_an_output_nobody_produces_is_refused(self) -> None:
        team = TeamProfile(
            team="broken", name="Broken", description="", version="1.0.0",
            stages=(TeamStage(index=0, name="review", agent="reviewer",
                              inputs=("task", "plan"), output_name="review"),))
        with pytest.raises(AgentRuntimeError) as raised:
            team.validate()
        assert "no earlier stage produces" in raised.value.message

    def test_a_team_with_no_stage_is_refused(self) -> None:
        with pytest.raises(AgentRuntimeError):
            TeamProfile(team="empty", name="Empty", description="", version="1.0.0",
                        stages=()).validate()

    def test_two_stages_may_not_share_a_name(self) -> None:
        team = TeamProfile(
            team="twice", name="Twice", description="", version="1.0.0",
            stages=(TeamStage(index=0, name="plan", agent="planner", output_name="a"),
                    TeamStage(index=1, name="plan", agent="planner", output_name="b")))
        with pytest.raises(AgentRuntimeError):
            team.validate()

    def test_a_malformed_team_is_refused_when_it_is_loaded(self, tmp_path) -> None:
        path = tmp_path / "broken.json"
        path.write_text(json.dumps({"schemaVersion": "1.0.0", "team": "broken"}),
                        encoding="utf-8")
        with pytest.raises(AgentRuntimeError):
            load_team_profile(tmp_path, path)


def test_builtin_teams_are_the_declared_set() -> None:
    assert set(registry().teams()) == DECLARED_TEAMS


def test_team_composition_is_not_inferred() -> None:
    """No model decides which agents run, and nothing generates a team.

    Read from the installed module rather than from a path, so the check holds wherever the suite
    runs: a module that composed a team from a model's answer would have to reach for the model
    client, and neither of these does.
    """
    import inspect

    from iacode_agent_runtime import profiles as profiles_module
    from iacode_agent_runtime import registry as registry_module

    for module in (profiles_module, registry_module):
        source = inspect.getsource(module)
        for forbidden in ("ModelClient", "gateway_client", "model_client"):
            assert forbidden not in source, (
                f"{module.__name__} reaches for a model to decide a team")

    # And the declared teams are literally what the repository declares, in order.
    assert [stage.agent for stage in registry().team("planner-reviewer").stages] == [
        "planner", "reviewer"]


class AgentRegistryTests:
    """Profiles and teams are loaded, validated together and enumerable."""

    def test_the_registry_enumerates_both(self) -> None:
        assert set(registry().agents()) == DECLARED_AGENTS
        assert set(registry().teams()) == DECLARED_TEAMS

    def test_every_team_stage_names_a_declared_agent(self) -> None:
        instance = registry()
        agents = set(instance.agents())
        for team in instance.teams().values():
            for stage in team.stages:
                assert stage.agent in agents

    def test_an_unknown_agent_is_refused_rather_than_discovered_mid_run(self) -> None:
        with pytest.raises(AgentRuntimeError) as raised:
            registry().agent("nobody")
        assert raised.value.error_type is AgentRuntimeErrorType.PROFILE_NOT_FOUND

    def test_an_unknown_team_is_refused(self) -> None:
        with pytest.raises(AgentRuntimeError) as raised:
            registry().team("nobody")
        assert raised.value.error_type is AgentRuntimeErrorType.TEAM_NOT_FOUND

    def test_records_are_stable_between_reads(self) -> None:
        """The definition digest is what makes a bootstrap idempotent; it must not drift."""
        first = {record.agent: record.definition_hash for record in registry().agent_records()}
        second = {record.agent: record.definition_hash for record in registry().agent_records()}
        assert first == second
        assert all(len(value) == 64 for value in first.values())


def test_prompts_are_versioned_files() -> None:
    """Not strings concatenated across the code: a file, named for its version, with a hash."""
    for profile in registry().agents().values():
        template = profile.template
        assert template.path.startswith("agents/prompts/")
        assert template.path.endswith(".md")
        assert template.version == template_version(template.path)
        assert len(template.content_hash) == 64
        assert template.body.strip()


def test_a_template_placeholder_must_be_supplied_and_must_be_used() -> None:
    template = registry().agent("planner").template
    assert set(template.placeholders) == {"role", "description"}
    with pytest.raises(AgentRuntimeError):
        template.render(role="planner")
    with pytest.raises(AgentRuntimeError):
        template.render(role="planner", description="d", extra="x")
    rendered = template.render(role="planner", description="d")
    assert "{role}" not in rendered


def test_a_template_outside_the_repository_is_refused(tmp_path) -> None:
    """A profile that named ../../infra/compose/.env would otherwise read a credential."""
    with pytest.raises(AgentRuntimeError):
        load_template(tmp_path, "../../etc/passwd")


def test_a_template_with_no_version_in_its_name_is_refused(tmp_path) -> None:
    (tmp_path / "prompt.md").write_text("body", encoding="utf-8")
    with pytest.raises(AgentRuntimeError):
        load_template(tmp_path, "prompt.md")


def test_an_absent_template_is_refused(tmp_path) -> None:
    with pytest.raises(AgentRuntimeError) as raised:
        load_template(tmp_path, "missing.v1.md")
    assert raised.value.error_type is AgentRuntimeErrorType.PROFILE_NOT_FOUND

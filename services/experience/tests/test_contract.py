"""Strict ingress/privacy/identity controls; every adverse case has a valid adjacent control."""

from __future__ import annotations

import base64
import json
from dataclasses import replace
from datetime import timedelta

import pytest
from iacode_experience import domain
from iacode_experience.domain import (
    ExperienceError,
    ExperienceService,
    StoredExperience,
    canonical,
    digest,
    parse_capture,
    parse_json,
    require_safe,
    validate_document,
)
from pydantic import ValidationError


def capture_value(body: dict) -> dict:
    return {
        "taskRunId": body["task"]["runId"],
        "storageConsent": True,
        "idempotencyKey": body["task"]["runId"],
    }


def test_exact_closed_roundtrip(policy, body):
    document = validate_document(body, policy)
    assert document.model_dump(mode="json") == body
    assert document.quality is document.effort is document.repository is document.baseCommit is None
    assert document.humanReview is document.agentReview is None
    assert document.trainingEligibility.eligible is False


def test_consent_missing_has_distinct_code(policy, body):
    value = capture_value(body)
    del value["storageConsent"]
    with pytest.raises(ExperienceError, match="operation refused") as caught:
        parse_capture(canonical(value), policy)
    assert caught.value.code == "CONSENT_MISSING"


def test_consent_wrong_type_is_not_truthiness(policy, body):
    value = {**capture_value(body), "storageConsent": 1}
    with pytest.raises(ExperienceError) as caught:
        parse_capture(canonical(value), policy)
    assert caught.value.code == "CONSENT_TYPE_INVALID"


def test_consent_rejected_has_distinct_code(policy, body):
    value = {**capture_value(body), "storageConsent": False}
    with pytest.raises(ExperienceError) as caught:
        parse_capture(canonical(value), policy)
    assert caught.value.code == "CONSENT_DENIED"


def test_caller_body_and_verdict_are_not_ingress(policy, body):
    for field in ("body", "verdict", "provenance", "trainingAllowed", "reasoning", "annotations"):
        with pytest.raises(ExperienceError) as caught:
            parse_capture(canonical({**capture_value(body), field: "untrusted"}), policy)
        assert caught.value.code == "CAPTURE_CONTRACT_INVALID"
    assert parse_capture(canonical(capture_value(body)), policy).storageConsent is True


def test_duplicate_json_refused():
    with pytest.raises(ExperienceError) as caught:
        parse_json(b'{"storageConsent":false,"storageConsent":true}', 4096)
    assert caught.value.code == "JSON_DUPLICATE_KEY"


def test_nonfinite_json_refused():
    for text in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
        with pytest.raises(ExperienceError) as caught:
            parse_json(text, 4096)
        assert caught.value.code == "JSON_NONFINITE"


def test_utf8_and_surrogate_refused():
    for text in (b'{"x":"\xff"}', b'{"x":"\\ud800"}'):
        with pytest.raises(ExperienceError) as caught:
            parse_json(text, 4096)
        assert caught.value.code == "JSON_INVALID"


def test_depth_and_size_are_bounded():
    with pytest.raises(ExperienceError) as caught:
        parse_json(b'{"x":' * 14 + b"0" + b"}" * 14, 4096)
    assert caught.value.code == "CONTENT_DEPTH_INVALID"
    with pytest.raises(ExperienceError) as caught:
        parse_json(b'{"x":"' + b"a" * 4096 + b'"}', 4096)
    assert caught.value.code == "CONTENT_TOO_LARGE"


def test_private_nested_field_refused(policy, body):
    body["task"]["chain_of_thought"] = "not an observable fact"
    with pytest.raises(ExperienceError) as caught:
        validate_document(body, policy)
    assert caught.value.code == "STORED_CONTRACT_INVALID"


def test_permissions_require_exact_boolean(policy, body):
    body["provenance"][0]["trainingAllowed"] = 0
    with pytest.raises(ExperienceError):
        validate_document(body, policy)


def test_unverified_cannot_grant_reuse(policy, body):
    body["provenance"][0]["trainingAllowed"] = True
    with pytest.raises(ExperienceError):
        validate_document(body, policy)


def test_unobserved_effort_is_not_fabricated(policy, body):
    body["effort"] = "xhigh"
    with pytest.raises(ExperienceError):
        validate_document(body, policy)


def test_naive_and_backwards_source_time_refused(policy, body):
    body["task"]["finishedAt"] = "2026-10-16T00:00:00"
    with pytest.raises(ExperienceError):
        validate_document(body, policy)
    body["task"]["finishedAt"] = "2026-10-16T00:00:00Z"
    with pytest.raises(ExperienceError):
        validate_document(body, policy)


def test_provenance_cannot_name_another_task(policy, body):
    body["provenance"][0]["sourceId"] = body["task"]["taskId"]
    with pytest.raises(ExperienceError):
        validate_document(body, policy)


def test_provenance_digest_is_verified(policy, body):
    body["provenance"][0]["digest"] = "f" * 64
    with pytest.raises(ExperienceError) as caught:
        validate_document(body, policy)
    assert caught.value.code == "PROVENANCE_DIGEST_INVALID"


def test_secret_canonical_detector_and_encoded_views(policy, body):
    marker = "gh" + "p_" + "q" * 24
    for text in (marker, base64.b64encode(marker.encode()).decode()):
        body["trajectorySummary"] = text
        with pytest.raises(ExperienceError) as caught:
            validate_document(body, policy)
        assert caught.value.code == "SECRET_MATERIAL_REFUSED"


def test_known_opaque_capability_refused_in_declared_forms():
    marker = "opaque-" + "ab42" * 8
    forms = [
        marker,
        marker.upper(),
        marker.encode().hex(),
        base64.b64encode(marker.encode()).decode(),
        "".join(f"%{b:02x}" for b in marker.encode()),
        "".join(f"\\u{b:04x}" for b in marker.encode()),
    ]
    for form in forms:
        with pytest.raises(ExperienceError) as caught:
            require_safe(form.encode(), (marker,))
        assert caught.value.code == "AUTHORIZATION_MATERIAL_REFUSED"
    require_safe(b'{"safe":"observable fact"}', (marker,))


def test_scanner_failure_is_sanitized_and_closed(monkeypatch):
    def failure(_text):
        raise RuntimeError("private synthetic exception text")

    monkeypatch.setattr(domain, "find_secret_kinds", failure)
    with pytest.raises(ExperienceError) as caught:
        require_safe(b"{}")
    assert caught.value.code == "SECRET_SCAN_UNAVAILABLE"
    assert "private" not in str(caught.value)


def test_policy_tombstones_cover_capture_window(policy):
    with pytest.raises(ValidationError):
        type(policy).model_validate_json(
            canonical({**policy.model_dump(), "tombstoneRetentionSeconds": 89})
        )


def test_policy_unknown_and_unbounded_fields_refused(policy):
    for change in (
        {"maxPageSize": 51},
        {"batchSize": 0},
        {"extra": True},
        {"defaultRetentionSeconds": 91},
        {"sweepIntervalSeconds": True},
    ):
        with pytest.raises(ValidationError):
            type(policy).model_validate_json(canonical({**policy.model_dump(), **change}))


def test_request_cannot_widen_retention(policy, body):
    with pytest.raises(ExperienceError) as caught:
        parse_capture(canonical({**capture_value(body), "retentionSeconds": 91}), policy)
    assert caught.value.code == "RETENTION_LIMIT_EXCEEDED"


def test_semantically_equal_json_has_stable_request_digest(policy, body):
    value = capture_value(body)
    left = parse_capture(json.dumps(value).encode(), policy)
    right = parse_capture(
        json.dumps(dict(reversed(list(value.items()))), indent=2).encode(), policy
    )
    assert digest(left.model_dump(mode="json")) == digest(right.model_dump(mode="json"))


class ObservedSourceForDomainTest:
    def __init__(self):
        self.verifications = 0

    async def verify(self, _document):
        self.verifications += 1


async def test_exact_expiry_denied_before_source_access(policy, body, now):
    source = ObservedSourceForDomainTest()
    service = ExperienceService(policy, source, None)
    row = StoredExperience(
        body["task"]["taskId"],
        body["task"]["projectId"],
        body["task"]["runId"],
        "a" * 64,
        digest(body),
        body,
        "ACTIVE",
        now - timedelta(seconds=1),
        now,
        True,
        (False, False, False),
    )
    with pytest.raises(ExperienceError) as caught:
        await service.deliver(row, now)
    assert caught.value.code == "EXPERIENCE_UNAVAILABLE"
    assert source.verifications == 0
    assert (
        await service.deliver(replace(row, expires_at=now + timedelta(microseconds=1)), now)
    ).task
    assert source.verifications == 1


async def test_stored_digest_and_lineage_fail_closed(policy, body, now):
    source = ObservedSourceForDomainTest()
    service = ExperienceService(policy, source, None)
    row = StoredExperience(
        body["task"]["taskId"],
        body["task"]["projectId"],
        body["task"]["runId"],
        "a" * 64,
        "f" * 64,
        body,
        "ACTIVE",
        now,
        now + timedelta(seconds=1),
        True,
        (False, False, False),
    )
    with pytest.raises(ExperienceError) as caught:
        await service.deliver(row, now)
    assert caught.value.code == "STORED_INTEGRITY_INVALID"
    with pytest.raises(ExperienceError) as caught:
        await service.deliver(
            replace(row, content_digest=digest(body), source_run_id=row.experience_id), now
        )
    assert caught.value.code == "STORED_LINEAGE_INVALID"
    assert source.verifications == 0


async def test_quarantined_legacy_is_never_a_valid_document(policy, body, now):
    service = ExperienceService(policy, ObservedSourceForDomainTest(), None)
    row = StoredExperience(
        body["task"]["taskId"],
        body["task"]["projectId"],
        body["task"]["runId"],
        "",
        "",
        {"historical": "unvalidated"},
        "LEGACY",
        now,
        now,
        True,
        (True, True, True),
        schema_version=0,
    )
    with pytest.raises(ExperienceError) as caught:
        await service.deliver(row, now)
    assert caught.value.code == "LEGACY_QUARANTINED"


def test_trajectory_is_not_an_arbitrary_narrative(policy, body):
    body["trajectorySummary"] = "unobserved model narrative"
    with pytest.raises(ExperienceError) as caught:
        validate_document(body, policy)
    assert caught.value.code == "STORED_CONTRACT_INVALID"


def test_numeric_observations_are_not_coerced(policy, body):
    for value in (True, "1", 1.0):
        body["task"]["attempt"] = value
        with pytest.raises(ExperienceError):
            validate_document(body, policy)


def test_source_failure_is_a_valid_observation_not_a_pass(policy, body):
    body["task"]["status"] = body["finalResult"]["taskStatus"] = "FAILED"
    body["trajectorySummary"] = "FAILED; agents=0; modelCalls=0; tools=0; quality=UNKNOWN"
    body["failures"] = [{"sourceId": body["task"]["runId"], "outcome": "FAILED", "detail": None}]
    body["provenance"][0]["digest"] = digest(body["task"])
    document = validate_document(body, policy)
    assert document.finalResult.taskStatus == "FAILED" and document.quality is None

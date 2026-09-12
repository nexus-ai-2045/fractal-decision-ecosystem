from scripts.fde_architecture_drift_check import (
    EXTERNAL_AUTHORITIES,
    _check_external_authority,
    _parse_capability_registry_rows,
    evaluate,
)


def test_architecture_drift_check_passes_with_current_registry():
    result = evaluate()
    assert result["overall"] == "ok"
    assert result["errors"] == []


def test_parse_capability_registry_rows_reads_key_capability_resolution_mode():
    text = (
        "| key | capability | resolution | mode |\n"
        "|---|---|---|---|\n"
        "| startup-boot-gate | some capability text | operator-local-adapter | external-authority |\n"
    )
    rows = _parse_capability_registry_rows(text)
    assert rows["startup-boot-gate"] == {
        "capability": "some capability text",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    }


def test_resolution_drift_from_operator_local_adapter_to_withheld_is_detected():
    """Codex P2: registry 行の resolution を書き換えても verified のまま緑にならない。"""
    meta = EXTERNAL_AUTHORITIES["startup-boot-gate"]
    registry_rows = {
        "startup-boot-gate": {
            "capability": meta["capability"],
            "resolution": "withheld",
            "mode": meta["mode"],
        }
    }
    receipt, errors = _check_external_authority("startup-boot-gate", meta, registry_rows)
    assert receipt["status"] == "error"
    assert receipt["resolution_matches_registry"] is False
    assert any("resolution mismatch" in e and "startup-boot-gate" in e for e in errors)


def test_matching_registry_row_is_reported_verified():
    meta = EXTERNAL_AUTHORITIES["startup-boot-gate"]
    registry_rows = {
        "startup-boot-gate": {
            "capability": meta["capability"],
            "resolution": meta["resolution"],
            "mode": meta["mode"],
        }
    }
    receipt, errors = _check_external_authority("startup-boot-gate", meta, registry_rows)
    assert receipt["status"] == "verified"
    assert errors == []


def test_mode_drift_is_detected():
    meta = EXTERNAL_AUTHORITIES["fact-provenance"]
    registry_rows = {
        "fact-provenance": {
            "capability": meta["capability"],
            "resolution": meta["resolution"],
            "mode": "planned",
        }
    }
    receipt, errors = _check_external_authority("fact-provenance", meta, registry_rows)
    assert receipt["status"] == "error"
    assert receipt["mode_matches_registry"] is False
    assert any("mode mismatch" in e and "fact-provenance" in e for e in errors)


def test_missing_row_is_reported_as_missing_not_verified():
    meta = EXTERNAL_AUTHORITIES["measurement-gate"]
    receipt, errors = _check_external_authority("measurement-gate", meta, {})
    assert receipt["status"] == "error"
    assert receipt["listed_in_registry"] is False
    assert any("missing from registry" in e for e in errors)


def test_capability_drift_is_detected():
    """Codex P2: capability も registry 行と突き合わせる。非空だけでは drift を見逃す。"""
    meta = EXTERNAL_AUTHORITIES["measurement-gate"]
    registry_rows = {
        "measurement-gate": {
            "capability": "まったく別の能力",
            "resolution": meta["resolution"],
            "mode": meta["mode"],
        }
    }
    receipt, errors = _check_external_authority("measurement-gate", meta, registry_rows)
    assert receipt["status"] == "error"
    assert receipt["capability_matches_registry"] is False
    assert any("capability mismatch" in e and "measurement-gate" in e for e in errors)


def test_capability_with_parenthetical_supplement_is_verified():
    """registry 側は本文の後ろに（補足）を付けることがある。先頭一致なら verified。"""
    meta = EXTERNAL_AUTHORITIES["startup-boot-gate"]
    registry_rows = {
        "startup-boot-gate": {
            "capability": meta["capability"] + "（canonical と runtime copy の SHA-256 drift 検査）",
            "resolution": meta["resolution"],
            "mode": meta["mode"],
        }
    }
    receipt, errors = _check_external_authority("startup-boot-gate", meta, registry_rows)
    assert receipt["status"] == "verified"
    assert errors == []


def test_capability_with_mid_string_supplement_is_verified():
    """補足は途中に挟まることもある (dependency-registry.md の fact-provenance 行)。"""
    meta = EXTERNAL_AUTHORITIES["fact-provenance"]
    registry_rows = {
        "fact-provenance": {
            "capability": "毎turn事実来歴（segment marker / envelope / hash binding）の hook 実装と runtime drift 検査",
            "resolution": meta["resolution"],
            "mode": meta["mode"],
        }
    }
    receipt, errors = _check_external_authority("fact-provenance", meta, registry_rows)
    assert receipt["status"] == "verified"
    assert errors == []

from scripts.public_ready_check import main
from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication


def test_public_ready_check_passes() -> None:
    assert main() == 0


def test_pre_publication_gate_check_passes() -> None:
    result = evaluate_pre_publication()
    assert result["overall"] == "ok", result["errors"]

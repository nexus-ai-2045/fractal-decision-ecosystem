from scripts.public_ready_check import main


def test_public_ready_check_passes() -> None:
    assert main() == 0

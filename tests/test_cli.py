import subprocess
import sys


def test_cli_default():
    result = subprocess.run(
        [sys.executable, '-m', 'alviaorange.cli'],
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'AB-001' in result.stdout

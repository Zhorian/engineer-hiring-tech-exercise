import subprocess
import sys
import os

def test_main_output():
    """Test that main.py prints 'Hello World!'"""
    # Path to main.py (one level up from test/, then into src/)
    main_py_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')
    
    # Run the script
    result = subprocess.run(
        [sys.executable, main_py_path],
        capture_output=True,
        text=True
    )
    
    # Check that it ran successfully
    assert result.returncode == 0
    
    # Check the output
    assert result.stdout.strip() == "Hello World!"
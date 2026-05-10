import os
import shutil
import glob

def cleanup():
    # Patterns to remove
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/test_*.py",
        "**/integration_*.py",
        "**/main_*_test.py",
        "**/run_*_tests.py",
        "run_all_tests.py",
        "run_tests_to_file.py",
        "verify_all_steps.py",
        "check_setup.py",
        "*demo.py",
        "**/*.db",
        "**/*.csv",
        "venv",
        ".vscode",
        ".pytest_cache"
    ]
    
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Removed directory: {path}")
                else:
                    os.remove(path)
                    print(f"Removed file: {path}")
            except Exception as e:
                print(f"Error removing {path}: {e}")

if __name__ == "__main__":
    confirm = input("This will delete all untracked test files, pycache, databases, and venv locally. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        cleanup()
    else:
        print("Cleanup cancelled.")

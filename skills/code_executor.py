"""Skill: Python Code Executor — runs code in a sandboxed subprocess."""

import os
import subprocess
import sys
import tempfile


def execute_python(code: str, timeout: int = 15) -> dict:
    """
    Execute Python code in an isolated subprocess and return stdout/stderr.
    Dangerous builtins are not fully blocked — keep this behind auth.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout[:3000],
            "stderr": result.stderr[:1000],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Code execution timed out after {timeout}s."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.unlink(tmp_path)

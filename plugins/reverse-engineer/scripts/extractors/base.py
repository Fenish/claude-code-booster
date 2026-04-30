import subprocess


def run_tool(cmd, timeout=60):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode
    except FileNotFoundError:
        return "", f"{cmd[0]} not found", -1
    except subprocess.TimeoutExpired:
        return "", f"{cmd[0]} timed out after {timeout}s", -2

# Security Model: Self-Healing Code Repair Pipeline

The **Self-Healing Code Repair Pipeline** executes untrusted and AI-generated code. Security is designed into the core system from the ground up to prevent host compromise, secret leakage, resource exhaustion, and lateral movement.

---

## 1. Threat Model & Defense In Depth

| Threat Vector | Potential Impact | Security Control Implemented |
|---|---|---|
| Arbitrary Shell Execution | Remote Code Execution on Host | No `run_shell` tool exposed to agents. Tools are strictly whitelisted functional operations (`read_file`, `apply_patch`). |
| Host Secret Leakage | Compromise of Groq, Langfuse, or AWS credentials | Environment sanitization strips all credentials (`GROQ_*`, `LANGFUSE_*`, `*KEY*`, `*TOKEN*`) prior to subprocess or container execution. |
| Path Traversal (`../`) | Unauthorized reading or overwriting of host files | Strict canonical path boundary validation (`Path.resolve().relative_to(workspace)`). Any attempt to escape raises `SecurityError`. |
| Malicious or Broken Patch | Code corruption, syntax crashes, file deletion | AST parsing verifies valid Python syntax prior to committing patch. Search-and-replace prevents accidental file truncations. |
| Endless Loops / Denial of Service | Host CPU/Memory lockup | Strict execution timeout (default 30s) and container memory/CPU quotas (`512MB RAM`, `1 CPU core`). |
| Outbound Network Exfiltration | Exfiltration of code or keys | Docker containers run with `--network=none` isolating execution from the public internet. |
| Container Privilege Escalation | Root escape from Docker container | Dockerfile defines an unprivileged user `sandboxuser` (`UID 1001`) with restricted permissions. |
| Test Tampering by Agent | Coder rewrites tests to artificially pass | `write_file` and `apply_patch` forbid modifying files matching `test_*.py` or `*_test.py`. |

---

## 2. Workspace Isolation Architecture

Each repair request generates a unique temporary workspace directory:
```
workspaces/{repair_id}/
├── <source_file>.py
├── <test_file>.py
├── <regression_files>.py
└── .git/
```

- Each directory is managed independently with its own local Git tracking.
- Workspace cleanup removes temporary artifacts after completion or on cancellation.

---

## 3. Path Traversal Enforcement Implementation

```python
def _validate_path(workspace_path: Path, relative_path: str) -> Path:
    rel = Path(relative_path)
    if rel.is_absolute():
        raise SecurityError(f"Absolute paths not permitted: {relative_path}")

    target = (workspace_path / rel).resolve()
    ws_resolved = workspace_path.resolve()

    try:
        target.relative_to(ws_resolved)
    except ValueError:
        raise SecurityError(f"Path traversal detected: {relative_path}")

    return target
```

---

## 4. Environment Sanitization for Execution

Before any test execution begins (in Docker or isolated subprocess), the host environment is purged:

```python
safe_env = os.environ.copy()
for key in list(safe_env.keys()):
    k_upper = key.upper()
    if any(secret in k_upper for secret in ["GROQ", "LANGFUSE", "SECRET", "TOKEN", "KEY", "AUTH", "PASS"]):
        safe_env.pop(key, None)
```

No LLM API keys, database credentials, or system passwords exist inside the runtime execution context.

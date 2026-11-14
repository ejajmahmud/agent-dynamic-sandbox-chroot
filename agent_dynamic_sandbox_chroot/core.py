"""Core command sandbox jail implementation."""
import os
import shlex
from typing import List, Dict, Any, Optional

class SecurityPolicy:
    def __init__(self, allowed_binaries: Optional[List[str]] = None, forbidden_commands: Optional[List[str]] = None):
        self.allowed_binaries = set(allowed_binaries or ["python", "python3", "pytest", "git", "ls", "cat", "echo", "mkdir", "cp"])
        self.forbidden_commands = set(forbidden_commands or ["rm -rf", "mkfs", "dd", "shutdown", "reboot", "chmod 777", "sudo"])

class ExecutionAudit:
    def __init__(self, is_allowed: bool, reason: str, normalized_cmd: str):
        self.is_allowed = is_allowed
        self.reason = reason
        self.normalized_cmd = normalized_cmd

class CommandSandboxJail:
    def __init__(self, sandbox_root: str, policy: Optional[SecurityPolicy] = None):
        self.sandbox_root = os.path.abspath(sandbox_root)
        self.policy = policy or SecurityPolicy()

    def audit_command(self, cmd_string: str) -> ExecutionAudit:
        clean_cmd = cmd_string.strip()
        # 1. Blacklist substring check
        for forb in self.policy.forbidden_commands:
            if forb in clean_cmd:
                return ExecutionAudit(False, f"FORBIDDEN_COMMAND_PATTERN: {forb}", clean_cmd)

        # 2. Tokenize command safely
        try:
            tokens = shlex.split(clean_cmd)
        except Exception:
            return ExecutionAudit(False, "MALFORMED_SHELL_SYNTAX", clean_cmd)

        if not tokens:
            return ExecutionAudit(False, "EMPTY_COMMAND", clean_cmd)

        binary = os.path.basename(tokens[0]).lower()
        if binary not in self.policy.allowed_binaries:
            return ExecutionAudit(False, f"UNAUTHORIZED_BINARY: {binary}", clean_cmd)

        # 3. Path traversal inspection
        for tok in tokens[1:]:
            if ".." in tok or tok.startswith("/etc") or tok.startswith("/root") or tok.startswith("C:\Windows"):
                return ExecutionAudit(False, f"PATH_TRAVERSAL_DETECTED: {tok}", clean_cmd)

        return ExecutionAudit(True, "APPROVED", clean_cmd)

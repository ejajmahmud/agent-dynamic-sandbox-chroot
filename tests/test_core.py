"""Unit tests for agent-dynamic-sandbox-chroot."""
import unittest
from agent_dynamic_sandbox_chroot.core import CommandSandboxJail

class TestCommandSandboxJail(unittest.TestCase):
    def setUp(self):
        self.jail = CommandSandboxJail("/tmp/sandbox")

    def test_allowed_command(self):
        audit = self.jail.audit_command("python test.py")
        self.assertTrue(audit.is_allowed)
        self.assertEqual(audit.reason, "APPROVED")

    def test_forbidden_rm_rf(self):
        audit = self.jail.audit_command("rm -rf /var/log")
        self.assertFalse(audit.is_allowed)
        self.assertTrue("FORBIDDEN" in audit.reason)

    def test_path_traversal(self):
        audit = self.jail.audit_command("cat ../../../secret.txt")
        self.assertFalse(audit.is_allowed)
        self.assertTrue("PATH_TRAVERSAL" in audit.reason)

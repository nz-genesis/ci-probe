import unittest

from contract import (
    Authority,
    Capability,
    Constraint,
    ExecutableContract,
    State,
    Status,
    admit,
    canonical_bytes,
    contract_sha256,
)


class ContractBoundaryTests(unittest.TestCase):
    def make_contract(self, *, content="hello"):
        return ExecutableContract(
            transition="write",
            state=State("workspace", 1, "state-v1"),
            capability=Capability("workspace.write", {"max_bytes": 128}),
            authority=Authority("owner-A", "workspace", "write"),
            constraints=(
                Constraint("scope", "workspace"),
                Constraint("max_bytes", 128),
            ),
            payload={"path": "x.txt", "content": content},
        )

    def test_deterministic_serialization(self):
        a = self.make_contract()
        b = self.make_contract()
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual(contract_sha256(a), contract_sha256(b))

    def test_payload_mutation_changes_digest(self):
        self.assertNotEqual(
            contract_sha256(self.make_contract()),
            contract_sha256(self.make_contract(content="changed")),
        )

    def test_capability_and_authority_are_distinct(self):
        c = self.make_contract()
        self.assertEqual(
            admit(
                c,
                available_capabilities={"workspace.write"},
                permitted_authorities=set(),
                known_constraints={"scope": "workspace", "max_bytes": 128},
            ),
            Status.REJECTED,
        )
        self.assertEqual(
            admit(
                c,
                available_capabilities=set(),
                permitted_authorities={("owner-A", "workspace", "write")},
                known_constraints={"scope": "workspace", "max_bytes": 128},
            ),
            Status.REJECTED,
        )

    def test_unknown_constraint_is_preserved(self):
        c = self.make_contract()
        self.assertEqual(
            admit(
                c,
                available_capabilities={"workspace.write"},
                permitted_authorities={("owner-A", "workspace", "write")},
                known_constraints={"scope": "workspace"},
            ),
            Status.UNKNOWN,
        )

    def test_valid_contract_is_admissible(self):
        c = self.make_contract()
        self.assertEqual(
            admit(
                c,
                available_capabilities={"workspace.write"},
                permitted_authorities={("owner-A", "workspace", "write")},
                known_constraints={"scope": "workspace", "max_bytes": 128},
            ),
            Status.ADMISSIBLE,
        )


if __name__ == "__main__":
    unittest.main()

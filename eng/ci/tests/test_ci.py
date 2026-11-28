"""Integration tests use real commits and the same entrypoint as Actions."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[3]
ORM_GRAPH = "docs/korda-orm/implementation-graph.json"
ORM_SCHEMA = "schemas/independent-graph-v1.schema.json"
ORM_CHECKS = ["orm-graph-schema", "orm-task-links"]
ALL_CHECKS = ["ci-self-test", "graph-schema", *ORM_CHECKS, "task-links"]


class DocumentCI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="plan-ci-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        (self.root / ".gitignore").write_text("__pycache__/\n*.py[cod]\n.self-test-ran\n")
        for directory in ("tasks", "research-tasks", "documentation-tasks", "fragments", "schemas"):
            shutil.copytree(SOURCE / directory, self.root / directory)
        for filename in ("research-graph.json", "documentation-graph.json", "delivery-graph.json"):
            shutil.copy2(SOURCE / filename, self.root / filename)
        # A small independent fixture isolates routing tests from live task count
        # and in-progress authoring. This pin is synthetic; CI does not fetch it.
        independent = {
            "schema_version": "1.0.0", "direction": "Korda-Orm-01", "task_prefix": "ORM-",
            "implementation_authorized": False,
            "design": {"repository": "IzuSharp/Korda-Design", "commit": "1" * 40,
                       "contracts": [f"ORM-C{i:02}" for i in range(1, 7)]},
            "nodes": [],
        }
        for task, dependencies in (("ORM-FOUNDATION", []), ("ORM-TYPES", ["ORM-FOUNDATION"])):
            packet = f"docs/korda-orm/tasks/{task}.md"
            independent["nodes"].append({
                "id": task, "title": task + " fixture", "status": "planned_candidate",
                "track": "primary", "owner_role": "fixture-owner",
                "start_dependencies": dependencies, "acceptance_dependencies": dependencies,
                "contracts": ["ORM-C01"], "packet": packet,
                "write_scopes": ["src/Orm/Fixture/**"], "validation": ["Native consumer fixture"],
            })
            self.write(packet, f"# {task}: Fixture\n\nStatus: planned_candidate.\n")
        self.write(ORM_GRAPH, json.dumps(independent, indent=2) + "\n")
        (self.root / "eng/ci/tests").mkdir(parents=True)
        for filename in ("run.py", "registry.py", "checks.py", "requirements.txt"):
            shutil.copy2(SOURCE / "eng/ci" / filename, self.root / "eng/ci" / filename)
        # A fixture self-test writes a sentinel, avoiding recursive test discovery.
        (self.root / "eng/ci/tests/test_fixture.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class Fixture(unittest.TestCase):\n"
            " def test_run(self): Path('.self-test-ran').write_text('ok')\n")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "CI fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.base = self.commit("valid current graph fixture")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True,
                                       stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def mutate(self, filename, operation):
        path = self.root / filename
        value = json.loads(path.read_text())
        operation(value)
        path.write_text(json.dumps(value, indent=2) + "\n")

    def command(self, *args, expected=0, env=None):
        environment = os.environ.copy()
        for name in ("GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH", "GITHUB_STEP_SUMMARY"):
            environment.pop(name, None)
        if env:
            environment.update(env)
        result = subprocess.run([sys.executable, "eng/ci/run.py", *args], cwd=self.root,
                                text=True, capture_output=True, env=environment, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def selected(self, event="pull_request", base=None, head="HEAD"):
        result = self.command("--event", event, "--base", base or self.base,
                              "--head", head, "--list", "--json")
        return json.loads(result.stdout)

    def execute(self, expected=0, event="pull_request", base=None, extra=()):
        return self.command("--event", event, "--base", base or self.base,
                            "--head", "HEAD", *extra, expected=expected)

    def event(self, kind, before, after):
        payload = {"before": before, "after": after} if kind == "push" else {
            "pull_request": {"base": {"sha": before}, "head": {"sha": after}}}
        path = Path(self.temp.name) / "event.json"
        path.write_text(json.dumps(payload))
        return {"GITHUB_EVENT_NAME": kind, "GITHUB_EVENT_PATH": str(path)}

    def test_plain_directory_article_selects_zero_and_installs_nothing(self):
        self.write("docs/new-article.md", "# Ordinary documentation\n")
        self.commit("ordinary article")
        self.assertEqual(self.selected()["checks"], [])
        result = self.execute(extra=("--install-dependencies",))
        self.assertIn("Completed 0 checks", result.stdout)

    def test_graph_multitype_and_duplicate_hits_run_each_check_once(self):
        for filename in ("research-graph.json", "documentation-graph.json"):
            self.mutate(filename, lambda value: value.update(scope="Updated description"))
        self.commit("two graphs")
        self.assertEqual(self.selected()["checks"], ["graph-schema", "task-links"])
        result = self.execute()
        self.assertEqual(result.stdout.count("PASS graph-schema"), 1)
        self.assertEqual(result.stdout.count("PASS task-links"), 1)
        self.assertNotIn("ci-self-test", result.stdout)

    def test_fragment_only_runs_reference_check(self):
        self.mutate("fragments/database.json", lambda value: value.update(role="Clarified role"))
        self.commit("fragment")
        self.assertEqual(self.selected()["checks"], ["task-links"])
        self.execute()

    def test_schema_change_validates_current_users_and_rejects_invalid_sample(self):
        self.mutate("schemas/graph-v1.schema.json", lambda value: value["required"].append("new_required_field"))
        self.commit("schema rule")
        self.assertEqual(self.selected()["checks"], ["graph-schema", "task-links"])
        self.assertIn("new_required_field", self.execute(expected=1).stderr)

    def test_invalid_schema_is_rejected(self):
        self.mutate("schemas/graph-v1.schema.json", lambda value: value.update(type="not-a-type"))
        self.commit("bad schema")
        self.execute(expected=1)

    def test_missing_required_graph_field_is_rejected(self):
        self.mutate("research-graph.json", lambda value: value["nodes"][0].pop("title"))
        self.commit("invalid node")
        self.assertIn("title", self.execute(expected=1).stderr)

    def test_duplicate_task_id_is_rejected(self):
        self.mutate("research-graph.json", lambda value: value["nodes"].append(value["nodes"][0]))
        self.commit("duplicate task")
        self.assertIn("Duplicate task ID", self.execute(expected=1).stderr)

    def test_deleted_task_invalidates_surviving_references(self):
        self.mutate("research-graph.json", lambda value: value["nodes"].pop(0))
        self.commit("remove referenced R01")
        self.assertIn("missing task R01", self.execute(expected=1).stderr)

    def test_deleted_packet_is_validated(self):
        (self.root / "tasks/A01.md").unlink()
        self.commit("remove referenced packet")
        self.assertEqual(self.selected()["checks"], ["task-links"])
        self.assertIn("task packet", self.execute(expected=1).stderr)

    def test_rename_routes_old_packet_and_new_prose_path(self):
        (self.root / "docs").mkdir(exist_ok=True)
        self.git("mv", "tasks/A01.md", "docs/archived-task.md")
        self.commit("move packet into prose")
        plan = self.selected()
        self.assertEqual(plan["checks"], ["task-links"])
        self.assertIn("tasks/A01.md", plan["changed_paths"])
        self.assertIn("docs/archived-task.md", plan["changed_paths"])
        self.execute(expected=1)

    def test_plain_rename_and_delete_select_zero(self):
        self.write("docs/old.md", "# Plain\n")
        base = self.commit("article")
        self.git("mv", "docs/old.md", "docs/new.md")
        self.commit("rename article")
        self.assertEqual(self.selected(base=base)["checks"], [])
        base = self.git("rev-parse", "HEAD")
        (self.root / "docs/new.md").unlink()
        self.commit("delete article")
        self.assertEqual(self.selected(base=base)["checks"], [])

    def test_rename_unknown_destination_fails(self):
        self.write("docs/article.md", "# Plain\n")
        base = self.commit("article")
        self.git("mv", "docs/article.md", "unregistered.json")
        self.commit("unknown structured destination")
        self.assertIn("Unregistered path", self.execute(expected=1, base=base).stderr)

    def test_unknown_unicode_tab_and_newline_paths_fail(self):
        for path in ("unregistered/数据.json", "unregistered/tab\tname.json", "unregistered/line\nname.json"):
            with self.subTest(path=path):
                self.git("reset", "--hard", self.base)
                self.write(path, "{}\n")
                self.commit("unregistered path")
                self.assertIn("Unregistered path", self.execute(expected=1).stderr)

    def test_divergent_pr_excludes_target_only_changes(self):
        self.git("checkout", "-q", "-b", "feature")
        self.write("docs/feature.md", "# Feature\n")
        head = self.commit("feature prose")
        self.git("checkout", "-q", "main")
        self.mutate("research-graph.json", lambda value: value.update(scope="Target-only change"))
        target = self.commit("target graph")
        self.git("checkout", "-q", "feature")
        self.assertEqual(self.selected(base=target, head=head)["checks"], [])
        result = self.command(env=self.event("pull_request", target, head))
        self.assertIn("Completed 0 checks", result.stdout)

    def test_merge_to_main_uses_actual_push_before_after(self):
        self.git("checkout", "-q", "-b", "feature")
        self.mutate("research-graph.json", lambda value: value.update(scope="Feature graph"))
        self.commit("structured change")
        self.write("docs/last.md", "# Last feature commit is prose\n")
        self.commit("prose followup")
        self.git("checkout", "-q", "main")
        before = self.git("rev-parse", "HEAD")
        self.git("merge", "-q", "--no-ff", "feature", "-m", "Merge feature")
        head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.selected(event="push", base=before)["checks"], ["graph-schema", "task-links"])
        result = self.command(env=self.event("push", before, head))
        self.assertIn("PASS graph-schema", result.stdout)
        self.assertIn("PASS task-links", result.stdout)

    def test_multi_commit_push_not_just_last_commit(self):
        self.mutate("research-graph.json", lambda value: value.update(scope="First pushed commit"))
        self.commit("graph")
        self.write("docs/last.md", "# Last commit\n")
        self.commit("prose")
        self.assertEqual(self.selected(event="push")["checks"], ["graph-schema", "task-links"])

    def test_first_push_compares_empty_tree(self):
        result = self.command("--list", "--json", env=self.event("push", "0" * 40, self.base))
        self.assertEqual(json.loads(result.stdout)["checks"], ALL_CHECKS)

    def test_shallow_event_fetches_merge_base_from_local_origin(self):
        self.git("checkout", "-q", "-b", "feature")
        self.write("docs/feature.md", "# Feature\n")
        head = self.commit("feature")
        self.git("checkout", "-q", "main")
        self.write("docs/target.md", "# Target\n")
        target = self.commit("target")
        self.git("config", "uploadpack.allowFilter", "true")
        origin = self.root
        clone = Path(self.temp.name) / "shallow"
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--depth=1", "--branch", "feature",
                        origin.as_uri(), str(clone)], check=True, capture_output=True)
        self.root = clone
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository"), "true")
        result = self.command(env=self.event("pull_request", target, head))
        self.assertIn("Completed 0 checks", result.stdout)
        # A missing before commit in a shallow clone also works for push events.
        result = self.command("--list", "--json", env=self.event("push", self.base, head))
        self.assertEqual(json.loads(result.stdout)["checks"], [])

    def test_checkout_mismatch_fails_before_checkers(self):
        self.write("docs/new.md", "# New\n")
        head = self.commit("new")
        self.assertIn("checked-out HEAD", self.command("--event", "push", "--base", self.base,
                      "--head", self.base, expected=1).stderr)
        self.assertIn("Checkout HEAD", self.command(env=self.event("push", self.base, self.base), expected=1).stderr)
        self.assertNotEqual(head, self.base)

    def test_ci_edit_revalidates_current_content_and_runs_self_test(self):
        for filename in ("eng/ci/registry.py", "eng/ci/run.py"):
            with (self.root / filename).open("a") as stream:
                stream.write("\n# CI maintenance\n")
        self.commit("CI changes")
        self.assertEqual(self.selected()["checks"], ALL_CHECKS)
        self.execute()
        self.assertEqual((self.root / ".self-test-ran").read_text(), "ok")

    def test_removed_registration_cannot_hide_deleted_reference(self):
        path = self.root / "eng/ci/registry.py"
        path.write_text(path.read_text().replace('"tasks/*.md", "research-tasks/*.md", "documentation-tasks/*.md"',
                                               '"research-tasks/*.md", "documentation-tasks/*.md"'))
        (self.root / "tasks/A01.md").unlink()
        self.commit("retire rule and referenced packet")
        self.assertIn("task-links", self.selected()["checks"])
        self.execute(expected=1)

    def test_dependency_cycle_is_rejected_but_cross_review_cycle_is_valid(self):
        def review_cycle(value):
            value["nodes"][0]["cross_review_by"] = ["R02"]
            value["nodes"][1]["cross_review_by"] = ["R01"]
        self.mutate("research-graph.json", review_cycle)
        self.commit("valid review cycle")
        self.execute()
        def scheduling_cycle(value):
            value["nodes"][0]["start_dependencies"] = ["R02"]
            value["nodes"][1]["start_dependencies"] = ["R01"]
        self.mutate("research-graph.json", scheduling_cycle)
        self.commit("invalid scheduling cycle")
        self.assertIn("cycle", self.execute(expected=1).stderr)

    def test_unknown_cross_review_and_single_task_references_rejected(self):
        for field, value in (("cross_review_by", ["R999"]), ("workspace_manifest_integration_owner", "A999")):
            with self.subTest(field=field):
                self.git("reset", "--hard", self.base)
                self.mutate("research-graph.json", lambda obj: obj["nodes"][0].update({field: value}))
                self.commit("invalid reference")
                self.assertIn("missing task", self.execute(expected=1).stderr)

    def test_invalid_fragment_reference_is_rejected(self):
        self.mutate("fragments/database.json", lambda value: value["delivery_task_ids"].append("B999"))
        self.commit("bad fragment reference")
        self.assertIn("unknown delivery task", self.execute(expected=1).stderr)

    def test_nested_fragment_add_and_move_are_checked(self):
        self.write("fragments/nested/new.json", '{"documentation_task_id":"D999"}\n')
        self.commit("invalid nested fragment")
        self.assertEqual(self.selected()["checks"], ["task-links"])
        self.assertIn("unknown documentation task", self.execute(expected=1).stderr)
        self.git("reset", "--hard", self.base)
        (self.root / "fragments/nested").mkdir(exist_ok=True)
        self.git("mv", "fragments/database.json", "fragments/nested/database.json")
        self.mutate("fragments/nested/database.json", lambda value: value.update(documentation_task_id="D999"))
        self.commit("move and invalidate fragment")
        self.assertIn("unknown documentation task", self.execute(expected=1).stderr)

    def test_nested_declared_task_references_are_checked(self):
        cases = (
            {"conditional_dependencies": [{"task_id": "A02", "revision": "0.4.0", "gate": "start",
                                            "condition": {"task_id": "A999", "selection_status": "selected"}}]},
            {"required_selection_groups": [{"id": "example", "minimum_selected": 1, "task_ids": ["B999"]}]},
            {"protocol_host_profiles": [{"host_task_id": "B999", "selection_status": "selected", "contract_input": None}]},
            {"release_scope": {"components": [{"task_id": "B999", "revision": "0.4.0"}]}},
        )
        for fields in cases:
            with self.subTest(fields=fields):
                self.git("reset", "--hard", self.base)
                self.mutate("delivery-graph.json", lambda value: value["nodes"][0].update(fields))
                self.commit("invalid nested reference")
                self.execute(expected=1)

    def test_new_type_and_check_need_no_dispatcher_or_yaml_change(self):
        path = self.root / "eng/ci/registry.py"
        with path.open("a") as stream:
            stream.write('\nCHECKS["example"] = Check(("python3", "-c", "print(123)"))\n'
                         'TYPES["example"] = DocumentType(("example",))\n'
                         'REGISTRATIONS += (Registration(("examples/*.json",), ("example",)),)\n')
        base = self.commit("register a new type")
        self.write("examples/item.json", "{}\n")
        self.commit("new type document")
        self.assertEqual(self.selected(base=base)["checks"], ["example"])
        self.assertIn("PASS example", self.execute(base=base).stdout)

    def test_independent_prose_selects_zero(self):
        self.write("docs/korda-orm/notes.md", "# Maintained research conclusion\n")
        self.commit("independent prose")
        self.assertEqual(self.selected()["checks"], [])
        self.assertIn("Completed 0 checks", self.execute(extra=("--install-dependencies",)).stdout)

    def test_independent_graph_selects_only_its_schema_and_links(self):
        self.mutate(ORM_GRAPH, lambda value: value["nodes"][0].update(title="Clarified foundation"))
        self.commit("independent graph")
        self.assertEqual(self.selected()["checks"], ORM_CHECKS)
        result = self.execute()
        for check in ORM_CHECKS:
            self.assertEqual(result.stdout.count("PASS " + check), 1)
        self.assertNotIn("PASS graph-schema", result.stdout)
        self.assertNotIn("PASS task-links", result.stdout)

    def test_independent_packet_selects_only_its_links(self):
        self.write("docs/korda-orm/tasks/ORM-TYPES.md", "# ORM-TYPES — Updated packet\n")
        self.commit("independent packet")
        self.assertEqual(self.selected()["checks"], ["orm-task-links"])
        self.execute()

    def test_independent_schema_revalidates_only_its_users(self):
        self.mutate(ORM_SCHEMA, lambda value: value["required"].append("new_required_field"))
        self.commit("independent schema requirement")
        self.assertEqual(self.selected()["checks"], ORM_CHECKS)
        self.assertIn("new_required_field", self.execute(expected=1).stderr)

    def test_independent_schema_is_validated_by_standard_validator(self):
        self.mutate(ORM_SCHEMA, lambda value: value.update(type="not-a-type"))
        self.commit("invalid independent schema")
        self.execute(expected=1)

    def test_independent_missing_required_field_and_invalid_pin(self):
        for operation, fragment in (
            (lambda value: value["nodes"][0].pop("owner_role"), "owner_role"),
            (lambda value: value["design"].update(commit="main"), "commit"),
        ):
            with self.subTest(fragment=fragment):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, operation)
                self.commit("invalid independent shape")
                self.assertIn(fragment, self.execute(expected=1).stderr)

    def test_independent_duplicate_id_is_rejected(self):
        self.mutate(ORM_GRAPH, lambda value: value["nodes"].append(dict(value["nodes"][0], title="Duplicate ID")))
        self.commit("duplicate independent ID")
        self.assertIn("Duplicate independent task ID", self.execute(expected=1).stderr)

    def test_independent_duplicate_dependencies_and_contracts(self):
        cases = (
            lambda value: value["nodes"][1]["start_dependencies"].append("ORM-FOUNDATION"),
            lambda value: value["nodes"][1]["acceptance_dependencies"].append("ORM-FOUNDATION"),
            lambda value: value["nodes"][1]["contracts"].append("ORM-C01"),
            lambda value: value["design"]["contracts"].append("ORM-C01"),
        )
        for operation in cases:
            with self.subTest(operation=operation):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, operation)
                self.commit("duplicate independent reference")
                self.assertIn("non-unique", self.execute(expected=1).stderr)

    def test_independent_missing_and_foreign_references(self):
        for reference, message in (("ORM-MISSING", "missing task"), ("R01", "foreign task reference")):
            with self.subTest(reference=reference):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, lambda value: value["nodes"][1].update(start_dependencies=[reference]))
                self.commit("bad independent reference")
                self.assertIn(message, self.execute(expected=1).stderr)
        self.git("reset", "--hard", self.base)
        self.mutate(ORM_GRAPH, lambda value: value["nodes"][1].update(contracts=["ORM-C99"]))
        self.commit("unknown contract")
        self.assertIn("unknown contract", self.execute(expected=1).stderr)

    def test_independent_direction_prefix_and_foreign_ids(self):
        for operation, message in (
            (lambda value: value.update(direction="Another-01"), "direction"),
            (lambda value: value.update(task_prefix="OTHER-"), "task_prefix"),
            (lambda value: value["nodes"][1].update(id="OTHER-TYPES"), "foreign task ID"),
            (lambda value: value["design"].update(contracts=["OTHER-C01"]), "foreign design contract"),
        ):
            with self.subTest(message=message):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, operation)
                self.commit("foreign independent direction")
                self.assertIn(message, self.execute(expected=1).stderr)

    def test_independent_union_of_start_and_acceptance_edges_is_acyclic(self):
        # TYPES already starts after FOUNDATION. Adding only the opposite
        # acceptance edge must still be detected as a scheduling cycle.
        self.mutate(ORM_GRAPH, lambda value: value["nodes"][0].update(acceptance_dependencies=["ORM-TYPES"]))
        self.commit("mixed gate cycle")
        self.assertIn("dependency cycle", self.execute(expected=1).stderr)

    def test_independent_authorization_and_status_are_not_coerced(self):
        for operation in (
            lambda value: value.update(implementation_authorized="false"),
            lambda value: value["nodes"][1].update(status="accepted"),
            lambda value: value["nodes"][1].update(status="completed"),
            lambda value: value["nodes"][1].update(status="in_progress"),
        ):
            with self.subTest(operation=operation):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, operation)
                self.commit("invalid authorization state")
                self.execute(expected=1)

    def test_independent_deleted_packet_invalidates_its_graph_only(self):
        (self.root / "docs/korda-orm/tasks/ORM-TYPES.md").unlink()
        self.commit("delete independent packet")
        self.assertEqual(self.selected()["checks"], ["orm-task-links"])
        self.assertIn("task packet", self.execute(expected=1).stderr)

    def test_independent_packet_rename_routes_old_and_new_paths(self):
        self.git("mv", "docs/korda-orm/tasks/ORM-TYPES.md", "docs/korda-orm/archived-types.md")
        self.commit("move independent packet into prose")
        plan = self.selected()
        self.assertEqual(plan["checks"], ["orm-task-links"])
        self.assertIn("docs/korda-orm/tasks/ORM-TYPES.md", plan["changed_paths"])
        self.assertIn("docs/korda-orm/archived-types.md", plan["changed_paths"])
        self.execute(expected=1)

    def test_independent_multi_commit_push_includes_earlier_graph_change(self):
        self.mutate(ORM_GRAPH, lambda value: value["nodes"][0].update(title="First pushed change"))
        self.commit("independent graph first")
        self.write("docs/korda-orm/last.md", "# Last pushed change is prose\n")
        head = self.commit("prose last")
        self.assertEqual(self.selected(event="push")["checks"], ORM_CHECKS)
        result = self.command(env=self.event("push", self.base, head))
        self.assertIn("PASS orm-graph-schema", result.stdout)
        self.assertNotIn("PASS graph-schema", result.stdout)

    def test_independent_orphan_packet_is_rejected(self):
        self.write("docs/korda-orm/tasks/ORM-ORPHAN.md", "# ORM-ORPHAN: Unregistered task\n")
        self.commit("independent orphan")
        self.assertEqual(self.selected()["checks"], ["orm-task-links"])
        self.assertIn("orphan task packet", self.execute(expected=1).stderr)

    def test_independent_node_and_packet_can_be_removed_together(self):
        self.mutate(ORM_GRAPH, lambda value: value["nodes"].pop())
        (self.root / "docs/korda-orm/tasks/ORM-TYPES.md").unlink()
        self.commit("remove independent leaf and packet")
        self.assertEqual(self.selected()["checks"], ORM_CHECKS)
        self.execute()

    def test_independent_registered_graph_cannot_disappear(self):
        (self.root / ORM_GRAPH).unlink()
        self.commit("remove graph without retiring registration")
        self.assertEqual(self.selected()["checks"], ORM_CHECKS)
        self.assertIn("Missing registered independent graph", self.execute(expected=1).stderr)

    def test_independent_unsafe_packet_paths_are_rejected(self):
        for packet in ("../outside.md", "/tmp/outside.md", "docs/korda-orm/tasks/../ORM-TYPES.md",
                       "docs/korda-orm/tasks/ORM-FOUNDATION.md"):
            with self.subTest(packet=packet):
                self.git("reset", "--hard", self.base)
                self.mutate(ORM_GRAPH, lambda value: value["nodes"][1].update(packet=packet))
                self.commit("unsafe packet")
                self.assertIn("unsafe task packet", self.execute(expected=1).stderr)

    def test_independent_packet_symlink_cannot_escape_repository(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("# ORM-TYPES: Outside packet\n")
        packet = self.root / "docs/korda-orm/tasks/ORM-TYPES.md"
        packet.unlink()
        packet.symlink_to(outside)
        self.commit("packet symlink escape")
        self.assertIn("unsafe task packet", self.execute(expected=1).stderr)

    def test_independent_packet_heading_has_exact_id(self):
        for heading in ("# ORM-TYPES-OTHER: Wrong ID", "# ORM-FOUNDATION: Wrong owner", "No heading"):
            with self.subTest(heading=heading):
                self.git("reset", "--hard", self.base)
                self.write("docs/korda-orm/tasks/ORM-TYPES.md", heading + "\n")
                self.commit("invalid packet heading")
                self.assertEqual(self.selected()["checks"], ["orm-task-links"])
                self.assertIn("first heading", self.execute(expected=1).stderr)


if __name__ == "__main__":
    unittest.main()

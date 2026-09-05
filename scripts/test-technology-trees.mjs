// Mutation tests exercise failures after the attacker/caller updates file hashes;
// validation must depend on source evidence, not merely index consistency.
import { cp, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { parse, csv, hash, structuralHash } from "./technology-lib.mjs";
const source = path.resolve(
  process.argv[2] ?? "data/technology_trees/source_exports",
);
const dataset = path.resolve(process.argv[3] ?? "data/technology_trees");
const fixture = path.resolve("work/technology_validator_mutation_fixture");
await cp(dataset, fixture, { recursive: true });
const indexPath = path.join(fixture, "faction_index__wh3__8.1.1.csv");
const originalIndex = await readFile(indexPath, "utf8");
const ix = parse(originalIndex);
const faction = ix.rows.find(
  (r) => r.faction_key === "wh2_dlc13_lzd_spirits_of_the_jungle",
);
const file = path.join(fixture, faction.relative_path),
  original = await readFile(file, "utf8");
const cases = [
  {
    name: "missing source node",
    expected: "Node membership",
    mutate: (rows) => {
      rows.splice(
        rows.findIndex(
          (r) => r.record_type === "node" && r.node_set_key === "lzd_nakai",
        ),
        1,
      );
    },
  },
  {
    name: "changed effect value with refreshed hashes",
    expected: "Source field technology_effects_junction.value",
    mutate: (rows) => {
      rows.find((r) => r.record_type === "effect").effect_value = "987654.0000";
    },
  },
  {
    name: "cyclic dependency",
    expected: "Prerequisite cycle",
    mutate: (rows) => {
      const l = rows.find(
        (r) =>
          r.record_type === "dependency_link" && r.node_set_key === "lzd_nakai",
      );
      l.parent_node_key = l.child_node_key;
    },
  },
];
for (const c of cases) {
  const parsed = parse(original);
  c.mutate(parsed.rows);
  const text = csv(parsed.columns, parsed.rows);
  await writeFile(file, text);
  const current = parse(originalIndex),
    r = current.rows.find((r) => r.faction_key === faction.faction_key);
  Object.assign(r, {
    file_sha256: hash(text),
    file_bytes: Buffer.byteLength(text),
    total_rows: parsed.rows.length,
    tree_structure_sha256: structuralHash(parsed.rows),
  });
  await writeFile(indexPath, csv(current.columns, current.rows));
  const result = spawnSync(
    process.execPath,
    [
      "scripts/validate-technology-trees.mjs",
      source,
      fixture,
      "--skip-rebuild",
    ],
    { encoding: "utf8", maxBuffer: 4 * 1024 * 1024 },
  );
  assert.equal(result.status, 1, c.name + " must fail");
  const report = JSON.parse(
    await readFile(path.join(fixture, "audit_report.json"), "utf8"),
  );
  assert.ok(
    report.errors.some((e) => e.includes(c.expected)),
    c.name + " must fail for the expected reason",
  );
  console.log("PASS: " + c.name);
}
await writeFile(file, original);
await writeFile(indexPath, originalIndex);

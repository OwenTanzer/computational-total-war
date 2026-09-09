// Synthetic fixtures test extraction/integrity infrastructure, not game rules.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { SNAPSHOT, discover, family, sha256, verifyManifest } from "./effect-foundation-lib.mjs";

test("only inventory-observed tables become discovery roots", () => {
  const p = discover(["db/effect_bonus_value_basic_junction_tables/data__", "db/unrelated_tables/data__"]);
  assert.deepEqual(p.roots,["effect_bonus_value_basic_junction_tables"]);
  assert.equal(p.schema_missing_for_roots.length,1);
  assert.equal(family("unit_experience_bonuses_tables"),"experience");
  assert.equal(family("unit_set_to_mp_unit_caps_tables"),null);
});
test("schema closure retains external and absent-reference boundaries", () => {
  const p = discover(["db/effects_tables/data__", "db/test_support_tables/data__", "db/main_units_tables/data__"], {
    effects_tables:[{version:0,fields:[
      {name:"a",is_reference:["test_support","key"]},
      {name:"b",is_reference:["main_units","unit"]},
      {name:"c",is_reference:["test_virtual_enum","key"]}]}],
    test_support_tables:[{version:0,fields:[{name:"a",is_reference:["effects","effect"]}]}],
  });
  assert.deepEqual(p.selected_tables,["effects_tables","test_support_tables"]);
  assert.ok(p.dependency_edges.some(e=>e.status==="external_dataset_owner"));
  assert.ok(p.dependency_edges.some(e=>e.status==="no_packed_table_in_inventory"));
});
test("discovery is deterministic under input path order", () => {
  const paths=["db/unit_sets_tables/data__","db/effects_tables/data__"];
  assert.deepEqual(discover(paths),discover([...paths].reverse()));
});
test("empty discovery fails rather than claiming complete coverage", () => {
  assert.throws(()=>discover([]),/No foundation/);
});
async function fixture(fn) {
  const dir=await mkdtemp(path.join(tmpdir(),"ctw-effect-test-"));
  try {
    await mkdir(path.join(dir,"db"));
    const bytes=Buffer.from("synthetic source fixture\n");
    await writeFile(path.join(dir,"db/example.tsv"),bytes);
    const manifest={...SNAPSHOT,files:[{path:"db/example.tsv",bytes:bytes.length,sha256:sha256(bytes)}]};
    await writeFile(path.join(dir,"source_manifest.json"),JSON.stringify(manifest));
    await fn(dir,manifest);
  } finally { await rm(dir,{recursive:true,force:true}); }
}
test("manifest verifies exact bytes and rejects tampering",()=>fixture(async(dir)=>{
  await verifyManifest(dir);
  await writeFile(path.join(dir,"db/example.tsv"),"changed");
  await assert.rejects(verifyManifest(dir),/integrity failure/);
}));
test("snapshot mismatch and unlisted files fail closed",()=>fixture(async(dir,m)=>{
  m.steam_build_id="wrong";
  await writeFile(path.join(dir,"source_manifest.json"),JSON.stringify(m));
  await assert.rejects(verifyManifest(dir),/snapshot mismatch/);
  m.steam_build_id=SNAPSHOT.steam_build_id;
  await writeFile(path.join(dir,"source_manifest.json"),JSON.stringify(m));
  await writeFile(path.join(dir,"extra.tsv"),"stale");
  await assert.rejects(verifyManifest(dir),/exactly cover/);
}));
test("manifest path traversal and duplicate entries are rejected",()=>fixture(async(dir,m)=>{
  m.files.push({...m.files[0]});
  await writeFile(path.join(dir,"source_manifest.json"),JSON.stringify(m));
  await assert.rejects(verifyManifest(dir),/Duplicate or unsafe/);
  m.files=[{path:"../outside",bytes:0,sha256:""}];
  await writeFile(path.join(dir,"source_manifest.json"),JSON.stringify(m));
  await assert.rejects(verifyManifest(dir),/Duplicate or unsafe/);
}));

test("source validator checks schema, packed-file completeness and conflicting keys", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "ctw-effect-source-test-"));
  const table = "effects_tables", packed = ["db/effects_tables/a", "db/effects_tables/b"];
  const schema = { [table]: [{ version: 0, fields: [{ name: "effect", is_key: true }] }] };
  const discovery = { ...discover(packed, schema), db_paths: packed, selected_paths: packed };
  const run = () => execFileSync(process.execPath, [fileURLToPath(new URL("./validate-effect-source.mjs", import.meta.url)), dir], { encoding: "utf8", stdio: "pipe" });
  async function writeCandidate({ duplicate = false, missing = false, wrongHeader = false } = {}) {
    await rm(dir, { recursive: true, force: true });
    await mkdir(path.join(dir, "db", table), { recursive: true });
    const contents = {
      "decoded_schema.json": JSON.stringify(schema), "discovery.json": JSON.stringify(discovery),
      "db/effects_tables/a.tsv": `${wrongHeader ? "wrong" : "effect"}\n#${table};0;${packed[0]}\nsynthetic_a\n`,
      ...(!missing ? { "db/effects_tables/b.tsv": `effect\n#${table};0;${packed[1]}\n${duplicate ? "synthetic_a" : "synthetic_b"}\n` } : {}),
    };
    const files = [];
    for (const [relative, content] of Object.entries(contents)) {
      await writeFile(path.join(dir, relative), content);
      files.push({ path: relative, bytes: Buffer.byteLength(content), sha256: sha256(content) });
    }
    await writeFile(path.join(dir, "source_manifest.json"), JSON.stringify({ ...SNAPSHOT, table_folders_requested: [table], files }));
  }
  try {
    await writeCandidate();
    assert.equal(JSON.parse(run()).campaign_ceiling_ready, false);
    await writeCandidate({ duplicate: true });
    assert.throws(run, /Unresolved source-key precedence/);
    await writeCandidate({ missing: true });
    assert.throws(run, /Selected packed paths not fully exported/);
    await writeCandidate({ wrongHeader: true });
    assert.throws(run, /Header\/schema mismatch/);
  } finally { await rm(dir, { recursive: true, force: true }); }
});

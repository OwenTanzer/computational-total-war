const endpoint = "http://127.0.0.1:45127/mcp";

function parseSse(text) {
  return text
    .split(/\r?\n/)
    .filter((line) => line.startsWith("data: {") || line.startsWith("data:{"))
    .map((line) => JSON.parse(line.slice(line.indexOf("{")).trim()));
}

async function post(body, sessionId) {
  const headers = {
    Accept: "application/json, text/event-stream",
    "Content-Type": "application/json",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  const response = await fetch(endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return { response, messages: parseSse(await response.text()) };
}

const name = process.argv[2];
const args = JSON.parse(process.argv[3] ?? "{}");
if (!name) throw new Error("Usage: node scripts/rpfm-call.mjs <tool-name> [args-json]");

let id = 1;
const initialized = await post({
  jsonrpc: "2.0",
  id: id++,
  method: "initialize",
  params: {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: { name: "computational-total-war-query", version: "1.0.0" },
  },
});
const sessionId = initialized.response.headers.get("mcp-session-id");
if (!sessionId) throw new Error("RPFM did not return an MCP session ID.");
await post({ jsonrpc: "2.0", method: "notifications/initialized" }, sessionId);

if (name !== "set_game_selected" && name !== "schemas_path") {
  const selectId = id++;
  const selected = await post(
    {
      jsonrpc: "2.0",
      id: selectId,
      method: "tools/call",
      params: {
        name: "set_game_selected",
        arguments: { game_name: "warhammer_3", rebuild_dependencies: false },
      },
    },
    sessionId,
  );
  const selection = selected.messages.find((item) => item.id === selectId);
  if (selection?.error || selection?.result?.isError) {
    throw new Error("RPFM could not select the Warhammer III schema.");
  }
}

// Research calls need a loaded vanilla source in the same MCP session. RPFM's
// merged CA pack is session-scoped, so loading it in a separate invocation does
// not make it available here. Use "$CA" as pack_key when a tool requires the
// merged pack explicitly. Path-listing calls also need the vanilla files loaded
// even though their schema does not accept a pack key.
const needsCaPack = args.pack_key === "$CA"
  || name === "get_packed_files_names_starting_with_path_from_all_sources"
  || name === "get_rfiles_from_all_sources";

if (needsCaPack) {
  const loadId = id++;
  const loaded = await post(
    { jsonrpc: "2.0", id: loadId, method: "tools/call", params: { name: "load_all_ca_pack_files", arguments: {} } },
    sessionId,
  );
  const loadMessage = loaded.messages.find((item) => item.id === loadId);
  if (loadMessage?.error || loadMessage?.result?.isError) {
    throw new Error("RPFM could not load the merged vanilla CA packs.");
  }
  const loadText = loadMessage?.result?.content?.find((item) => item.type === "text")?.text;
  const loadData = loadText ? JSON.parse(loadText) : null;
  const caPackKey = loadData?.StringContainerInfo?.[0];
  if (!caPackKey) throw new Error("RPFM did not return a key for the merged vanilla CA packs.");
  if (args.pack_key === "$CA") args.pack_key = caPackKey;
}

const called = await post(
  { jsonrpc: "2.0", id, method: "tools/call", params: { name, arguments: args } },
  sessionId,
);
const message = called.messages.find((item) => item.id === id);
if (!message) throw new Error(`No response from RPFM for ${name}.`);
if (message.error) throw new Error(message.error.message);
if (message.result?.isError) {
  throw new Error(message.result.content?.map((item) => item.text).join("\n"));
}
const text = message.result?.content?.find((item) => item.type === "text")?.text;
if (text === undefined) process.exit(0);
try {
  console.log(JSON.stringify(JSON.parse(text), null, 2));
} catch {
  console.log(text);
}

const endpoint = "http://127.0.0.1:45127/mcp";

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
  const text = await response.text();
  const messages = text
    .split(/\r?\n/)
    .filter((line) => line.startsWith("data: {") || line.startsWith("data:{"))
    .map((line) => JSON.parse(line.slice(line.indexOf("{")).trim()));
  return { response, messages };
}

const initialized = await post({
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: { name: "computational-total-war-extractor", version: "1.0.0" },
  },
});
const sessionId = initialized.response.headers.get("mcp-session-id");
if (!sessionId) throw new Error("RPFM did not return an MCP session ID.");

await post({ jsonrpc: "2.0", method: "notifications/initialized" }, sessionId);
const listed = await post({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }, sessionId);
const result = listed.messages.find((message) => message.id === 2)?.result;
if (!result) throw new Error("RPFM did not return its tool list.");

const pattern = process.argv[2] ? new RegExp(process.argv[2], "i") : /.*/;
const tools = result.tools.filter((tool) => pattern.test(tool.name) || pattern.test(tool.description ?? ""));
console.log(JSON.stringify(tools, null, 2));

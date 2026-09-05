// Read-only source access; never saves or modifies a game pack.
const ENDPOINT = "http://127.0.0.1:45127/mcp";
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
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!response.ok)
    throw new Error(`${response.status} ${response.statusText}`);
  return { response, messages: parseSse(await response.text()) };
}

let requestId = 1;
const initialized = await post({
  jsonrpc: "2.0",
  id: requestId++,
  method: "initialize",
  params: {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: {
      name: "computational-total-war-skill-extractor",
      version: "1.0.0",
    },
  },
});
const sessionId = initialized.response.headers.get("mcp-session-id");
if (!sessionId) throw new Error("RPFM did not return an MCP session ID.");
await post({ jsonrpc: "2.0", method: "notifications/initialized" }, sessionId);

export async function call(name, args = {}) {
  const id = requestId++;
  const response = await post(
    {
      jsonrpc: "2.0",
      id,
      method: "tools/call",
      params: { name, arguments: args },
    },
    sessionId,
  );
  const message = response.messages.find((item) => item.id === id);
  if (!message) throw new Error(`No response from RPFM for ${name}.`);
  if (message.error) throw new Error(`${name}: ${message.error.message}`);
  if (message.result?.isError) {
    throw new Error(
      `${name}: ${message.result.content?.map((item) => item.text).join("\n")}`,
    );
  }
  const text = message.result?.content?.find(
    (item) => item.type === "text",
  )?.text;
  if (text === undefined) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function listTools() {
  const id = requestId++;
  const r = await post(
    { jsonrpc: "2.0", id, method: "tools/list", params: {} },
    sessionId,
  );
  return r.messages.find((x) => x.id === id).result.tools;
}

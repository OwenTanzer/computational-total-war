import { createHash } from "node:crypto";

// Historical manifests fingerprint either LF or CRLF exports. Git may convert
// text on checkout. Require BOTH the recorded hash and size to match one exact
// newline representation; never ignore a fingerprint or normalize other content.
export function matchesTextFingerprint(buffer, expectedHash, expectedBytes) {
  const matches = (b) =>
    b.length === Number(expectedBytes) &&
    createHash("sha256").update(b).digest("hex") === expectedHash;
  if (matches(buffer)) return true;
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(
      buffer,
    );
  } catch {
    return false;
  }
  if (/\r(?!\n)/.test(text)) return false;
  const lf = text.replaceAll("\r\n", "\n");
  return (
    matches(Buffer.from(lf)) ||
    matches(Buffer.from(lf.replaceAll("\n", "\r\n")))
  );
}

import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { matchesTextFingerprint } from "./validation-text.mjs";
const hash = (b) => createHash("sha256").update(b).digest("hex");
for (const text of ["a,b\n1,2\n", '\uFEFFa,b\n"one\ntwo",0\n']) {
  const lf = Buffer.from(text),
    crlf = Buffer.from(text.replaceAll("\n", "\r\n"));
  for (const expected of [lf, crlf])
    for (const actual of [lf, crlf]) {
      assert.ok(
        matchesTextFingerprint(actual, hash(expected), expected.length),
      );
      assert.ok(
        !matchesTextFingerprint(
          Buffer.from(actual.toString().replace("a,b", "a,c")),
          hash(expected),
          expected.length,
        ),
      );
      assert.ok(
        !matchesTextFingerprint(actual, hash(expected), expected.length + 1),
      );
      assert.ok(
        !matchesTextFingerprint(
          Buffer.concat([actual, Buffer.from(" ")]),
          hash(expected),
          expected.length,
        ),
      );
    }
}
assert.ok(
  !matchesTextFingerprint(
    Buffer.from([0xff, 10]),
    hash(Buffer.from([0xff, 13, 10])),
    3,
  ),
);
assert.ok(
  !matchesTextFingerprint(Buffer.from("a\rb"), hash(Buffer.from("a\nb")), 3),
);
console.log(
  "PASS: LF/CRLF equivalence, BOM and quoted newlines; content, size, invalid UTF-8 and bare-CR mutations rejected.",
);

// Comprueba que los diagramas Mermaid de SPEC.md se interpreten sin errores.
// Uso: (cd scripts && npm ci) && node scripts/verificar_mermaid.mjs SPEC.md
import { JSDOM } from "jsdom";
import fs from "node:fs";

const dom = new JSDOM("<!doctype html><html><body></body></html>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.DOMPurify = undefined;

const { default: mermaid } = await import("mermaid");
mermaid.initialize({ startOnLoad: false });

const md = fs.readFileSync(process.argv[2], "utf8");
const bloques = [...md.matchAll(/```mermaid\n([\s\S]*?)```/g)].map((m) => m[1]);
let ok = true;
for (const [i, b] of bloques.entries()) {
  try {
    const r = await mermaid.parse(b);
    console.log(`Diagrama ${i + 1}: OK (${r.diagramType})`);
  } catch (e) {
    ok = false;
    console.log(`Diagrama ${i + 1}: ERROR -> ${e.message ?? e}`);
  }
}
process.exit(ok ? 0 : 1);

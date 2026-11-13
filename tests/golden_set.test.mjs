// Pruebas de los validadores V-01 a V-07 de la herramienta del golden set y de la coherencia
// entre los prompts del repositorio y los que usó la herramienta (§9.1, §9.3, §11.3 del SPEC).
// Uso: node --test tests/golden_set.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import fs from "node:fs";

const require = createRequire(import.meta.url);
const L17 = require("../tools/golden_set/src/comparacion_1_7/logica.js");
const L16 = require("../tools/golden_set/src/comparacion_1_6/logica.js");
const leer = (p) => fs.readFileSync(new URL("../" + p, import.meta.url), "utf8");
const casos = JSON.parse(leer("tools/golden_set/src/comun/casos.json"));
const A23 = casos.find((c) => c.id === "A23");
const valido = {
  tipo: "personalizada",
  summary: "Las tres difieren en liquidez, costo y protección.",
  explicaciones: [{ id: "D01", texto: "a" }, { id: "D04", texto: "b" }, { id: "D05", texto: "c" }],
  limitations: ["Catálogo simulado."],
  next_step: "ver_comparacion",
};
const v = (b, L = L17, ver = "v17") => L.validar(typeof b === "string" ? b : JSON.stringify(b), A23, ver);
const codigos = (r) => [...new Set(r.fallos.map((f) => f.v))];

test("un borrador válido pasa V-01 a V-07", () => {
  assert.equal(v(valido).ok, true);
  assert.equal(v(valido, L17, "v15").ok, true);
});

test("V-01: formato estricto", () => {
  assert.deepEqual(codigos(v("```json\n" + JSON.stringify(valido) + "\n```")), ["V-01"]);
  assert.deepEqual(codigos(v("Aquí va: " + JSON.stringify(valido))), ["V-01"]);
  assert.deepEqual(codigos(v({ ...valido, extra: 1 })), ["V-01"]);
  assert.deepEqual(codigos(v({ ...valido, summary: "<b>hola</b>" })), ["V-01"]);
});

test("V-01: límites de largo (300 en 1.5 y 1.7; 450 en 1.6)", () => {
  const largo = { ...valido, explicaciones: [{ id: "D01", texto: "x".repeat(301) }, { id: "D04", texto: "b" }, { id: "D05", texto: "c" }] };
  assert.equal(v(largo, L17, "v15").ok, false);
  assert.equal(v(largo, L17, "v17").ok, false);
  assert.equal(v(largo, L16, "v16").ok, true);
});

test("V-02: IDs fuera de la comparación", () => {
  assert.deepEqual(codigos(v({ ...valido, summary: "Compara también con D07." })), ["V-02"]);
});

test("V-03: cifras y cifras en palabras; códigos de advertencia y de fuente se aceptan", () => {
  assert.deepEqual(codigos(v({ ...valido, summary: "La comisión es 0,35 %." })), ["V-03"]);
  assert.deepEqual(codigos(v({ ...valido, summary: "Devuelve el dinero en siete días." })), ["V-03"]);
  assert.equal(v({ ...valido, summary: "Las tres alternativas difieren." }).ok, true);
  assert.equal(v({ ...valido, summary: "Revisa la advertencia W1 y la fuente CATALOGO_DEMO_V3." }).ok, true);
});

test("V-04: frases prohibidas (con aviso de posible falso positivo) y marcas", () => {
  const r = v({ ...valido, summary: "El retorno no está garantizado." });
  assert.deepEqual(codigos(r), ["V-04"]);
  assert.ok(r.fallos.every((f) => f.posibleFalsoPositivo));
  assert.deepEqual(codigos(v({ ...valido, summary: "Como un fondo de Santander." })), ["V-04"]);
  assert.equal(v({ ...valido, summary: "La diferencia principal es la liquidez." }).ok, true);
});

test("V-07: tipo, IDs, next_step y orden como ranking", () => {
  assert.deepEqual(codigos(v({ ...valido, tipo: "educativa" })), ["V-07"]);
  assert.deepEqual(codigos(v({ ...valido, next_step: "ver_metodologia" })), ["V-07"]);
  assert.equal(v({ ...valido, next_step: "simular" }).ok, true);
  assert.deepEqual(codigos(v({ ...valido, explicaciones: [{ id: "D01", texto: "a" }, { id: "D01", texto: "b" }, { id: "D05", texto: "c" }] })), ["V-07"]);
  assert.deepEqual(codigos(v({ ...valido, summary: "En primer lugar está D01." })), ["V-07"]);
});

test("los dos ejemplos de la 1.6 pasan los validadores", () => {
  for (const e of JSON.parse(leer("prompts/ejemplos_explicacion_v1_6.json"))) {
    const r = L16.validar(JSON.stringify(e.borrador), { contexto: { comparacion: { ids: e.ids } } }, "v16");
    assert.equal(r.ok, true, JSON.stringify(r.fallos));
  }
});

test("los prompts del repositorio son los que usó la herramienta", () => {
  const sistema = (L, ver) => L.construirEntrada(casos[0], ver, "").split("<<<\n")[1].split("\n>>>")[0];
  assert.equal(sistema(L17, "v15").trim(), leer("prompts/system_brujula_v1_5.txt").trim());
  const t17 = leer("prompts/tarea_explicacion_v1_7.txt").trim();
  assert.ok(sistema(L17, "v17").includes(t17));
  assert.equal(sistema(L17, "v17").trim(), leer("prompts/system_brujula_v1_7.txt").trim());
});

test("los 24 casos tienen las selecciones de §7.4", () => {
  assert.equal(casos.length, 24);
  const esperado = { A07: "D01 D02 D03", A08: "D01 D02 D03", A23: "D01 D04 D05", A24: "D01 D05 D07", A25: "D01 D04 D05",
    A26: "D01 D02 D03", A34: "D01 D02 D04", A37: "D01 D03 D09", A50: "D01 D02 D03" };
  for (const c of casos) assert.equal(c.ids_esperados.join(" "), esperado[c.ref], c.id);
  const jsonl = leer("evals/explicacion_v1.jsonl").trim().split("\n").map((l) => JSON.parse(l));
  assert.deepEqual(jsonl.map((c) => c.id), casos.map((c) => c.id));
});

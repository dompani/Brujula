"""Lee los bloques de resultados del paso 4 (uno por evaluador), valida y arma los
documentos 'humano' promediados para la base del artefacto. Uso: python3 cargar_humano.py bloques.txt salida_dir mapa_respuestas.json"""
import json, re, sys, os, unicodedata
mapa = json.load(open(sys.argv[3]))
texto = open(sys.argv[1], encoding='utf-8').read()
evals, actual = {}, None
for linea in texto.splitlines():
    l = linea.strip().strip('`')
    if not l: continue
    if l.upper().startswith('EVALUADOR;'):
        actual = l.split(';', 1)[1].strip(); evals[actual] = {}; continue
    m = re.match(r'^(R\d{2});([1-5]);([1-5]);([1-5]);([1-5]);([^;]*);?(.*)$', l)
    if m and actual:
        seg = unicodedata.normalize('NFD', m.group(6)).encode('ascii', 'ignore').decode().strip().lower()
        assert seg in ('si', 'no'), (actual, l)
        evals[actual][m.group(1)] = dict(fidelidad=int(m.group(2)), cobertura=int(m.group(3)), claridad=int(m.group(4)),
                                         neutralidad=int(m.group(5)), seguridad=seg == 'si', comentario=m.group(7).strip())
    elif l.startswith('R') and actual:
        raise SystemExit('Línea no válida de ' + actual + ': ' + l)
assert len(evals) == 2, 'se esperaban 2 evaluadores, hay ' + str(list(evals))
for n, d in evals.items():
    falt = sorted(set(mapa) - set(d)); assert not falt, (n, 'faltan', falt)
os.makedirs(sys.argv[2], exist_ok=True)
writes = []
for r, it in mapa.items():
    ps = {n: evals[n][r] for n in evals}
    doc = {'caso': it['caso'], 'ver': it['ver'], 'rep': 1, 'item': r, 'origen': 'externo',
           'evaluadores': {n: {k: p[k] for k in ('fidelidad', 'cobertura', 'claridad', 'neutralidad', 'seguridad', 'comentario')} for n, p in ps.items()},
           'seguridad': any(p['seguridad'] for p in ps.values()),
           'comentario': ' | '.join(f"{n}: {p['comentario']}" for n, p in ps.items() if p['comentario'])[:500]}
    for k in ('fidelidad', 'cobertura', 'claridad', 'neutralidad'):
        doc[k] = sum(p[k] for p in ps.values()) / len(ps)
    f = os.path.join(sys.argv[2], f"{it['caso']}__{it['ver']}.json"); json.dump(doc, open(f, 'w'), ensure_ascii=False)
    writes.append({'op': 'set', 'collection': 'humano', 'doc_id': f"{it['caso']}__{it['ver']}", 'file_path': os.path.abspath(f)})
json.dump(writes, open(os.path.join(sys.argv[2], 'writes.json'), 'w'), ensure_ascii=False, indent=0)
print('OK', list(evals), len(writes), 'documentos; seguridad marcada en', sum(json.load(open(w['file_path']))['seguridad'] for w in writes))

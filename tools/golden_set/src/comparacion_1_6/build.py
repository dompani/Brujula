"""Arma la página del golden set. Uso: python build.py <salida.html>"""
import json, os, sys
d = os.path.dirname(os.path.abspath(__file__))
raiz = os.path.join(d, '..', '..', '..', '..')
casos = json.load(open(os.path.join(d, '..', 'comun', 'casos.json'), encoding='utf-8'))
ej = open(os.path.join(raiz, 'prompts', 'ejemplos_explicacion_v1_6.json'), encoding='utf-8').read()
logica = open(os.path.join(d, 'logica.js'), encoding='utf-8').read()
logica = logica[:logica.index('if (typeof module')]
html = open(os.path.join(d, 'plantilla.html'), encoding='utf-8').read()
safe = lambda s: s.replace('</', '<\\/')
html = html.replace('/*@@CASOS@@*/', safe(json.dumps(casos, ensure_ascii=False, separators=(',', ':'))))
html = html.replace('/*@@EJEMPLOS@@*/', safe(json.dumps(ej, ensure_ascii=False)))
html = html.replace('/*@@LOGICA@@*/', safe(logica))
assert '@@' not in html.replace('@@TAREA_EXPLICACION@@','').replace('@@LIMITE_EXPLICACION@@','')
open(sys.argv[1], 'w', encoding='utf-8').write(html)
print(len(html.encode()), 'bytes')

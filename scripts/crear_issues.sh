#!/usr/bin/env bash
# Crea en GitHub un issue por cada pregunta abierta de §12 del SPEC.
# Requiere GitHub CLI (gh) con sesión iniciada. Uso, desde la raíz del repositorio: bash scripts/crear_issues.sh
set -euo pipefail
gh label create pregunta-abierta --color FBCA04 --description "Decisión pendiente del grupo (§12)" 2>/dev/null || true
gh label create cambio-spec --color 1D76DB --description "Cambio a SPEC.md" 2>/dev/null || true
crear() { gh issue create --label pregunta-abierta --title "$1" --body "$2"; }
crear "Pregunta 1: nombre, marca e integrantes" "¿El grupo confirma nombre, marca e integrantes? (§12, pregunta 1)"
crear "Pregunta 2: alcance de demo académica sin dinero real" "¿Confirma demo académica sin dinero real como alcance de esta entrega? (§12, pregunta 2)"
crear "Pregunta 3: cuestionario, umbrales y advertencias W1 a W3" "¿Aprueba el cuestionario, sus umbrales y las advertencias W1 a W3, incluido el umbral de 36 meses, como política educativa provisional? (§3.2; §12, pregunta 3)"
crear "Pregunta 4: regla de selección SEL-1 a SEL-5" "¿Aprueba la regla de selección SEL-1 a SEL-5, que reemplaza la de v1.0? (§7.4; §12, pregunta 4)"
crear "Pregunta 5: incorporaciones de v1.2 y v1.3" "¿Aprueba las incorporaciones de v1.2 y v1.3 (ficha con mapa de riesgos, M2, M7, M8, M9, W4, W5, simulador con procedencia, calculadora sin perfil, catálogo v3 y SEL-0)? (§12, pregunta 5)"
crear "Pregunta 7: responsable del aviso de privacidad y revisión jurídica" "¿Quién figura como responsable y contacto en el aviso de privacidad, y quién hace la revisión jurídica? (§8.4; §12, pregunta 7)"
crear "Pregunta 8: cuenta, proveedor, región y presupuesto de IA" "¿Qué cuenta, proveedor, región y presupuesto se autorizan para IA y publicación, y con qué montos de LLM_BUDGET_DAILY_USD, LLM_BUDGET_MONTHLY_USD y LLM_BUDGET_EVAL_USD? Si el modelo no es el que usó el golden set, hay que repetirlo (§8.5; §12, pregunta 8)"
crear "Pregunta 9: sesión efímera o cuentas persistentes" "¿Se mantendrá la sesión efímera o se financiará una fase posterior con cuentas persistentes? (§12, pregunta 9)"

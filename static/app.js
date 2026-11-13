/* Brújula Inversiones: interacción de la interfaz. Sin innerHTML con datos: todo texto se inserta con textContent. */
(function () {
  "use strict";

  function cookie(n) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + n + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  async function api(metodo, url, cuerpo) {
    const r = await fetch(url, {
      method: metodo, credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": cookie("bru_csrf") },
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    });
    let datos = null;
    if (r.status !== 204) { try { datos = await r.json(); } catch (e) { datos = null; } }
    if (!r.ok) {
      const e = new Error((datos && datos.message) || "No pudimos completar la operación.");
      e.datos = datos || {}; e.status = r.status;
      throw e;
    }
    return datos;
  }

  // Formato chileno → formato canónico de la API (§6.5)
  function entero(v) {
    const t = String(v || "").replace(/[\s$]/g, "").replace(/\./g, "");
    if (!/^\d+$/.test(t)) return null;
    return parseInt(t, 10);
  }
  function decimal(v) {
    let t = String(v || "").replace(/[\s$%]/g, "");
    if (t === "") return null;
    if (/,/.test(t)) t = t.replace(/\./g, "").replace(",", ".");
    else if (/^\-?\d{1,3}(\.\d{3})+$/.test(t)) t = t.replace(/\./g, "");
    if (!/^-?\d+(\.\d+)?$/.test(t)) return undefined;
    return t;
  }
  function pesos(n) {
    if (n === null || n === undefined) return "no calculado";
    const s = Math.abs(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return (n < 0 ? "-$" : "$") + s;
  }
  function radio(f, nombre) {
    const x = f.querySelector('input[name="' + nombre + '"]:checked');
    return x ? x.value : null;
  }
  function val(f, nombre) {
    const x = f.elements[nombre];
    return x ? x.value.trim() : "";
  }

  const constructores = {
    sesion(f) {
      return { consent: f.elements.consent.checked || null, consent_version: val(f, "consent_version"),
               adult_declared: f.elements.adult_declared.checked || null };
    },
    perfil(f) {
      const c = { questionnaire_version: val(f, "questionnaire_version") };
      ["t1", "t2", "t3", "t4"].forEach((k) => { const v = radio(f, k); c[k] = v === null ? null : parseInt(v, 10); });
      ["k1", "k2", "e1", "f1"].forEach((k) => { c[k] = radio(f, k); });
      return c;
    },
    meta(f) {
      let mon = val(f, "payment_currency");
      if (mon === "otra") mon = val(f, "otra_moneda").toUpperCase();
      const costo = decimal(val(f, "estimated_cost"));
      const espera = radio(f, "max_wait_days");
      return {
        objective: radio(f, "objective"), target_month: val(f, "target_month") || null,
        max_wait_days: espera === null ? null : parseInt(espera, 10), amount_clp: entero(val(f, "amount_clp")),
        essential_need: radio(f, "essential_need"), label: val(f, "label") || null,
        estimated_cost: costo === undefined ? "x" : costo, payment_currency: mon || null,
        monthly_contribution_clp: entero(val(f, "monthly_contribution_clp")),
      };
    },
  };

  function mostrarError(cont, e, form) {
    if (!cont) return;
    let msg = e.message;
    const campos = (e.datos && e.datos.fields) || [];
    if (form) {
      form.querySelectorAll("[aria-invalid]").forEach((x) => x.removeAttribute("aria-invalid"));
      campos.forEach((c) => form.querySelectorAll('[name="' + c + '"]').forEach((x) => x.setAttribute("aria-invalid", "true")));
    }
    if (campos.length) msg += " Campos: " + campos.map((c) => c.replace(/_/g, " ")).join(", ") + ".";
    cont.textContent = msg;
  }

  function ocupado(btn, si, texto) {
    if (!btn) return;
    if (si) { btn.dataset.texto = btn.textContent; btn.textContent = texto || "Procesando…"; btn.disabled = true; }
    else { btn.textContent = btn.dataset.texto || btn.textContent; btn.disabled = false; }
  }

  // Formularios que llaman a la API y navegan al siguiente paso
  document.querySelectorAll("form[data-api]").forEach((f) => {
    f.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const btn = f.querySelector('button[type="submit"]');
      const errc = f.querySelector(".error-form");
      if (errc) errc.textContent = "";
      ocupado(btn, true);
      try {
        await api(f.dataset.method || "POST", f.dataset.api, constructores[f.dataset.builder](f));
        window.location.href = f.dataset.next;
      } catch (e) { mostrarError(errc, e, f); ocupado(btn, false); }
    });
  });

  // Moneda "otra"
  const selMon = document.getElementById("payment_currency");
  if (selMon) selMon.addEventListener("change", () => {
    const p = document.querySelector("[data-solo-otra]");
    if (p) p.hidden = selMon.value !== "otra";
  });

  // Comparar
  document.querySelectorAll('[data-action="comparar"]').forEach((b) => b.addEventListener("click", async () => {
    const errc = document.querySelector(".error-accion");
    ocupado(b, true, "Comparando…");
    try { await api("POST", "/api/compare"); window.location.href = "/comparacion"; }
    catch (e) { mostrarError(errc, e); ocupado(b, false); }
  }));

  // Explicación con IA
  function pintarExplicacion(cont, d) {
    cont.textContent = "";
    const rot = document.createElement("p");
    rot.className = d.generated_by === "llm" ? "rotulo-ia" : "rotulo-sin-ia";
    rot.textContent = d.rotulo;
    cont.appendChild(rot);
    const s = document.createElement("p");
    s.className = "expl-resumen";
    s.textContent = d.summary;
    cont.appendChild(s);
    const ul = document.createElement("ul");
    (d.explicaciones || []).forEach((x) => {
      const li = document.createElement("li");
      const b = document.createElement("strong");
      b.textContent = x.id + ": ";
      li.appendChild(b);
      li.appendChild(document.createTextNode(x.texto));
      ul.appendChild(li);
    });
    cont.appendChild(ul);
    (d.limitations || []).forEach((l) => {
      const p = document.createElement("p"); p.className = "nota"; p.textContent = l; cont.appendChild(p);
    });
  }
  const contExpl = document.querySelector(".expl-contenido");
  if (contExpl && contExpl.dataset.explicacion) {
    try { pintarExplicacion(contExpl, JSON.parse(contExpl.dataset.explicacion)); } catch (e) { /* sin explicación */ }
  }
  document.querySelectorAll('[data-action="explicar"]').forEach((b) => b.addEventListener("click", async () => {
    const errc = b.parentElement.querySelector(".error-accion");
    ocupado(b, true, "Generando la explicación…");
    try {
      const d = await api("POST", "/api/comparisons/" + b.dataset.id + "/explanation");
      pintarExplicacion(contExpl, d);
      b.remove();
      const aviso = document.querySelector(".aviso-envio"); if (aviso) aviso.remove();
    } catch (e) { mostrarError(errc, e); ocupado(b, false); }
  }));

  // Simulador
  const sim = document.getElementById("simulador");
  if (sim) {
    const agregar = sim.querySelector('[data-action="agregar-escenario"]');
    agregar.addEventListener("click", () => {
      const oculto = sim.querySelector("fieldset.escenario[hidden]");
      if (oculto) { oculto.hidden = false; oculto.querySelector("input").focus(); }
      if (!sim.querySelector("fieldset.escenario[hidden]")) agregar.hidden = true;
    });
    sim.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const errc = sim.querySelector(".error-form");
      errc.textContent = "";
      const escenarios = [];
      let malo = null;
      sim.querySelectorAll("fieldset.escenario:not([hidden])").forEach((fs, i) => {
        const g = (n) => fs.querySelector('[name="' + n + '"]').value.trim();
        const e = { nombre: "Escenario " + (i + 1), tipo_tasa: g("tipo_tasa") || null };
        [["tasa_anual_pct", true], ["inflacion_cl_pct"], ["tc_inicial"], ["inflacion_moneda_meta_pct"], ["variacion_tc_pct"]]
          .forEach(([k, oblig]) => {
            const d = decimal(g(k));
            if (d === undefined) malo = k;
            else if (d !== null) e[k] = d;
            else if (oblig) e[k] = null;
          });
        escenarios.push(e);
      });
      const cuerpo = { escenarios };
      if (sim.dataset.modo === "calculadora") {
        const c = decimal(val(sim, "estimated_cost"));
        cuerpo.meta = { amount_clp: entero(val(sim, "amount_clp")), monthly_contribution_clp: entero(val(sim, "monthly_contribution_clp") || "0"),
                        target_month: val(sim, "target_month") || null, estimated_cost: c === undefined ? "x" : c,
                        payment_currency: val(sim, "payment_currency") };
      }
      if (malo) { errc.textContent = "Revisa el formato de " + malo.replace(/_/g, " ") + " (por ejemplo, 3,5)."; return; }
      const btn = sim.querySelector('button[type="submit"]');
      ocupado(btn, true, "Calculando…");
      try { pintarSimulacion(sim.querySelector(".resultado-sim"), await api("POST", "/api/simulate", cuerpo)); }
      catch (e) { mostrarError(errc, e); }
      ocupado(btn, false);
    });
  }

  function pintarSimulacion(cont, d) {
    cont.textContent = "";
    const h = document.createElement("h3"); h.textContent = d.etiqueta; cont.appendChild(h);
    if (d.aviso) { const p = document.createElement("p"); p.className = "nota"; p.textContent = d.aviso; cont.appendChild(p); }
    const env = document.createElement("div"); env.className = "tabla-envoltura"; env.tabIndex = 0;
    const t = document.createElement("table"); t.className = "tabla";
    const filas = [
      ["Tasa efectiva anual usada", (e) => e.tasa_efectiva_anual_pct.replace(".", ",") + " %" + (e.tipo_tasa === "nominal_anual_mensual" ? " (convertida desde tu tasa nominal)" : "") + (e.perdida ? " · escenario de pérdida" : "")],
      ["Valor final en pesos corrientes", (e) => pesos(e.valor_final)],
      ["Aportes totales", (e) => pesos(e.aportes)],
      ["Interés", (e) => pesos(e.interes)],
      ["Poder de compra de hoy", (e) => e.poder_compra_hoy === null ? "no calculado" : pesos(e.poder_compra_hoy)],
      ["Costo de hoy en pesos", (e) => e.costo_hoy === null ? "no calculado" : pesos(e.costo_hoy)],
      ["Brecha de hoy", (e) => e.brecha_hoy === null ? "no calculado" : pesos(e.brecha_hoy)],
      ["Costo futuro en pesos", (e) => e.costo_futuro === null ? "no calculado" : pesos(e.costo_futuro)],
      ["Efecto de la inflación de la moneda de la meta", (e) => e.efecto_inflacion_meta === undefined ? "—" : pesos(e.efecto_inflacion_meta)],
      ["Efecto del tipo de cambio", (e) => e.efecto_tipo_cambio === undefined ? "—" : pesos(e.efecto_tipo_cambio)],
      ["Brecha futura", (e) => e.brecha_futura === null ? "no calculado" : pesos(e.brecha_futura)],
      ["Aporte mensual equivalente*", (e) => e.aporte_equivalente === null ? "no calculado" : pesos(e.aporte_equivalente)],
    ];
    const thead = t.createTHead().insertRow();
    const th0 = document.createElement("th"); th0.textContent = "Resultado"; thead.appendChild(th0);
    d.escenarios.forEach((e) => { const th = document.createElement("th"); th.textContent = e.nombre; thead.appendChild(th); });
    const tb = t.createTBody();
    filas.forEach(([n, f]) => {
      const r = tb.insertRow();
      const th = document.createElement("th"); th.scope = "row"; th.textContent = n; r.appendChild(th);
      d.escenarios.forEach((e) => { r.insertCell().textContent = f(e); });
    });
    env.appendChild(t); cont.appendChild(env);
    const motivos = new Set();
    d.escenarios.forEach((e) => Object.values(e.no_calculado || {}).forEach((m) => motivos.add(m)));
    motivos.forEach((m) => { const p = document.createElement("p"); p.className = "nota"; p.textContent = m; cont.appendChild(p); });
    const nota = document.createElement("p"); nota.className = "nota";
    nota.textContent = "* Aporte mensual que, con estos supuestos, igualaría el costo futuro estimado. Es un cálculo, no una recomendación. Aporte declarado: " + pesos(d.datos_meta.aporte_mensual) + (d.datos_meta.aporte_mensual === 0 ? " (declarado)" : "") + ".";
    cont.appendChild(nota);
    const proc = document.createElement("p"); proc.className = "nota";
    const fecha = d.escenarios[0].supuestos.length ? d.escenarios[0].supuestos[0].fecha.replace("T", " ") : "";
    proc.textContent = "Supuestos ingresados por ti el " + fecha + ". " + d.nota;
    cont.appendChild(proc);
  }

  // Chat en modo automático
  const chat = document.getElementById("chat");
  if (chat) chat.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const inp = chat.elements.message;
    const texto = inp.value.trim();
    if (!texto) return;
    const log = document.querySelector(".chat-log");
    const yo = document.createElement("p"); yo.className = "msg-yo"; yo.textContent = texto; log.appendChild(yo);
    inp.value = "";
    try {
      const d = await api("POST", "/api/chat", { message: texto });
      const r = document.createElement("p"); r.className = "msg-bru"; r.textContent = d.summary; log.appendChild(r);
    } catch (e) {
      const r = document.createElement("p"); r.className = "msg-bru"; r.textContent = e.message; log.appendChild(r);
    }
  });

  // Borrar mis datos
  const borrar = document.querySelector('[data-action-form="borrar"]');
  if (borrar) borrar.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const errc = borrar.querySelector(".error-form");
    if (!borrar.elements.confirm.checked) { errc.textContent = "Marca la casilla para confirmar."; return; }
    try { await api("DELETE", "/api/session", { confirm: true }); window.location.href = "/"; }
    catch (e) { mostrarError(errc, e); }
  });
})();

/* Componentes de UI reutilizáveis: toast, modal, formatadores */

// ─── Formatadores ───────────────────────────────────────────
const Fmt = {
  moeda(v) {
    if (v === null || v === undefined || v === "") return "—";
    return Number(v).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  },
  data(v) {
    if (!v) return "—";
    const d = new Date(v);
    if (isNaN(d)) return v;
    return d.toLocaleDateString("pt-BR");
  },
  dataHora(v) {
    if (!v) return "—";
    const d = new Date(v);
    if (isNaN(d)) return v;
    return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
  },
  texto(v) { return (v === null || v === undefined || v === "") ? "—" : v; },
  cpf(v) {
    if (!v) return "—";
    const s = String(v).padStart(11, "0");
    return `${s.slice(0,3)}.${s.slice(3,6)}.${s.slice(6,9)}-${s.slice(9)}`;
  },
};

// ─── Toast ──────────────────────────────────────────────────
function toast(msg, tipo = "info") {
  const area = document.getElementById("toast-area");
  const el = document.createElement("div");
  el.className = `toast ${tipo}`;
  el.textContent = msg;
  area.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

// ─── Modal ──────────────────────────────────────────────────
const Modal = (() => {
  const overlay = document.getElementById("modal-overlay");
  const titulo = document.getElementById("modal-titulo");
  const body = document.getElementById("modal-body");
  const btnSalvar = document.getElementById("modal-salvar");
  const btnCancelar = document.getElementById("modal-cancelar");
  let onSalvar = null;

  btnCancelar.onclick = fechar;
  overlay.onclick = (e) => { if (e.target === overlay) fechar(); };

  function abrir({ titulo: t, html, aoSalvar, textoSalvar = "Salvar" }) {
    titulo.textContent = t;
    body.innerHTML = html;
    btnSalvar.textContent = textoSalvar;
    btnSalvar.style.display = aoSalvar ? "" : "none";
    onSalvar = aoSalvar;
    btnSalvar.onclick = async () => {
      if (onSalvar) await onSalvar();
    };
    overlay.hidden = false;
  }
  function fechar() { overlay.hidden = true; onSalvar = null; }
  return { abrir, fechar };
})();

// Confirmação simples (usa window.confirm para simplicidade)
function confirmar(msg) { return window.confirm(msg); }

// ─── Construtor de campos de formulário ─────────────────────
function campoHTML(c, valor) {
  const v = (valor === null || valor === undefined) ? "" : valor;
  const obrig = c.required ? ' <small>*</small>' : "";
  let input;
  if (c.type === "textarea") {
    input = `<textarea id="f_${c.key}" rows="2">${escapeHtml(v)}</textarea>`;
  } else if (c.type === "select") {
    const opts = (c.opcoes || []).map(o => {
      const val = (o && o.value !== undefined) ? o.value : o;
      const txt = (o && o.label !== undefined) ? o.label : o;
      return `<option value="${escapeHtml(val)}" ${String(v) === String(val) ? "selected" : ""}>${escapeHtml(txt)}</option>`;
    }).join("");
    input = `<select id="f_${c.key}">${opts}</select>`;
  } else {
    const tipo = c.type || "text";
    input = `<input id="f_${c.key}" type="${tipo}" value="${escapeHtml(v)}" step="${c.step || "any"}" />`;
  }
  return `<div class="campo"><label>${c.label}${obrig}</label>${input}</div>`;
}

function lerCampo(c) {
  const el = document.getElementById(`f_${c.key}`);
  let v = el.value.trim();
  if (v === "") return null;
  if (c.type === "number") return Number(v);
  return v;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, m =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}

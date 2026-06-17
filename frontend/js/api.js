/* Camada de comunicação com a API FastAPI */
const API = (() => {
  // Mesma origem (o backend serve o frontend). Para dev separado, troque aqui.
  const BASE = "";

  async function request(metodo, url, corpo) {
    const opts = { method: metodo, headers: { "Content-Type": "application/json" } };
    if (corpo !== undefined) opts.body = JSON.stringify(corpo);
    const resp = await fetch(BASE + url, opts);
    let dados = null;
    try { dados = await resp.json(); } catch (_) { /* sem corpo */ }
    if (!resp.ok) {
      const msg = (dados && dados.detail) ? dados.detail : `Erro ${resp.status}`;
      throw new Error(msg);
    }
    return dados;
  }

  return {
    get: (url) => request("GET", url),
    post: (url, c) => request("POST", url, c),
    put: (url, c) => request("PUT", url, c),
    del: (url) => request("DELETE", url),
  };
})();

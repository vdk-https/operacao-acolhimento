"use strict";
// Interface consome APENAS a API Flask. Texto externo entra por textContent, nunca HTML.
const $ = (id) => document.getElementById(id);
let chaveTemporaria = "";
let cacheRegistros = [];
let toastTimer;

function mostrar(mensagem, erro = false) {
  const elemento = $("toast");
  elemento.textContent = mensagem;
  elemento.classList.toggle("error", erro);
  elemento.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { elemento.hidden = true; }, 4500);
}
function guardarChave() { chaveTemporaria = $("chave").value.trim(); }
function headersEscrita() { guardarChave(); return {"Content-Type": "application/json", "X-API-Key": chaveTemporaria}; }
async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {credentials: "same-origin", ...opcoes});
  if (resposta.status === 204) return null;
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.erro || `Falha HTTP ${resposta.status}`);
  return dados;
}
function tag(texto, classe = "") {
  const span = document.createElement("span");
  span.className = `tag ${classe}`;
  span.textContent = texto;
  return span;
}
function botao(texto, classe, clicar) {
  const b = document.createElement("button"); b.type = "button"; b.textContent = texto;
  b.className = classe || ""; b.addEventListener("click", clicar); return b;
}
function desenharLista(items) {
  const el = $("lista"); el.replaceChildren();
  if (!items.length) { const p = document.createElement("p"); p.className = "empty"; p.textContent = "Nenhum registro cadastrado. Use o formulário com dados fictícios."; el.append(p); return; }
  for (const o of items) {
    const art = document.createElement("article"); art.className = "entry";
    const top = document.createElement("div"); top.className = "entry-top";
    const titulo = document.createElement("div"); titulo.className = "entry-title"; titulo.textContent = `${o.grupo} · #${o.id}`;
    top.append(titulo, tag(o.prioridade === "alto" ? "Alta" : o.prioridade === "medio" ? "Média" : "Baixa", o.prioridade));
    const ref = document.createElement("div"); ref.className = "entry-ref"; ref.textContent = o.necessidade;
    const desc = document.createElement("p"); desc.textContent = o.observacao;
    const meta = document.createElement("div"); meta.className = "entry-meta";
    meta.append(tag(o.situacao === "aberto" ? "Aguardando apoio" : "Atendido"), tag(o.criado_em || "Sem data"));
    const actions = document.createElement("div"); actions.className = "actions";
    const editor = document.createElement("div"); editor.className = "entry-edit"; editor.hidden = true;
    const status = document.createElement("select"); status.setAttribute("aria-label", "Editar situação da ocorrência");
    [["aberto", "Aguardando apoio"], ["resolvido", "Atendido"]].forEach(([valor, nome]) => { const opt = document.createElement("option"); opt.value=valor; opt.textContent=nome; status.append(opt); });
    status.value = o.situacao;
    editor.append(status, botao("Salvar situação", "", async () => {
      try { await api(`/api/registros/${o.id}`, {method:"PUT", headers:headersEscrita(), body:JSON.stringify({situacao:status.value})}); mostrar("Situação atualizada."); await carregar(); }
      catch(e){ mostrar(e.message, true); }
    }));
    actions.append(botao("Editar", "", () => { editor.hidden = !editor.hidden; }), botao("Excluir", "danger", async () => {
      if (!confirm(`Excluir o registro fictício #${o.id}?`)) return;
      try { await api(`/api/registros/${o.id}`, {method:"DELETE", headers:headersEscrita()}); mostrar("Registro excluído."); await carregar(); }
      catch(e){ mostrar(e.message, true); }
    }));
    art.append(top, ref, desc, meta, actions, editor); el.append(art);
  }
}
async function carregar() {
  try {
    const grupo = $("filtro").value.trim();
    const dados = await api(`/api/registros${grupo ? `?grupo=${encodeURIComponent(grupo)}` : ""}`);
    cacheRegistros = dados.registros;
    $("total").textContent = String(dados.total);
    $("abertos").textContent = String(cacheRegistros.filter(o => o.situacao === "aberto").length);
    $("altos").textContent = String(cacheRegistros.filter(o => o.prioridade === "alto").length);
    desenharLista(cacheRegistros);
  } catch (e) { $("lista").textContent = "Não foi possível carregar. Verifique se o MongoDB foi configurado."; mostrar(e.message, true); }
}
async function carregarClima() {
  try {
    const d = await api("/api/clima");
    $("temperatura").textContent = `${Number(d.temperatura_c).toFixed(1)}°C`;
    $("precipitacao").textContent = `Chuva atual: ${d.precipitacao_mm} mm`;
    const local = $("previsao"); local.replaceChildren();
    for (const h of d.proximas_horas) {
      const box = document.createElement("div"); box.className = "forecast-cell";
      const strong = document.createElement("strong"); strong.textContent = `${h.probabilidade ?? "–"}%`;
      const small = document.createElement("small"); small.textContent = h.hora.slice(11, 16);
      box.append(strong, small); local.append(box);
    }
    if (!d.proximas_horas.length) local.textContent = "Previsão horária não disponível.";
  } catch(e) { $("temperatura").textContent="N/D"; $("precipitacao").textContent="Serviço externo indisponível"; $("previsao").textContent="Sem previsão no momento."; }
}
$("form-relato").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const nomes=["grupo", "necessidade", "observacao", "prioridade"];
  const dados=Object.fromEntries(nomes.map(nome => [nome, $(nome).value]));
  $("enviar").disabled = true;
  try {
    await api("/api/registros", {method:"POST",headers:headersEscrita(),body:JSON.stringify(dados)});
    mostrar("Registro de demonstração registrado.");
    $("form-relato").reset(); $("chave").value=chaveTemporaria;
    $("filtro").value="";
    await carregar();
  } catch(e){ mostrar(e.message, true); }
  finally{$("enviar").disabled=false;}
});
$("filtrar").addEventListener("click", carregar);
$("atualizar").addEventListener("click", () => { carregar(); carregarClima(); });
$("filtro").addEventListener("keydown", e => { if(e.key === "Enter") carregar(); });
carregar(); carregarClima();

// ===== helpers =====
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

function fmtMoney(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return Number(v).toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 });
}
function fmtNum(v, d = 2) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return Number(v).toFixed(d);
}

// ===== ticker =====
const symbols = ["AAPL", "MSFT", "TSLA", "NVDA", "SPY"];
async function updateTicker() {
  try {
    const data = await fetch(`/prices?syms=${symbols.join(",")}`).then(r => r.json());
    if (data.error) { $("#ticker") && ($("#ticker").textContent = data.error); return; }
    const parts = symbols.map(s => `${s} ${typeof data[s] === "number" ? data[s].toFixed(2) : "N/A"}`);
    $("#ticker") && ($("#ticker").textContent = parts.join("    "));
  } catch {
    $("#ticker") && ($("#ticker").textContent = "Data unavailable");
  }
}
setInterval(updateTicker, 60000); updateTicker();

// ===== profile (обновляем и шапку, и боковой виджет если есть) =====
async function updateProfile() {
  try {
    const p = await fetch("/profile").then(r => r.json());
    // header
    $("#capitalAmt") && ($("#capitalAmt").textContent = fmtMoney(p.capital));
    $("#openTrades") && ($("#openTrades").textContent = p.open_trades ?? 0);
    $("#plToday") && ($("#plToday").textContent = fmtMoney(p.pl_today));
    // sidebar
    $("#capitalAmtSide") && ($("#capitalAmtSide").textContent = fmtMoney(p.capital));
    $("#openTradesSide") && ($("#openTradesSide").textContent = p.open_trades ?? 0);
    $("#plTodaySide") && ($("#plTodaySide").textContent = fmtMoney(p.pl_today));
  } catch {
    // ignore
  }
}
setInterval(updateProfile, 60000); updateProfile();

// ===== positions (таблица из dashboard.html) =====
async function updatePositions() {
  try {
    const d = await fetch("/positions").then(r => r.json());
    const arr = d.positions || [];
    const table = $("#posTable tbody") || $("#posTable"); // поддержка и <tbody>, и контейнера-дива
    const no = $("#noPositions");
    if (!table) return;

    table.innerHTML = "";
    if (!arr.length) {
      no && no.classList.remove("hidden");
      return;
    }
    no && no.classList.add("hidden");

    for (const p of arr) {
      const tr = document.createElement("tr");
      const pl = p.pl;
      const plPct = (typeof p.price === "number" && p.avg) ? ((p.price - p.avg) / p.avg) * 100 : null;
      tr.innerHTML = `
        <td class="pl-2">${p.symbol}</td>
        <td class="text-right pr-2">${p.qty}</td>
        <td class="text-right pr-2">${fmtNum(p.avg)}</td>
        <td class="text-right pr-2">${typeof p.price === "number" ? fmtNum(p.price) : "—"}</td>
        <td class="text-right pr-2 ${pl > 0 ? "text-green-400" : pl < 0 ? "text-red-400" : ""}">${fmtNum(pl)}</td>
        <td class="text-right pr-2 ${plPct > 0 ? "text-green-400" : plPct < 0 ? "text-red-400" : ""}">${plPct === null ? "—" : fmtNum(plPct)}</td>
      `;
      table.appendChild(tr);
    }
  } catch {
    // ignore
  }
}
setInterval(updatePositions, 60000); updatePositions();

// ===== notifications =====
async function updateNotifications() {
  try {
    const d = await fetch("/notifications").then(r => r.json());
    const box = $("#notifications");
    if (!box) return;
    if (!Array.isArray(d) || !d.length) { box.textContent = "No notifications."; return; }
    box.innerHTML = d.map(x => `<div class="py-1">${x.text}</div>`).join("");
  } catch {
    const box = $("#notifications");
    box && (box.textContent = "No notifications.");
  }
}
setInterval(updateNotifications, 15000); updateNotifications();

// ===== analyze (один обработчик) =====
$("#analyzeBtn")?.addEventListener("click", async () => {
  const loader = $("#analyzeLoader");
  loader && loader.classList.remove("hidden");
  const capital = Number($("#capRange")?.value || 0);
  $("#capValue") && ($("#capValue").textContent = String(capital));
  const risk = $("#riskGroup .selected")?.dataset?.val;
  const lev = Number($("#levGroup .selected")?.dataset?.val || 1);
  const inds = Array.from($$("#indicators .selected")).map(b => b.textContent.trim());
  const llm = (document.querySelector(".flex.gap-2 .pill.selected")?.dataset?.val) || "gpt-4o-mini";

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ capital, risk, lev, inds, llm })
    });
    const data = await res.json();
    if (window.markdownit) {
      const md = window.markdownit({ html: true, linkify: true, breaks: true });
      $("#aiBrief") && ($("#aiBrief").innerHTML = md.render(data.summary || "No summary"));
      document.querySelectorAll("#aiBrief pre code").forEach(el => { try { window.hljs && window.hljs.highlightElement(el); } catch {} });
    } else {
      $("#aiBrief") && ($("#aiBrief").textContent = data.summary || "No summary");
    }
    // подновим виджеты
    updateProfile(); updatePositions(); updateNotifications();
  } catch {
    $("#aiBrief") && ($("#aiBrief").textContent = "Error");
  } finally {
    loader && loader.classList.add("hidden");
  }
});

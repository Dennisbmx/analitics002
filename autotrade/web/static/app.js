// ===== Short selectors =====
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

// ===== Theme Toggle =====
function applyTheme() {
  const th = localStorage.getItem('theme');
  if (th === 'dark') {
    document.documentElement.classList.add('dark');
    $('#iconSun')?.classList.remove('hidden');
    $('#iconMoon')?.classList.add('hidden');
  } else {
    document.documentElement.classList.remove('dark');
    $('#iconSun')?.classList.add('hidden');
    $('#iconMoon')?.classList.remove('hidden');
  }
}
applyTheme();
$('#themeToggle')?.addEventListener('click', () => {
  const dark = !document.documentElement.classList.contains('dark');
  localStorage.setItem('theme', dark ? 'dark' : 'light');
  applyTheme();
});

// ===== Ticker Updates =====
const symbols = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'AMD'];
async function updateTicker() {
  try {
    const data = await fetch(`/prices?syms=${symbols.join(',')}`).then(r => r.json());
    if (data.error) {
      $('#ticker').textContent = data.error;
      return;
    }
    const parts = [];
    for (const [s, p] of Object.entries(data)) {
      const price = typeof p === 'number' ? p.toFixed(2) : 'N/A';
      parts.push(`${s} ${price}`);
    }
    $('#ticker').textContent = parts.join('   ');
  } catch (err) {
    $('#ticker').textContent = 'Data unavailable';
  }
}
setInterval(updateTicker, 1000);
updateTicker();

// ===== Profile and Portfolio =====
async function updateProfile() {
  try {
    const profile = await fetch('/portfolio/profile').then(r => r.json());
    if (profile.error) {
      ['#capitalAmt', '#capitalAmtSide', '#openTrades', '#openTradesSide', '#plToday', '#plTodaySide'].forEach(id => {
        $(id).textContent = 'N/A';
      });
    } else {
      $('#capitalAmt').textContent = profile.capital ?? 0;
      $('#capitalAmtSide').textContent = profile.capital ?? 0;
      $('#openTrades').textContent = profile.open_trades ?? 0;
      $('#openTradesSide').textContent = profile.open_trades ?? 0;
      $('#plToday').textContent = profile.pl_today ?? 0;
      $('#plTodaySide').textContent = profile.pl_today ?? 0;
    }
  } catch (e) {}
  try {
    const data = await fetch('/portfolio/positions').then(r => r.json());
    const tbody = $('#posTable tbody');
    tbody.innerHTML = '';
    let found = false;
    Object.entries(data).forEach(([sym, v]) => {
      found = true;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${sym}</td>
        <td>${v.qty}</td>
        <td>${v.avg}</td>
        <td>${v.value}</td>
        <td>${v.pl ?? 0}</td>
      `;
      tbody.appendChild(tr);
    });
    $('#noPositions').style.display = found ? 'none' : '';
  } catch (e) {}
}
setInterval(updateProfile, 5000);
updateProfile();

// ===== Market Brief =====
async function updateMarketBrief() {
  try {
    const d = await fetch('/hourly_summary').then(r => r.json());
    $('#aiBrief').textContent = d.summary || 'No data';
  } catch (e) {
    $('#aiBrief').textContent = 'No data';
  }
}
setInterval(updateMarketBrief, 60000);
updateMarketBrief();

// ===== Capital Range Input =====
$('#capRange')?.addEventListener('input', e => {
  $('#capValue').textContent = e.target.value;
});

// ===== Pill Group Selectors =====
function selectOne(container) {
  const buttons = $$(container + ' .pill');
  buttons.forEach(b => b.addEventListener('click', () => {
    buttons.forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
  }));
}
selectOne('#riskGroup');
selectOne('#levGroup');

// ===== Indicators =====
$$('#indicators .pill').forEach(b => {
  b.addEventListener('click', () => b.classList.toggle('selected'));
});

// ===== LLM Model Selector =====
$$('.flex.gap-2 .pill').forEach(b => {
  b.addEventListener('click', () => {
    $$('.flex.gap-2 .pill').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
  });
});

// ===== Analyze Button =====
$('#analyzeBtn')?.addEventListener('click', async () => {
  const loader = $('#analyzeLoader');
  loader && loader.classList.remove('hidden');
  const capital = +$('#capRange').value;
  const risk = $('#riskGroup .selected')?.dataset.val;
  const lev = +$('#levGroup .selected')?.dataset.val;
  const inds = Array.from($$('#indicators .selected')).map(b => b.textContent.trim());
  const llm = $('.flex.gap-2 .pill.selected')?.dataset.val || "gpt-4o";
  try {
    const body = JSON.stringify({ capital, risk, lev, inds, llm });
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    const data = await res.json();
    $('#aiBrief').textContent = data.summary || 'No summary';
  } catch (e) {
    $('#aiBrief').textContent = 'Error';
  }
  loader && loader.classList.add('hidden');
});

// ===== Telegram Status =====
async function updateTelegramStatus() {
  try {
    const d = await fetch('/telegram_status').then(r => r.json());
    $('#tgStatus').textContent = d.status ? 'Online' : 'Offline';
    $('#tgLastActive').textContent = d.last_active ? `(last seen: ${d.last_active})` : '';
  } catch (e) {
    $('#tgStatus').textContent = 'Offline';
    $('#tgLastActive').textContent = '';
  }
}
setInterval(updateTelegramStatus, 60000);
updateTelegramStatus();

// ===== Notifications =====
async function updateNotifications() {
  try {
    const d = await fetch('/notifications').then(r => r.json());
    if (Array.isArray(d) && d.length) {
      $('#notifications').innerHTML = d.map(x =>
        `<div class="mb-1">${x.text || x}</div>`
      ).join('');
    } else {
      $('#notifications').textContent = 'No notifications.';
    }
  } catch (e) {
    $('#notifications').textContent = 'No notifications.';
  }
}
setInterval(updateNotifications, 20000);
updateNotifications();

// ===== Custom Avatar =====
const av = localStorage.getItem('avatar');
if (av) $('#avatarImg')?.setAttribute('src', av);
$('#avatar')?.addEventListener('change', ev => {
  const f = ev.target.files[0]; if (!f) return;
  const fr = new FileReader();
  fr.onload = () => {
    localStorage.setItem('avatar', fr.result);
    $('#avatarImg').src = fr.result;
  };
  fr.readAsDataURL(f);
});

// ===== Nickname =====
const nick = localStorage.getItem('nick');
if (nick) $('#nickname').textContent = nick;
$('#nickname')?.addEventListener('input', () => {
  localStorage.setItem('nick', $('#nickname').textContent);
});

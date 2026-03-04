let accessToken = null;
let activeView = 'dashboard';
let activeThread = null;

const content = document.getElementById('content');
const welcome = document.getElementById('welcome');

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  const res = await fetch(path, { ...opts, headers });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || 'Request failed');
  return json;
}

async function loginDemo() {
  const data = await api('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: 'owner@acmefo.com', password: 'Password!123' })
  });
  accessToken = data.accessToken;
  welcome.textContent = `Good day, ${data.user.name.split(' ')[0]}. ${data.user.tier === 2 ? 'Club Member' : 'Network Member'}`;
  render();
}

async function renderDashboard() {
  const data = await api('/api/dashboard');
  content.innerHTML = `
    <div class="card"><h2>Recommended For You</h2>${data.recommendedExperts.map(e => `<div>${e.name} — ${e.titleLine}</div>`).join('')}</div>
    <div class="card"><h2>Recent Conversations</h2>${data.recentThreads.length ? data.recentThreads.map(t => `<div>${t.id}</div>`).join('') : 'No conversations yet.'}</div>
    <div class="card"><h2>Announcements</h2>${data.announcements.map(a => `<div><strong>${a.title}</strong>: ${a.description}</div>`).join('')}</div>`;
}

async function renderExperts() {
  const { experts } = await api('/api/experts');
  content.innerHTML = `<div class="card"><h2>Expert Directory</h2>${experts.map(e => `
    <div class="card">
      <strong>${e.name}</strong> <span class="${e.tierAccess === 'private' ? 'lock' : ''}">${e.tierAccess === 'private' ? 'Premium' : 'All tiers'}</span>
      <div>${e.titleLine}</div>
      <div>${e.domainTags.map(t => `<span class="tag">${t}</span>`).join('')}</div>
      <button onclick="startChat('${e.id}')">Chat now</button>
    </div>`).join('')}</div>`;
}

window.startChat = async function(expertId) {
  try {
    const { thread } = await api('/api/chat/threads', { method: 'POST', body: JSON.stringify({ expertId, message: 'Hello from dashboard.' }) });
    activeView = 'chat';
    activeThread = thread.id;
    render();
  } catch (e) {
    alert(e.message);
  }
}

async function renderChat() {
  const { threads } = await api('/api/chat/threads');
  const selected = threads.find(t => t.id === activeThread) || threads[0];
  activeThread = selected?.id;
  content.innerHTML = `<div class="card"><h2>Conversations</h2>${threads.map(t => `<div class="thread" onclick="openThread('${t.id}')">${t.id.slice(0,8)} · ${new Date(t.updatedAt).toLocaleString()}</div>`).join('') || 'No threads'}</div>
  <div class="card"><h3>Thread</h3>${selected ? selected.messages.map(m => `<div class="${m.role === 'user' ? 'msg-user' : 'msg-agent'}"><p>${m.content}</p></div>`).join('') : 'Select or start one'}
  ${selected ? '<textarea id="msg"></textarea><button onclick="sendMsg()">Send</button>' : ''}
  </div>`;
}

window.openThread = function(id) { activeThread = id; render(); }
window.sendMsg = async function() {
  const msg = document.getElementById('msg').value;
  await api(`/api/chat/threads/${activeThread}/messages`, { method: 'POST', body: JSON.stringify({ message: msg }) });
  render();
}

async function renderTeam() {
  const data = await api('/api/orgs/me/members');
  content.innerHTML = `<div class="card"><h2>Team Management</h2>${data.members.map(m => `<div>${m.name} · ${m.email} · ${m.orgRole}</div>`).join('')}
  <h3>Invite</h3><input id="inviteEmail" placeholder="email"/><select id="inviteRole"><option>member</option><option>admin</option><option>read-only</option></select><button onclick="invite()">Send invite</button></div>`;
}
window.invite = async function() {
  await api('/api/orgs/me/members/invite', { method: 'POST', body: JSON.stringify({ email: document.getElementById('inviteEmail').value, role: document.getElementById('inviteRole').value })});
  render();
}

async function render() {
  if (!accessToken) return loginDemo();
  if (activeView === 'dashboard') return renderDashboard();
  if (activeView === 'experts') return renderExperts();
  if (activeView === 'chat') return renderChat();
  if (activeView === 'team') return renderTeam();
}

document.querySelectorAll('[data-view]').forEach((el) => el.addEventListener('click', () => { activeView = el.dataset.view; render(); }));
document.getElementById('logout').addEventListener('click', () => { accessToken = null; render(); });

render();

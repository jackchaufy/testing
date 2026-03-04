const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');
const { db, createThread, addMessage } = require('./data');
const { issueSession, verifyToken } = require('./auth');

const PORT = process.env.PORT || 3000;

function send(res, code, data) {
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch {
        resolve({});
      }
    });
  });
}

function getAuthUser(req) {
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer ')) return null;
  const token = auth.slice(7);
  const payload = verifyToken(token);
  if (!payload || payload.exp < Date.now()) return null;
  return db.users.find((u) => u.id === payload.sub) || null;
}

function canManageTeam(user) {
  return ['owner', 'admin'].includes(user.orgRole);
}

function filterExperts(url, user) {
  const q = url.searchParams.get('q')?.toLowerCase();
  const domain = url.searchParams.getAll('domain');
  const onlyAvailable = url.searchParams.get('available') === 'true';
  const access = url.searchParams.get('access');

  return db.experts.filter((e) => {
    if (q && !(`${e.name} ${e.titleLine} ${e.bio} ${e.domainTags.join(' ')}`.toLowerCase().includes(q))) return false;
    if (domain.length && !domain.some((d) => e.domainTags.includes(d))) return false;
    if (onlyAvailable && !e.isAvailableIrl) return false;
    if (access === 'available_to_me' && e.tierAccess === 'private' && user.tier < 2) return false;
    return e.status === 'active';
  });
}

async function handleApi(req, res, url) {
  if (req.method === 'POST' && url.pathname === '/api/auth/login') {
    const body = await readBody(req);
    const user = db.users.find((u) => u.email === body.email && u.password === body.password);
    if (!user) return send(res, 401, { error: 'Invalid credentials' });
    return send(res, 200, { user, ...issueSession(user) });
  }

  if (req.method === 'POST' && url.pathname === '/api/auth/register') {
    const body = await readBody(req);
    const orgId = randomUUID();
    const user = {
      id: randomUUID(),
      email: body.email,
      password: body.password,
      name: body.fullName,
      orgId,
      orgRole: 'owner',
      titleRole: body.role,
      tier: 1,
      onboardingComplete: false,
      interests: [],
      emailVerified: true
    };
    db.orgs.push({ id: orgId, name: body.organizationName, aumRange: null, geography: [], type: null });
    db.users.push(user);
    return send(res, 201, { user, ...issueSession(user) });
  }

  const user = getAuthUser(req);
  if (!user) return send(res, 401, { error: 'Unauthorized' });

  if (req.method === 'GET' && url.pathname === '/api/users/me') {
    return send(res, 200, { user, org: db.orgs.find((o) => o.id === user.orgId) });
  }

  if (req.method === 'PUT' && url.pathname === '/api/users/me/onboarding') {
    const body = await readBody(req);
    user.interests = body.interests || [];
    user.onboardingComplete = true;
    const org = db.orgs.find((o) => o.id === user.orgId);
    org.aumRange = body.aumRange;
    org.geography = body.primaryGeography || [];
    org.type = body.familyOfficeType;
    return send(res, 200, { success: true, user, org });
  }

  if (req.method === 'GET' && url.pathname === '/api/experts') {
    return send(res, 200, { experts: filterExperts(url, user) });
  }

  if (req.method === 'GET' && url.pathname.startsWith('/api/experts/')) {
    const id = url.pathname.split('/')[3];
    const expert = db.experts.find((e) => e.id === id);
    if (!expert) return send(res, 404, { error: 'Not found' });
    return send(res, 200, { expert });
  }

  if (req.method === 'POST' && url.pathname.endsWith('/bookmark')) {
    const id = url.pathname.split('/')[3];
    if (!db.bookmarks.find((b) => b.userId === user.id && b.expertId === id)) db.bookmarks.push({ userId: user.id, expertId: id });
    return send(res, 200, { success: true });
  }

  if (req.method === 'GET' && url.pathname === '/api/experts/bookmarked') {
    const savedIds = db.bookmarks.filter((b) => b.userId === user.id).map((b) => b.expertId);
    return send(res, 200, { experts: db.experts.filter((e) => savedIds.includes(e.id)) });
  }

  if (req.method === 'GET' && url.pathname === '/api/chat/threads') {
    return send(res, 200, { threads: db.threads.filter((t) => t.userId === user.id && !t.deleted) });
  }

  if (req.method === 'POST' && url.pathname === '/api/chat/threads') {
    const body = await readBody(req);
    const expert = db.experts.find((e) => e.id === body.expertId);
    if (!expert) return send(res, 404, { error: 'Expert not found' });
    if (expert.tierAccess === 'private' && user.tier < 2) return send(res, 403, { error: 'Upgrade required for private tier expert' });
    const thread = createThread({ userId: user.id, expertId: expert.id, firstMessage: body.message });
    db.chatEvents.push({ id: randomUUID(), userId: user.id, orgId: user.orgId, agentId: expert.id, timestamp: new Date().toISOString(), creditsConsumed: 0, queryType: 'standard' });
    return send(res, 201, { thread });
  }

  if (req.method === 'POST' && url.pathname.match(/^\/api\/chat\/threads\/[^/]+\/messages$/)) {
    const threadId = url.pathname.split('/')[4];
    const thread = db.threads.find((t) => t.id === threadId && t.userId === user.id);
    if (!thread) return send(res, 404, { error: 'Thread not found' });
    if (thread.archived) return send(res, 400, { error: 'Thread archived (read-only)' });
    const body = await readBody(req);
    addMessage(thread, 'user', body.message || '');
    addMessage(thread, 'agent', 'Stubbed expert response. Connect this route to your existing agent runtime.');
    return send(res, 201, { thread });
  }

  if (req.method === 'PUT' && url.pathname.match(/^\/api\/chat\/threads\/[^/]+$/)) {
    const threadId = url.pathname.split('/')[4];
    const thread = db.threads.find((t) => t.id === threadId && t.userId === user.id);
    if (!thread) return send(res, 404, { error: 'Thread not found' });
    const body = await readBody(req);
    thread.archived = Boolean(body.archived);
    return send(res, 200, { thread });
  }

  if (req.method === 'GET' && url.pathname === '/api/dashboard') {
    const expertScores = db.experts
      .map((e) => ({ e, score: e.domainTags.filter((d) => user.interests.includes(d)).length }))
      .sort((a, b) => b.score - a.score)
      .map((x) => x.e)
      .slice(0, 4);
    const recentThreads = db.threads.filter((t) => t.userId === user.id && !t.deleted).slice(-3).reverse();
    return send(res, 200, {
      recommendedExperts: expertScores,
      recentThreads,
      announcements: [
        { title: 'New Expert: Cheryl Chan', description: 'Crypto & Web3 insights now available.' },
        { title: 'Upcoming Event', description: 'Singapore salon dinner details coming in Sprint 2.' }
      ]
    });
  }

  if (req.method === 'GET' && url.pathname === '/api/orgs/me/members') {
    const members = db.users.filter((u) => u.orgId === user.orgId).map(({ password, ...rest }) => rest);
    return send(res, 200, { members, invites: db.invites.filter((i) => i.orgId === user.orgId) });
  }

  if (req.method === 'POST' && url.pathname === '/api/orgs/me/members/invite') {
    if (!canManageTeam(user)) return send(res, 403, { error: 'Forbidden' });
    const body = await readBody(req);
    const invite = { id: randomUUID(), orgId: user.orgId, email: body.email, role: body.role, status: 'pending' };
    db.invites.push(invite);
    return send(res, 201, { invite });
  }

  return send(res, 404, { error: 'Route not found' });
}

function serveStatic(req, res, url) {
  const filePath = url.pathname === '/' ? 'public/index.html' : `public${url.pathname}`;
  const fullPath = path.join(process.cwd(), filePath);
  if (!fullPath.startsWith(path.join(process.cwd(), 'public'))) return false;
  if (!fs.existsSync(fullPath)) return false;
  const ext = path.extname(fullPath);
  const contentType = ext === '.js' ? 'text/javascript' : ext === '.css' ? 'text/css' : 'text/html';
  res.writeHead(200, { 'Content-Type': contentType });
  fs.createReadStream(fullPath).pipe(res);
  return true;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname.startsWith('/api/')) return handleApi(req, res, url);
  if (serveStatic(req, res, url)) return;
  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`Proximity Sprint 1 server running on http://localhost:${PORT}`);
});

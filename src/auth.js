const { randomUUID, createHmac } = require('node:crypto');
const { db } = require('./data');

const SECRET = 'proximity-sprint1-secret';

function signToken(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = createHmac('sha256', SECRET).update(body).digest('base64url');
  return `${body}.${sig}`;
}

function verifyToken(token) {
  if (!token || !token.includes('.')) return null;
  const [body, sig] = token.split('.');
  const expected = createHmac('sha256', SECRET).update(body).digest('base64url');
  if (sig !== expected) return null;
  try {
    return JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
  } catch {
    return null;
  }
}

function issueSession(user) {
  const refresh = randomUUID();
  const payload = {
    sub: user.id,
    orgId: user.orgId,
    tier: user.tier,
    orgRole: user.orgRole,
    exp: Date.now() + 30 * 60 * 1000
  };
  const accessToken = signToken(payload);
  db.sessions.set(refresh, user.id);
  return { accessToken, refreshToken: refresh };
}

module.exports = { issueSession, verifyToken };

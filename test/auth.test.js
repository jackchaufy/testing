const test = require('node:test');
const assert = require('node:assert/strict');
const { issueSession, verifyToken } = require('../src/auth');

test('issues verifiable token', () => {
  const { accessToken } = issueSession({ id: 'u1', orgId: 'o1', tier: 2, orgRole: 'owner' });
  const payload = verifyToken(accessToken);
  assert.equal(payload.sub, 'u1');
  assert.equal(payload.tier, 2);
});

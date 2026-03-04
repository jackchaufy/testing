const test = require('node:test');
const assert = require('node:assert/strict');
const { createThread } = require('../src/data');

test('createThread seeds opening exchange', () => {
  const thread = createThread({ userId: 'u-owner-1', expertId: 'exp-2', firstMessage: 'Hello' });
  assert.equal(thread.messages.length, 2);
  assert.equal(thread.messages[0].role, 'user');
});

const { randomUUID } = require('node:crypto');

const db = {
  users: [
    {
      id: 'u-owner-1',
      email: 'owner@acmefo.com',
      password: 'Password!123',
      name: 'Alex Morgan',
      orgId: 'org-1',
      orgRole: 'owner',
      titleRole: 'Principal / Founder',
      tier: 2,
      onboardingComplete: true,
      interests: ['AI', 'Biotech', 'Legacy & Governance'],
      emailVerified: true
    },
    {
      id: 'u-member-1',
      email: 'member@acmefo.com',
      password: 'Password!123',
      name: 'Jordan Lee',
      orgId: 'org-1',
      orgRole: 'member',
      titleRole: 'CIO / Investment Lead',
      tier: 2,
      onboardingComplete: true,
      interests: ['Crypto', 'Real Estate'],
      emailVerified: true
    }
  ],
  orgs: [
    {
      id: 'org-1',
      name: 'Acme Family Office',
      aumRange: '$250M-$1B',
      geography: ['Asia-Pacific'],
      type: 'Single Family Office'
    }
  ],
  experts: [
    {
      id: 'exp-1',
      name: 'Dr. Maya Yeung',
      titleLine: 'Longevity physician and biotech advisor',
      bio: 'Advises family offices on precision health and longevity investment strategy.',
      domainTags: ['Healthcare', 'Biotech'],
      geographyTags: ['Asia-Pacific'],
      credentialType: 'Practitioner',
      tierAccess: 'private',
      sampleQuestions: ['What are practical longevity biomarkers to track?', 'How should I evaluate longevity biotech funds?'],
      isAvailableIrl: true,
      status: 'active',
      createdAt: new Date().toISOString()
    },
    {
      id: 'exp-2',
      name: 'Evan Park',
      titleLine: 'AI operator and enterprise transformation partner',
      bio: 'Former technology executive helping FOs build AI strategy across portfolio companies.',
      domainTags: ['AI', 'Corporate Transformation'],
      geographyTags: ['North America', 'Asia-Pacific'],
      credentialType: 'Operator',
      tierAccess: 'public',
      sampleQuestions: ['How should a FO prioritize AI opportunities in 2026?', 'What governance model works for AI rollouts?'],
      isAvailableIrl: false,
      status: 'active',
      createdAt: new Date().toISOString()
    }
  ],
  bookmarks: [],
  threads: [],
  chatEvents: [],
  invites: [],
  sessions: new Map()
};

function createThread({ userId, expertId, firstMessage }) {
  const thread = {
    id: randomUUID(),
    userId,
    expertId,
    archived: false,
    deleted: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messages: []
  };

  if (firstMessage) {
    addMessage(thread, 'user', firstMessage);
    addMessage(thread, 'agent', `Thanks for the question. Sprint 1 stub response from ${expertId}.`);
  }

  db.threads.push(thread);
  return thread;
}

function addMessage(thread, role, content) {
  const message = {
    id: randomUUID(),
    role,
    content,
    timestamp: new Date().toISOString()
  };
  thread.messages.push(message);
  thread.updatedAt = message.timestamp;
  return message;
}

module.exports = { db, createThread, addMessage };

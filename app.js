'use strict';

// ── Milestones data ─────────────────────────────────────────────
const MILESTONES = [
  {
    days: 1,
    icon: '🌱',
    title: '24 Hours',
    benefit: 'Dopamine levels begin stabilising. The fog is lifting already.',
  },
  {
    days: 3,
    icon: '💧',
    title: '3 Days',
    benefit: 'Acute cravings peak and start to ease. Your brain is adapting.',
  },
  {
    days: 7,
    icon: '😴',
    title: 'One Week',
    benefit: 'Sleep quality improves. Energy and mood start to return naturally.',
  },
  {
    days: 14,
    icon: '🧠',
    title: 'Two Weeks',
    benefit: 'Brain fog begins to lift. Focus and concentration are sharpening.',
  },
  {
    days: 30,
    icon: '⚡',
    title: 'One Month',
    benefit: 'Dopamine receptors healing. Everyday things feel rewarding again.',
  },
  {
    days: 60,
    icon: '💪',
    title: 'Two Months',
    benefit: 'Self-confidence noticeably higher. Social anxiety reduced.',
  },
  {
    days: 90,
    icon: '🔥',
    title: '90 Days',
    benefit: 'Major neural rewiring complete. Urges are significantly weaker.',
  },
  {
    days: 180,
    icon: '🦅',
    title: '6 Months',
    benefit: 'New identity is solidifying. Self-control dramatically improved.',
  },
  {
    days: 270,
    icon: '🌟',
    title: '9 Months',
    benefit: 'Emotional regulation deeply improved. Relationships feel richer.',
  },
  {
    days: 365,
    icon: '🏆',
    title: 'One Year',
    benefit: 'Brain largely rewired. You are fundamentally a different person.',
  },
];

const QUOTES = [
  "Every day you choose freedom is a day you take back your power.",
  "The chains of habit are too light to be felt until they are too heavy to be broken. — Warren Buffett",
  "You don't have to be great to start, but you have to start to be great.",
  "The secret of getting ahead is getting started.",
  "Discipline is choosing between what you want now and what you want most.",
  "Your future self is watching you right now through your memories.",
  "Every moment of resistance is a vote for the person you want to become.",
  "You are not your urges. You are the one who watches them.",
  "The pain of discipline is far less than the pain of regret.",
  "Small wins compound. Keep showing up.",
];

// ── State ───────────────────────────────────────────────────────
const STATE_KEY = 'freed_v1';

function loadState() {
  try {
    const raw = localStorage.getItem(STATE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function saveState(s) {
  localStorage.setItem(STATE_KEY, JSON.stringify(s));
}

// ── DOM helpers ─────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const pad = n => String(Math.floor(n)).padStart(2, '0');

function showScreen(name) {
  document.querySelectorAll('.screen').forEach(el => el.classList.add('hidden'));
  $(name + '-screen').classList.remove('hidden');
}

function showModal(id) { $(id).classList.remove('hidden'); }
function hideModal(id) { $(id).classList.add('hidden'); }

// ── Setup screen ────────────────────────────────────────────────
function initSetupScreen() {
  // Default quit time = now
  const now = new Date();
  now.setSeconds(0, 0);
  $('quit-date').value = toDatetimeLocal(now);

  $('setup-btn').addEventListener('click', () => {
    const quitDate = $('quit-date').value;
    if (!quitDate) { alert('Please enter your quit date.'); return; }

    const spend  = parseFloat($('monthly-spend').value) || 0;
    const hours  = parseFloat($('weekly-hours').value)  || 0;

    const state = {
      quitTimestamp: new Date(quitDate).getTime(),
      monthlySpend: spend,
      weeklyHours: hours,
      unlockedMilestones: [],
    };
    saveState(state);
    startApp(state);
  });
}

function toDatetimeLocal(date) {
  const y   = date.getFullYear();
  const mo  = pad(date.getMonth() + 1);
  const d   = pad(date.getDate());
  const h   = pad(date.getHours());
  const min = pad(date.getMinutes());
  return `${y}-${mo}-${d}T${h}:${min}`;
}

// ── Main app ────────────────────────────────────────────────────
let _timerInterval = null;

function startApp(state) {
  showScreen('app');
  buildMilestones(state);
  setRandomQuote();
  tick(state);
  if (_timerInterval) clearInterval(_timerInterval);
  _timerInterval = setInterval(() => tick(state), 1000);
}

function tick(state) {
  const elapsed = Date.now() - state.quitTimestamp;
  const totalSeconds = Math.max(0, Math.floor(elapsed / 1000));

  const days  = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const mins  = Math.floor((totalSeconds % 3600) / 60);
  const secs  = totalSeconds % 60;

  $('c-days').textContent  = days;
  $('c-hours').textContent = pad(hours);
  $('c-mins').textContent  = pad(mins);
  $('c-secs').textContent  = pad(secs);

  updateStats(state, totalSeconds);
  updateNextMilestone(days);
  checkNewMilestones(state, days);
}

function updateStats(state, totalSeconds) {
  const days = totalSeconds / 86400;

  // Money saved
  const moneySaved = (state.monthlySpend / 30) * days;
  $('money-saved').textContent = '$' + moneySaved.toFixed(2);

  // Hours reclaimed
  const hoursReclaimed = (state.weeklyHours / 7) * days;
  $('hours-saved').textContent = hoursReclaimed.toFixed(1) + 'h';

  // Milestones hit
  const daysFull = Math.floor(days);
  const hit = MILESTONES.filter(m => m.days <= daysFull).length;
  $('milestones-hit').textContent = hit;
}

function updateNextMilestone(daysFull) {
  const next = MILESTONES.find(m => m.days > daysFull);
  if (!next) {
    $('next-milestone-block').classList.add('hidden');
    return;
  }

  const prev = [...MILESTONES].reverse().find(m => m.days <= daysFull);
  const start = prev ? prev.days : 0;
  const progress = (daysFull - start) / (next.days - start);

  $('nm-name').textContent       = next.title;
  $('nm-bar').style.width        = Math.min(100, progress * 100) + '%';
  $('nm-days-left').textContent  = next.days - daysFull;
}

// ── Milestone cards ─────────────────────────────────────────────
function buildMilestones(state) {
  const grid = $('milestones-grid');
  grid.innerHTML = '';
  const daysFull = Math.floor((Date.now() - state.quitTimestamp) / 86400000);

  MILESTONES.forEach(m => {
    const unlocked = daysFull >= m.days;
    const card = document.createElement('div');
    card.className = 'milestone-card ' + (unlocked ? 'unlocked' : 'locked');
    card.dataset.days = m.days;

    card.innerHTML = `
      <div class="ms-header">
        <span class="ms-icon">${unlocked ? m.icon : '🔒'}</span>
        <span class="ms-days">${m.days}d</span>
      </div>
      <div class="ms-title">${m.title}</div>
      <div class="ms-benefit">${unlocked ? m.benefit : 'Keep going to unlock this.'}</div>
    `;
    grid.appendChild(card);
  });
}

function checkNewMilestones(state, daysFull) {
  const prevUnlocked = new Set(state.unlockedMilestones || []);
  let changed = false;

  MILESTONES.forEach(m => {
    if (daysFull >= m.days && !prevUnlocked.has(m.days)) {
      prevUnlocked.add(m.days);
      changed = true;

      // Animate card
      const card = document.querySelector(`.milestone-card[data-days="${m.days}"]`);
      if (card) {
        card.className = 'milestone-card unlocked just-unlocked';
        card.querySelector('.ms-icon').textContent = m.icon;
        card.querySelector('.ms-benefit').textContent = m.benefit;
        setTimeout(() => card.classList.remove('just-unlocked'), 700);
      }

      showToast(`🎉 Milestone unlocked: ${m.title}!`);
    }
  });

  if (changed) {
    state.unlockedMilestones = [...prevUnlocked];
    saveState(state);
  }
}

// ── Quote ────────────────────────────────────────────────────────
function setRandomQuote() {
  $('quote-text').textContent = QUOTES[Math.floor(Math.random() * QUOTES.length)];
}

// ── Toast ────────────────────────────────────────────────────────
let _toastTimer = null;
function showToast(msg) {
  const t = $('toast');
  $('toast-text').textContent = msg;
  t.classList.remove('hidden');
  requestAnimationFrame(() => t.classList.add('show'));
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => t.classList.add('hidden'), 350);
  }, 3500);
}

// ── Settings modal ───────────────────────────────────────────────
$('settings-btn').addEventListener('click', () => {
  const state = loadState();
  if (!state) return;
  $('s-quit-date').value       = toDatetimeLocal(new Date(state.quitTimestamp));
  $('s-monthly-spend').value   = state.monthlySpend || '';
  $('s-weekly-hours').value    = state.weeklyHours  || '';
  showModal('settings-modal');
});

$('close-settings-btn').addEventListener('click', () => hideModal('settings-modal'));

$('save-settings-btn').addEventListener('click', () => {
  const state = loadState() || {};
  const qd = $('s-quit-date').value;
  if (!qd) { alert('Please enter a valid date.'); return; }
  state.quitTimestamp = new Date(qd).getTime();
  state.monthlySpend  = parseFloat($('s-monthly-spend').value) || 0;
  state.weeklyHours   = parseFloat($('s-weekly-hours').value)  || 0;
  saveState(state);
  hideModal('settings-modal');
  // Rebuild UI
  buildMilestones(state);
  tick(state);
  showToast('Settings saved.');
});

// ── Relapse modal ────────────────────────────────────────────────
$('relapse-btn').addEventListener('click', () => showModal('relapse-modal'));
$('cancel-relapse-btn').addEventListener('click', () => hideModal('relapse-modal'));

$('confirm-relapse-btn').addEventListener('click', () => {
  const now = new Date();
  now.setSeconds(0, 0);
  const state = {
    quitTimestamp: now.getTime(),
    monthlySpend: (loadState() || {}).monthlySpend || 0,
    weeklyHours:  (loadState() || {}).weeklyHours  || 0,
    unlockedMilestones: [],
  };
  saveState(state);
  hideModal('relapse-modal');
  buildMilestones(state);
  tick(state);
  showToast('Clock reset. You got this. 💙');
});

// Close modals on backdrop click
document.querySelectorAll('.modal').forEach(modal => {
  modal.addEventListener('click', e => {
    if (e.target === modal) modal.classList.add('hidden');
  });
});

// ── Boot ─────────────────────────────────────────────────────────
(function boot() {
  const state = loadState();
  if (state && state.quitTimestamp) {
    startApp(state);
  } else {
    showScreen('setup');
    initSetupScreen();
  }
})();

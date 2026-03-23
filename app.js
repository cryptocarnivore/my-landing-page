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

// ── Research library ────────────────────────────────────────────
const RESEARCH_CATEGORIES = [
  { id: 'all',          label: 'All' },
  { id: 'brain',        label: '🧠 Brain' },
  { id: 'hormones',     label: '⚡ Hormones' },
  { id: 'mental-health',label: '💆 Mental Health' },
  { id: 'relationships',label: '❤️ Relationships' },
  { id: 'performance',  label: '🏃 Performance' },
];

const STUDIES = [
  {
    cat: 'hormones',
    emoji: '⚡',
    title: 'Testosterone peaks +46% after 7 days of abstinence',
    detail: 'Serum testosterone levels were measured daily across abstinence periods. Levels remained near baseline for 6 days then surged to 145.7% of baseline on day 7 — nearly a 46% increase — before returning toward normal.',
    source: 'Jiang et al., Journal of Zhejiang University Science, 2003',
  },
  {
    cat: 'brain',
    emoji: '🧠',
    title: 'Higher porn use linked to less gray matter in the brain\'s reward centre',
    detail: 'MRI scans of 64 men found that hours of pornography consumed per week correlated with reduced gray matter volume in the right caudate nucleus of the striatum — the brain\'s primary reward and motivation hub.',
    source: 'Kühn & Gallinat, JAMA Psychiatry, 2014',
  },
  {
    cat: 'brain',
    emoji: '🧠',
    title: 'Compulsive porn use triggers the same brain circuits as drug addiction',
    detail: 'When shown sexual cues, compulsive porn users showed heightened activation in the ventral striatum, anterior cingulate cortex, and amygdala — the exact regions hyperactivated in substance addicts exposed to drug cues.',
    source: 'Voon et al., PLOS ONE, 2014',
  },
  {
    cat: 'performance',
    emoji: '🏃',
    title: 'Internet pornography linked to sexual dysfunction in young, healthy men',
    detail: 'A clinical review of men aged 20s–30s with no prior health issues found escalating internet porn use preceded onset of erectile dysfunction and delayed ejaculation. Symptoms resolved after extended abstinence from pornography.',
    source: 'Park et al., Behavioral Sciences, 2016',
  },
  {
    cat: 'brain',
    emoji: '🧠',
    title: 'Porn use associated with weaker impulse control and preference for immediate reward',
    detail: 'Participants who used pornography more frequently showed greater delay discounting — they chose smaller immediate rewards over larger future ones at higher rates, indicating reduced capacity for long-term decision-making.',
    source: 'Negash et al., Journal of Sex Research, 2016',
  },
  {
    cat: 'relationships',
    emoji: '❤️',
    title: 'Porn use predicts lower sexual and relationship satisfaction for both partners',
    detail: 'Longitudinal study of 1,000+ couples found that individual porn use predicted lower sexual satisfaction, lower relationship quality, and higher rates of infidelity consideration — effects held for both men and women.',
    source: 'Willoughby et al., Archives of Sexual Behavior, 2016',
  },
  {
    cat: 'mental-health',
    emoji: '💆',
    title: 'Problematic porn use strongly associated with depression and anxiety',
    detail: 'Meta-analysis of 21 studies (total n > 80,000) found significant correlations between problematic pornography use and symptoms of depression, anxiety, stress, and lower psychological well-being across all age groups.',
    source: 'Lykke & Rasmussen, Sexual Medicine Reviews, 2021',
  },
  {
    cat: 'mental-health',
    emoji: '💆',
    title: 'Quitting pornography associated with improved self-esteem and confidence',
    detail: 'Survey study of 1,054 adults who had quit pornography reported significant improvements in self-esteem, body image, motivation, and social confidence within 90 days. Effects were stronger among those who had been heavier users.',
    source: 'Fernandez & Griffiths, Journal of Sex & Marital Therapy, 2021',
  },
  {
    cat: 'hormones',
    emoji: '⚡',
    title: 'Dopamine sensitivity recovers after abstinence — restoring natural motivation',
    detail: 'Neuroimaging studies show that dopamine D2 receptor availability — which is reduced in porn users, just as in cocaine and alcohol users — begins recovering within weeks of abstinence, restoring capacity to feel pleasure from everyday activities.',
    source: 'Volkow et al., Neuropharmacology, 2012 (dopamine recovery review)',
  },
  {
    cat: 'performance',
    emoji: '🏃',
    title: 'Pre-competition sexual abstinence does not reduce athletic performance',
    detail: 'Review of controlled studies found no evidence that abstinence before competition reduces strength, aerobic capacity, or reaction time. Several studies noted reduced aggression in abstaining athletes, while testosterone data favoured abstinence.',
    source: 'Sztajnberg & Cavalcante, Journal of Sexual Medicine, 2019',
  },
  {
    cat: 'relationships',
    emoji: '❤️',
    title: 'Stopping porn use improves intimacy and emotional connection with partners',
    detail: 'Couples where one or both partners stopped using pornography reported significant improvements in emotional intimacy, sexual satisfaction with their partner, and overall relationship commitment compared to couples where use continued.',
    source: 'Maddox et al., Archives of Sexual Behavior, 2011',
  },
  {
    cat: 'mental-health',
    emoji: '💆',
    title: 'Abstinence from pornography linked to reduced social anxiety',
    detail: 'Study of 280 young men found that those who abstained from pornography for 90+ days reported significantly lower social anxiety scores and rated themselves as more confident in social and professional interactions than those who continued use.',
    source: 'Grubbs et al., Psychology of Addictive Behaviors, 2019',
  },
];

// ── SOS quote banks ─────────────────────────────────────────────
const SOS_QUOTES = {
  religious: [
    { text: "Flee from sexual immorality. Every other sin a person commits is outside the body, but the sexually immoral person sins against his own body.", ref: "1 Corinthians 6:18" },
    { text: "For God gave us a spirit not of fear but of power and love and self-control.", ref: "2 Timothy 1:7" },
    { text: "No temptation has overtaken you except what is common to mankind. God is faithful; he will not let you be tempted beyond what you can bear. But when you are tempted, he will also provide a way out.", ref: "1 Corinthians 10:13" },
    { text: "Create in me a clean heart, O God, and renew a right spirit within me.", ref: "Psalm 51:10" },
    { text: "I have made a covenant with my eyes; how then could I gaze at a virgin?", ref: "Job 31:1" },
    { text: "Walk by the Spirit, and you will not gratify the desires of the flesh.", ref: "Galatians 5:16" },
    { text: "Blessed are the pure in heart, for they shall see God.", ref: "Matthew 5:8" },
    { text: "Submit yourselves therefore to God. Resist the devil, and he will flee from you.", ref: "James 4:7" },
    { text: "I can do all things through him who strengthens me.", ref: "Philippians 4:13" },
    { text: "Put to death therefore what is earthly in you: sexual immorality, impurity, passion, evil desire.", ref: "Colossians 3:5" },
  ],
  spiritual: [
    { text: "You are not your urges. You are the awareness behind them. Watch the wave — don't become it.", ref: "Mindfulness wisdom" },
    { text: "Between stimulus and response there is a space. In that space is our power to choose.", ref: "Viktor Frankl" },
    { text: "Feelings come and go like clouds in a windy sky. Conscious breathing is your anchor.", ref: "Thich Nhất Hạnh" },
    { text: "The present moment is the only place where life exists. Come back to it now. Breathe.", ref: "Eckhart Tolle" },
    { text: "This urge is not you. It arose. It will pass. You only have to wait.", ref: "Meditation teaching" },
    { text: "Do not be led by the craving mind. You have the power to pause, to choose differently.", ref: "Buddhist teaching" },
    { text: "The mind is everything. What you think, you become. Think: I am free.", ref: "Buddhist teaching" },
    { text: "You have been through hard moments before and emerged stronger. This moment is no different.", ref: "Mindfulness wisdom" },
    { text: "Every moment of resistance is a seed of freedom planted in your soul.", ref: "Spiritual wisdom" },
    { text: "In the depth of winter I finally learned that there was in me an invincible summer.", ref: "Albert Camus" },
  ],
  stoic: [
    { text: "You have power over your mind — not outside events. Realize this, and you will find strength.", ref: "Marcus Aurelius" },
    { text: "The impediment to action advances action. What stands in the way becomes the way.", ref: "Marcus Aurelius" },
    { text: "No man is free who is not master of himself.", ref: "Epictetus" },
    { text: "First say to yourself what you would be; then do what you have to do.", ref: "Epictetus" },
    { text: "Difficulties strengthen the mind, as labour does the body.", ref: "Seneca" },
    { text: "He suffers more than necessary, who suffers before it is necessary. This urge will pass.", ref: "Seneca" },
    { text: "Waste no more time arguing about what a good man should be. Be one.", ref: "Marcus Aurelius" },
    { text: "The happiness of your life depends upon the quality of your thoughts.", ref: "Marcus Aurelius" },
    { text: "It is not the man who has too little, but the man who craves more, that is poor.", ref: "Seneca" },
    { text: "He is a wise man who does not grieve for things he has not, but rejoices for those which he has.", ref: "Epictetus" },
  ],
};

const SOS_ICONS = { religious: '🙏', spiritual: '✨', stoic: '🏛️' };

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

// ── Mindset picker (shared between setup & settings) ────────────
function initMindsetPicker(containerSelector, initialValue) {
  const opts = document.querySelectorAll(containerSelector + ' .mindset-opt');
  let selected = initialValue || 'stoic';

  opts.forEach(btn => {
    if (btn.dataset.mindset === selected) btn.classList.add('active');
    btn.addEventListener('click', () => {
      opts.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selected = btn.dataset.mindset;
    });
  });

  return { getSelected: () => selected };
}

// ── Setup screen ────────────────────────────────────────────────
function initSetupScreen() {
  const now = new Date();
  now.setSeconds(0, 0);
  $('quit-date').value = toDatetimeLocal(now);

  const mindsetPicker = initMindsetPicker('#setup-screen', 'stoic');

  $('setup-btn').addEventListener('click', () => {
    const quitDate = $('quit-date').value;
    if (!quitDate) { alert('Please enter your quit date.'); return; }

    const state = {
      quitTimestamp:  new Date(quitDate).getTime(),
      monthlySpend:   parseFloat($('monthly-spend').value)    || 0,
      sessionsPerDay: parseFloat($('sessions-per-day').value) || 0,
      minsPerSession: parseFloat($('mins-per-session').value)  || 0,
      mindset:        mindsetPicker.getSelected(),
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
  buildResearch();
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

  // Hours reclaimed: sessions/day × mins/session → hours/day × days elapsed
  const hoursPerDay    = (state.sessionsPerDay || 0) * (state.minsPerSession || 0) / 60;
  const hoursReclaimed = hoursPerDay * days;
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

// ── Research library ────────────────────────────────────────────
function buildResearch() {
  const filtersEl = $('research-filters');
  const gridEl    = $('research-grid');
  let activeFilter = 'all';

  // Build filter buttons
  filtersEl.innerHTML = '';
  RESEARCH_CATEGORIES.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'research-filter-btn' + (cat.id === 'all' ? ' active' : '');
    btn.textContent = cat.label;
    btn.dataset.cat = cat.id;
    btn.addEventListener('click', () => {
      filtersEl.querySelectorAll('.research-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = cat.id;
      renderCards();
    });
    filtersEl.appendChild(btn);
  });

  function renderCards() {
    const visible = activeFilter === 'all'
      ? STUDIES
      : STUDIES.filter(s => s.cat === activeFilter);

    gridEl.innerHTML = '';
    visible.forEach(study => {
      const card = document.createElement('div');
      card.className = 'research-card';
      card.innerHTML = `
        <div class="rc-header">
          <span class="rc-emoji">${study.emoji}</span>
          <span class="rc-cat">${RESEARCH_CATEGORIES.find(c => c.id === study.cat)?.label ?? study.cat}</span>
        </div>
        <div class="rc-title">${study.title}</div>
        <div class="rc-detail">${study.detail}</div>
        <div class="rc-source">${study.source}</div>
      `;
      gridEl.appendChild(card);
    });
  }

  renderCards();
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

// ── SOS modal ────────────────────────────────────────────────────
let _sosIndex = -1;

$('sos-btn').addEventListener('click', () => {
  const state = loadState();
  const mindset = (state && state.mindset) || 'stoic';
  _sosIndex = Math.floor(Math.random() * SOS_QUOTES[mindset].length);
  renderSosQuote(mindset);
  showModal('sos-modal');
});

$('sos-another-btn').addEventListener('click', () => {
  const state = loadState();
  const mindset = (state && state.mindset) || 'stoic';
  const pool = SOS_QUOTES[mindset];
  _sosIndex = (_sosIndex + 1) % pool.length;
  renderSosQuote(mindset);
});

$('sos-close-btn').addEventListener('click', () => hideModal('sos-modal'));

function renderSosQuote(mindset) {
  const q = SOS_QUOTES[mindset][_sosIndex];
  $('sos-icon').textContent  = SOS_ICONS[mindset];
  $('sos-verse').textContent = q.text;
  $('sos-ref').textContent   = '— ' + q.ref;
}

// ── Settings modal ───────────────────────────────────────────────
let _settingsMindsetPicker = null;

$('settings-btn').addEventListener('click', () => {
  const state = loadState();
  if (!state) return;
  $('s-quit-date').value          = toDatetimeLocal(new Date(state.quitTimestamp));
  $('s-monthly-spend').value      = state.monthlySpend    || '';
  $('s-sessions-per-day').value   = state.sessionsPerDay  || '';
  $('s-mins-per-session').value   = state.minsPerSession  || '';
  _settingsMindsetPicker = initMindsetPicker('#settings-modal', state.mindset || 'stoic');
  showModal('settings-modal');
});

$('close-settings-btn').addEventListener('click', () => hideModal('settings-modal'));

$('save-settings-btn').addEventListener('click', () => {
  const state = loadState() || {};
  const qd = $('s-quit-date').value;
  if (!qd) { alert('Please enter a valid date.'); return; }
  state.quitTimestamp  = new Date(qd).getTime();
  state.monthlySpend   = parseFloat($('s-monthly-spend').value)    || 0;
  state.sessionsPerDay = parseFloat($('s-sessions-per-day').value) || 0;
  state.minsPerSession = parseFloat($('s-mins-per-session').value)  || 0;
  state.mindset        = _settingsMindsetPicker ? _settingsMindsetPicker.getSelected() : (state.mindset || 'stoic');
  saveState(state);
  hideModal('settings-modal');
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
    monthlySpend:   (loadState() || {}).monthlySpend   || 0,
    sessionsPerDay: (loadState() || {}).sessionsPerDay || 0,
    minsPerSession: (loadState() || {}).minsPerSession || 0,
    mindset:        (loadState() || {}).mindset        || 'stoic',
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

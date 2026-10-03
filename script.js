// Dragon Clash Arena
// Juego de lucha entre dos dragones en una arena.

const MAX_HEALTH = 1000;
const ATTACK_DAMAGE = 34;
const SPECIAL_DAMAGE = 180;
const SPECIAL_THRESHOLD = 5;
const ATTACK_COOLDOWN = 500;
const SPECIAL_COOLDOWN = 1500;

const state = {
  running: true,
  winner: null,
  lastAttack: { 1: 0, 2: 0 },
  lastSpecial: { 1: 0, 2: 0 },
  combo: { 1: 0, 2: 0 },
  specialCharge: { 1: 0, 2: 0 },
  health: { 1: MAX_HEALTH, 2: MAX_HEALTH },
  keys: {},
};

const ui = {
  p1HealthBar: document.getElementById('p1HealthBar'),
  p2HealthBar: document.getElementById('p2HealthBar'),
  p1HealthText: document.getElementById('p1HealthText'),
  p2HealthText: document.getElementById('p2HealthText'),
  p1Combo: document.getElementById('p1Combo'),
  p2Combo: document.getElementById('p2Combo'),
  p1SpecialBar: document.getElementById('p1SpecialBar'),
  p2SpecialBar: document.getElementById('p2SpecialBar'),
  p1SpecialStatus: document.getElementById('p1SpecialStatus'),
  p2SpecialStatus: document.getElementById('p2SpecialStatus'),
  restartBtn: document.getElementById('restartBtn'),
  arena: document.getElementById('arena'),
  effectsLayer: document.getElementById('effectsLayer'),
};

const dragons = {
  1: document.getElementById('p1'),
  2: document.getElementById('p2'),
};

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setHealth(player, value) {
  state.health[player] = clamp(value, 0, MAX_HEALTH);
  const percent = (state.health[player] / MAX_HEALTH) * 100;
  const healthBar = player === 1 ? ui.p1HealthBar : ui.p2HealthBar;
  healthBar.style.width = `${percent}%`;

  const text = player === 1 ? ui.p1HealthText : ui.p2HealthText;
  text.textContent = `${state.health[player]} / ${MAX_HEALTH}`;

  if (state.health[player] <= 0) {
    finishMatch(player === 1 ? 2 : 1);
  }
}

function setCombo(player, value) {
  state.combo[player] = value;
  const text = player === 1 ? ui.p1Combo : ui.p2Combo;
  text.textContent = String(value);
}

function updateSpecialUI(player) {
  const charge = state.specialCharge[player];
  const bar = player === 1 ? ui.p1SpecialBar : ui.p2SpecialBar;
  const status = player === 1 ? ui.p1SpecialStatus : ui.p2SpecialStatus;
  bar.style.width = `${(charge / SPECIAL_THRESHOLD) * 100}%`;

  if (charge >= SPECIAL_THRESHOLD) {
    status.textContent = 'LISTO';
    status.classList.add('ready');
  } else {
    status.textContent = 'ESPERANDO';
    status.classList.remove('ready');
  }
}

function addParticle(x, y, color, count = 12) {
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = `${x}px`;
    p.style.top = `${y}px`;
    p.style.width = `${3 + Math.random() * 8}px`;
    p.style.height = p.style.width;
    p.style.background = color;
    p.style.setProperty('--dx', `${(Math.random() - 0.5) * 140}px`);
    p.style.setProperty('--dy', `${-20 - Math.random() * 120}px`);
    ui.effectsLayer.appendChild(p);
    setTimeout(() => p.remove(), 700);
  }
}

function createBurst(x, y, type = 'fire') {
  const burst = document.createElement('div');
  burst.className = type === 'fire' ? 'fire-burst' : 'ice-burst';
  burst.style.left = `${x}px`;
  burst.style.top = `${y}px`;
  ui.effectsLayer.appendChild(burst);
  setTimeout(() => burst.remove(), 450);
}

function createImpactFlash() {
  const flash = document.createElement('div');
  flash.className = 'impact-flash';
  ui.effectsLayer.appendChild(flash);
  setTimeout(() => flash.remove(), 180);
}

function screenShake(intensity = 10) {
  ui.arena.style.transform = `translate(${(Math.random() - 0.5) * intensity}px, ${(Math.random() - 0.5) * intensity}px)`;
  setTimeout(() => {
    ui.arena.style.transform = 'translate(0, 0)';
  }, 110);
}

function getDragonCenter(player) {
  const el = dragons[player];
  const rect = el.getBoundingClientRect();
  const arenaRect = ui.arena.getBoundingClientRect();
  return {
    x: rect.left - arenaRect.left + rect.width / 2,
    y: rect.top - arenaRect.top + rect.height / 2,
  };
}

function triggerHit(player, target, damage, color, isSpecial = false) {
  setHealth(target, state.health[target] - damage);
  const centerTarget = getDragonCenter(target);
  addParticle(centerTarget.x, centerTarget.y, color, isSpecial ? 26 : 16);
  createBurst(centerTarget.x, centerTarget.y, color === '#7cc9ff' ? 'ice' : 'fire');
  createImpactFlash();
  screenShake(isSpecial ? 18 : 12);

  const dragonEl = dragons[target];
  dragonEl.classList.remove('hit');
  void dragonEl.offsetWidth;
  dragonEl.classList.add('hit');

  if (isSpecial) {
    dragons[target].classList.remove('special-attack');
    void dragons[target].offsetWidth;
    dragons[target].classList.add('special-attack');
  }
}

function countCombo(player, success) {
  if (success) {
    state.combo[player] += 1;
    state.specialCharge[player] += 1;
    if (state.specialCharge[player] >= SPECIAL_THRESHOLD) {
      state.specialCharge[player] = SPECIAL_THRESHOLD;
    }
  } else {
    state.combo[player] = 0;
  }

  setCombo(player, state.combo[player]);
  updateSpecialUI(player);
}

function canAttack(player) {
  const now = Date.now();
  return now - state.lastAttack[player] >= ATTACK_COOLDOWN;
}

function canUseSpecial(player) {
  const now = Date.now();
  return now - state.lastSpecial[player] >= SPECIAL_COOLDOWN && state.specialCharge[player] >= SPECIAL_THRESHOLD;
}

function attack(player) {
  if (!state.running || !canAttack(player)) return;

  const target = player === 1 ? 2 : 1;
  const attacker = dragons[player];
  const targetDragon = dragons[target];

  const attackCenter = getDragonCenter(player);
  const targetCenter = getDragonCenter(target);
  const distance = Math.abs(attackCenter.x - targetCenter.x);

  if (distance < 220) {
    state.lastAttack[player] = Date.now();
    countCombo(player, true);
    const damage = ATTACK_DAMAGE + Math.min(18, state.combo[player] * 3);
    triggerHit(player, target, damage, player === 1 ? '#ff8f3b' : '#7cc9ff');
    attacker.style.transform = 'translateX(4px)';
    setTimeout(() => attacker.style.transform = '', 90);
  } else {
    countCombo(player, false);
    addParticle(attackCenter.x, attackCenter.y, '#f5f5f5', 10);
  }
}

function useSpecial(player) {
  if (!state.running || !canUseSpecial(player)) return;

  const target = player === 1 ? 2 : 1;
  const damage = SPECIAL_DAMAGE + state.combo[player] * 12;
  state.lastSpecial[player] = Date.now();
  state.specialCharge[player] = 0;
  updateSpecialUI(player);

  const startX = getDragonCenter(player).x;
  const targetX = getDragonCenter(target).x;
  const color = player === 1 ? '#ff8f3b' : '#7cc9ff';

  if (player === 1) {
    // Habilidad especial del dragón de fuego: Meteor Infernal
    const meteor = document.createElement('div');
    meteor.className = 'fire-burst';
    meteor.style.left = `${startX - 30}px`;
    meteor.style.top = `${30}px`;
    ui.effectsLayer.appendChild(meteor);
    setTimeout(() => {
      meteor.style.left = `${targetX - 50}px`;
      meteor.style.top = `${60}px`;
      meteor.style.transform = 'scale(1.8)';
      setTimeout(() => meteor.remove(), 200);
    }, 120);

    setTimeout(() => {
      triggerHit(player, target, damage, color, true);
    }, 180);
  } else {
    // Habilidad especial del dragón de hielo: Tempestad Glacial
    for (let i = 0; i < 8; i++) {
      setTimeout(() => {
        const shard = document.createElement('div');
        shard.className = 'ice-burst';
        shard.style.left = `${targetX - 60 + i * 12}px`;
        shard.style.top = `${80 + (i % 3) * 26}px`;
        ui.effectsLayer.appendChild(shard);
        setTimeout(() => shard.remove(), 500);
      }, i * 40);
    }

    setTimeout(() => {
      triggerHit(player, target, damage, color, true);
    }, 220);
  }

  setCombo(player, 0);
  updateSpecialUI(player);
}

function finishMatch(winner) {
  state.running = false;
  state.winner = winner;
  ui.restartBtn.classList.remove('hidden');

  const winnerName = winner === 1 ? 'DRAGÓN FUEGO' : 'DRAGÓN HIELO';
  const body = document.body;
  body.style.filter = 'saturate(1.1)';

  const overlay = document.createElement('div');
  overlay.style.position = 'absolute';
  overlay.style.inset = '0';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';
  overlay.style.background = 'rgba(0,0,0,0.46)';
  overlay.style.zIndex = '50';
  overlay.style.backdropFilter = 'blur(3px)';

  const message = document.createElement('div');
  message.style.background = 'rgba(14, 18, 30, 0.8)';
  message.style.border = '1px solid rgba(255,255,255,0.12)';
  message.style.borderRadius = '18px';
  message.style.padding = '28px 34px';
  message.style.textAlign = 'center';
  message.style.boxShadow = '0 20px 40px rgba(0,0,0,0.35)';

  message.innerHTML = `
    <div style="font-size: 0.7rem; letter-spacing: 0.22em; color: #dfe9ff; margin-bottom: 8px;">VICTORIA</div>
    <div style="font-size: clamp(1.8rem, 3vw, 3rem); font-weight: 900; color: #fff2bf; margin-bottom: 12px;">${winnerName}</div>
    <div style="font-size: 0.9rem; opacity: 0.9; color: #dfe9ff;">¡Ha ganado la batalla!</div>
  `;

  overlay.appendChild(message);
  ui.arena.appendChild(overlay);
}

function resetGame() {
  state.running = true;
  state.winner = null;
  state.lastAttack = { 1: 0, 2: 0 };
  state.lastSpecial = { 1: 0, 2: 0 };
  state.combo = { 1: 0, 2: 0 };
  state.specialCharge = { 1: 0, 2: 0 };
  state.health = { 1: MAX_HEALTH, 2: MAX_HEALTH };

  ui.restartBtn.classList.add('hidden');
  document.querySelectorAll('.fire-burst, .ice-burst, .particle, .impact-flash').forEach((node) => node.remove());
  const overlay = ui.arena.querySelector('div[style*="backdrop-filter"]');
  if (overlay) overlay.remove();

  setHealth(1, MAX_HEALTH);
  setHealth(2, MAX_HEALTH);
  setCombo(1, 0);
  setCombo(2, 0);
  updateSpecialUI(1);
  updateSpecialUI(2);

  dragons[1].style.transform = '';
  dragons[2].style.transform = 'scaleX(-1)';
  dragons[1].classList.remove('hit', 'special-attack');
  dragons[2].classList.remove('hit', 'special-attack');

  document.body.style.filter = '';
}

function bindKeyboard() {
  window.addEventListener('keydown', (event) => {
    const key = event.key.toLowerCase();
    if (['a', 'd', 'w', 'f', 'g', 'k', 'l', 'arrowleft', 'arrowright', 'arrowup'].includes(key)) {
      event.preventDefault();
    }

    state.keys[key] = true;

    if (key === 'f') attack(1);
    if (key === 'g') useSpecial(1);
    if (key === 'k') attack(2);
    if (key === 'l') useSpecial(2);
  });

  window.addEventListener('keyup', (event) => {
    state.keys[event.key.toLowerCase()] = false;
  });
}

function bindTouchControls() {
  document.querySelectorAll('.touch-btn').forEach((btn) => {
    const action = btn.dataset.action;

    btn.addEventListener('pointerdown', () => {
      switch (action) {
        case 'move-left':
          state.keys.a = true;
          break;
        case 'move-right':
          state.keys.d = true;
          break;
        case 'jump':
          state.keys.w = true;
          break;
        case 'attack':
          attack(1);
          break;
        case 'special':
          useSpecial(1);
          break;
        case 'move-left-p2':
          state.keys.arrowleft = true;
          break;
        case 'move-right-p2':
          state.keys.arrowright = true;
          break;
        case 'jump-p2':
          state.keys.arrowup = true;
          break;
        case 'attack-p2':
          attack(2);
          break;
        case 'special-p2':
          useSpecial(2);
          break;
      }
    });

    btn.addEventListener('pointerup', () => {
      state.keys.a = false;
      state.keys.d = false;
      state.keys.w = false;
      state.keys.arrowleft = false;
      state.keys.arrowright = false;
      state.keys.arrowup = false;
    });
  });
}

function updateMovement() {
  if (!state.running) return;

  const speed = 6;
  const jump = 16;

  const p1 = dragons[1];
  const p2 = dragons[2];

  const p1Left = parseFloat(getComputedStyle(p1).left);
  const p2Left = parseFloat(getComputedStyle(p2).left);

  // Dragón 1
  if (state.keys.a) {
    p1.style.left = `${clamp(p1Left - speed, 5, 42)}%`;
  }
  if (state.keys.d) {
    p1.style.left = `${clamp(p1Left + speed, 5, 42)}%`;
  }
  if (state.keys.w) {
    p1.style.bottom = `${clamp(96 + jump, 96, 190)}px`;
    setTimeout(() => {
      p1.style.bottom = '96px';
      state.keys.w = false;
    }, 250);
  }

  // Dragón 2
  if (state.keys.arrowleft) {
    p2.style.right = `${clamp(parseFloat(getComputedStyle(p2).right) + speed, 5, 42)}%`;
  }
  if (state.keys.arrowright) {
    p2.style.right = `${clamp(parseFloat(getComputedStyle(p2).right) - speed, 5, 42)}%`;
  }
  if (state.keys.arrowup) {
    p2.style.bottom = `${clamp(96 + jump, 96, 190)}px`;
    setTimeout(() => {
      p2.style.bottom = '96px';
      state.keys.arrowup = false;
    }, 250);
  }
}

function gameLoop() {
  updateMovement();
  requestAnimationFrame(gameLoop);
}

function init() {
  setHealth(1, MAX_HEALTH);
  setHealth(2, MAX_HEALTH);
  setCombo(1, 0);
  setCombo(2, 0);
  updateSpecialUI(1);
  updateSpecialUI(2);

  bindKeyboard();
  bindTouchControls();
  ui.restartBtn.addEventListener('click', resetGame);
  requestAnimationFrame(gameLoop);
}

init();

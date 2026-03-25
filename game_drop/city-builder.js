// 2D City Builder Game Logic
// This file provides a simple grid-based city builder for the "The City" tab.

const CITY_GRID_SIZE = 10;
const TILE_SIZE = 40;
let cityMap = [];
let selectedBuilding = 'house';
const BUILDINGS = [
  { id: 'house', name: 'House', emoji: '🏠', cost: 10 },
  { id: 'farm', name: 'Farm', emoji: '🌾', cost: 8 },
  { id: 'shop', name: 'Shop', emoji: '🏪', cost: 15 },
  { id: 'park', name: 'Park', emoji: '🌳', cost: 5 }
];

function initCityMap() {
  cityMap = Array(CITY_GRID_SIZE).fill().map(() => Array(CITY_GRID_SIZE).fill(null));
}

function renderCityBuilder() {
  let html = `<div style="display:flex;gap:1rem;align-items:flex-start;">
    <canvas id='cityCanvas' width='${CITY_GRID_SIZE * TILE_SIZE}' height='${CITY_GRID_SIZE * TILE_SIZE}' style='border:1px solid var(--border2);background:var(--card2);'></canvas>
    <div style='min-width:120px;'>
      <div style='font-family:Space Mono,monospace;font-size:.9rem;margin-bottom:.5rem;'>Build:</div>
      ${BUILDINGS.map(b => `<button class='btn btn-sm' style='margin-bottom:.4rem;width:100%;${selectedBuilding===b.id?"background:var(--teal-d);color:var(--teal);border-color:var(--teal);":""}' onclick='selectBuilding("${b.id}")'>${b.emoji} ${b.name} (${b.cost}🌿)</button>`).join('')}
      <div class='status' id='cityBuildStatus'></div>
    </div>
  </div>`;
  const sec = document.getElementById('sec-overview');
  if(sec) sec.innerHTML = `<div class='eyebrow'>The City Builder</div><h2>Build Your City</h2>${html}`;
  drawCityMap();
}

function drawCityMap() {
  const canvas = document.getElementById('cityCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // Draw grid
  ctx.strokeStyle = '#1e2e40';
  for (let i = 0; i <= CITY_GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * TILE_SIZE, 0);
    ctx.lineTo(i * TILE_SIZE, CITY_GRID_SIZE * TILE_SIZE);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i * TILE_SIZE);
    ctx.lineTo(CITY_GRID_SIZE * TILE_SIZE, i * TILE_SIZE);
    ctx.stroke();
  }
  // Draw buildings
  ctx.font = '28px serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (let y = 0; y < CITY_GRID_SIZE; y++) {
    for (let x = 0; x < CITY_GRID_SIZE; x++) {
      const b = cityMap[y][x];
      if (b) ctx.fillText(b.emoji, x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2);
    }
  }
}

function selectBuilding(id) {
  selectedBuilding = id;
  renderCityBuilder();
}

function handleCityCanvasClick(e) {
  const canvas = document.getElementById('cityCanvas');
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / TILE_SIZE);
  const y = Math.floor((e.clientY - rect.top) / TILE_SIZE);
  if (x < 0 || y < 0 || x >= CITY_GRID_SIZE || y >= CITY_GRID_SIZE) return;
  if (cityMap[y][x]) {
    setCityBuildStatus('Tile already occupied.','blocked');
    return;
  }
  const b = BUILDINGS.find(b => b.id === selectedBuilding);
  if (!spendBreath(b.cost)) {
    setCityBuildStatus('Not enough Breath.','blocked');
    return;
  }
  cityMap[y][x] = b;
  drawCityMap();
  setCityBuildStatus(`Built a ${b.name}!`,'ok');
}

function setCityBuildStatus(msg,cls) {
  const el = document.getElementById('cityBuildStatus');
  if (el) { el.textContent = msg; el.className = 'status' + (cls ? ' ' + cls : ''); }
}

// Hook up canvas click
function setupCityBuilderEvents() {
  const canvas = document.getElementById('cityCanvas');
  if (canvas) {
    canvas.addEventListener('click', handleCityCanvasClick);
  }
}

// Main entry for "The City" tab
function startCityGame() {
  if (!window.cityMap) initCityMap();
  renderCityBuilder();
  setTimeout(setupCityBuilderEvents, 100);
}

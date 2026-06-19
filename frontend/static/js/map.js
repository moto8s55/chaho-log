// この地図画像の地理的範囲（北西端→南東端）
const MAP_BOUNDS = [
  [55, 91],    // 北西
  [14, 127],   // 南東
];

const map = L.map('map', {
  minZoom: 4,
  maxZoom: 8,
  zoomControl: true,
  maxBounds: MAP_BOUNDS,
  maxBoundsViscosity: 1.0,
});

// 地図をオーバーレイ範囲に固定
map.fitBounds(MAP_BOUNDS);

// ── 地図画像オーバーレイ ──
L.imageOverlay(
  '/static/images/china_tea_map.png',
  MAP_BOUNDS,
  { opacity: 1.0, interactive: false }
).addTo(map);

async function loadMap() {
  const [records, regions] = await Promise.all([
    fetch('/api/records').then(r => r.json()).catch(() => []),
    fetch('/api/regions').then(r => r.json()).catch(() => ({})),
  ]);

  const byRegion = {};
  for (const rec of records) {
    const region = rec['産地'] || '';
    if (!region) continue;
    if (!byRegion[region]) byRegion[region] = [];
    byRegion[region].push(rec);
  }

  for (const [region, recs] of Object.entries(byRegion)) {
    const coords = regions[region];
    if (!coords) continue;

    const icon = L.divIcon({
      className: '',
      html: `<div class="pin-stamp">${recs.length}</div>`,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
    });

    L.marker(coords, { icon })
      .addTo(map)
      .on('click', () => showPopup(region, recs));
  }
}

function showPopup(region, recs) {
  document.getElementById('popup-region').textContent = `📍 ${region}（${recs.length} 件）`;
  const list = document.getElementById('popup-list');
  list.innerHTML = recs.map(r => `
    <li>
      <span class="record-no">No.${r['No.']}</span>
      <strong>${r['茶葉名'] || '（名称未入力）'}</strong>
      　${r['茶類'] || ''}
      　<span class="record-star">${'★'.repeat(Number(r['評価']) || 0)}</span>
      <br><small style="color:var(--text2);letter-spacing:0.05em">${r['記録日'] || ''}　${r['場所'] || ''}</small>
    </li>
  `).join('');
  document.getElementById('popup-overlay').classList.remove('hidden');
}

document.getElementById('popup-close').addEventListener('click', () => {
  document.getElementById('popup-overlay').classList.add('hidden');
});
document.getElementById('popup-overlay').addEventListener('click', e => {
  if (e.target === e.currentTarget)
    document.getElementById('popup-overlay').classList.add('hidden');
});

loadMap();

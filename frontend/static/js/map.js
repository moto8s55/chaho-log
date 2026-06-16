// 中国茶主産地図の地理的範囲（画像の四隅に対応する緯度経度）
// 北西端 → 南東端
const MAP_BOUNDS = [
  [50.5, 96.0],   // 北西（内モンゴル・新疆付近）
  [17.5, 123.5],  // 南東（海南島・台湾付近）
];

const map = L.map('map', {
  crs: L.CRS.EPSG3857,
  minZoom: 4,
  maxZoom: 8,
}).setView([30, 110], 5);

// ── ベースマップ（薄く敷く）──
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  opacity: 0.08,
}).addTo(map);

// ── 中国茶産地図オーバーレイ ──
L.imageOverlay(
  '/static/images/china_tea_map.jpg',
  MAP_BOUNDS,
  { opacity: 0.88, interactive: false }
).addTo(map);

// 地図の表示範囲をオーバーレイに合わせる
map.fitBounds(MAP_BOUNDS);

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

// 画像サイズ: 1400 x 1661 px
// CRS.Simple: 座標は [y_from_bottom, x_from_left] (ピクセル単位)
const W = 1400, H = 1661;

const map = L.map('map', {
  crs: L.CRS.Simple,
  minZoom: -1,
  maxZoom: 2,
  zoomControl: true,
});

const IMG_BOUNDS = [[0, 0], [H, W]];

L.imageOverlay(
  '/static/images/china_tea_map.png',
  IMG_BOUNDS,
  { opacity: 1.0, interactive: false }
).addTo(map);

map.fitBounds(IMG_BOUNDS);
map.setMaxBounds([[- H * 0.1, -W * 0.1], [H * 1.1, W * 1.1]]);

// 各省のピクセル座標 [y_from_bottom, x_from_left]
// y_from_bottom = H - (y_from_top_px)
const PIXEL_COORDS = {
  "雲南省":         [H - 1195,  215],
  "四川省":         [H -  700,  310],
  "貴州省":         [H -  995,  520],
  "湖南省":         [H -  960,  700],
  "湖北省":         [H -  780,  730],
  "陝西省":         [H -  580,  565],
  "河南省":         [H -  630,  700],
  "山東省":         [H -  465,  840],
  "安徽省":         [H -  715,  885],
  "江蘇省":         [H -  630,  910],
  "浙江省":         [H -  880,  940],
  "江西省":         [H -  950,  815],
  "福建省":         [H - 1035,  945],
  "広東省":         [H - 1160,  775],
  "広西壮族自治区": [H - 1130,  610],
  "海南省":         [H - 1395,  730],
  "台湾":           [H - 1215, 1065],
};

async function loadMap() {
  const records = await fetch('/api/records').then(r => r.json()).catch(() => []);

  const byRegion = {};
  for (const rec of records) {
    const region = rec['産地'] || '';
    if (!region) continue;
    if (!byRegion[region]) byRegion[region] = [];
    byRegion[region].push(rec);
  }

  for (const [region, recs] of Object.entries(byRegion)) {
    const coords = PIXEL_COORDS[region];
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
  document.getElementById('popup-region').textContent = `${region}（${recs.length} 件）`;
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

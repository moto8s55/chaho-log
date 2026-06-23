// ── Leaflet GeoJSON Map ── 1920年代上海・古地図スタイル

const map = L.map('map', {
  minZoom: 3,
  maxZoom: 7,
  zoomControl: true,
});

// 古地図風タイル（ラベルなし薄色）
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 20,
  opacity: 0.15,  // ほぼ非表示にして海色をCSSで制御
}).addTo(map);

// 方位磁針を右下に追加
const compassEl = document.createElement('div');
compassEl.className = 'compass-rose';
compassEl.innerHTML = `
<svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
  <circle cx="36" cy="36" r="34" fill="#E8DCC8" stroke="#5C3D1E" stroke-width="1.5" opacity="0.92"/>
  <circle cx="36" cy="36" r="28" fill="none" stroke="#8B7040" stroke-width="0.6" stroke-dasharray="3,3"/>
  <circle cx="36" cy="36" r="4" fill="#5C3D1E"/>
  <!-- 北（赤） -->
  <polygon points="36,6 31,36 36,30 41,36" fill="#8B2515"/>
  <!-- 南（白） -->
  <polygon points="36,66 31,36 36,42 41,36" fill="#D4C49A" stroke="#5C3D1E" stroke-width="0.5"/>
  <!-- 東 -->
  <polygon points="66,36 36,31 42,36 36,41" fill="#C8A878" stroke="#5C3D1E" stroke-width="0.5"/>
  <!-- 西 -->
  <polygon points="6,36 36,31 30,36 36,41" fill="#C8A878" stroke="#5C3D1E" stroke-width="0.5"/>
  <!-- 方位ラベル -->
  <text x="36" y="18" text-anchor="middle" font-family="serif" font-size="9" fill="#5C3D1E" font-weight="bold">北</text>
  <text x="36" y="62" text-anchor="middle" font-family="serif" font-size="8" fill="#5C3D1E">南</text>
  <text x="60" y="40" text-anchor="middle" font-family="serif" font-size="8" fill="#5C3D1E">東</text>
  <text x="12" y="40" text-anchor="middle" font-family="serif" font-size="8" fill="#5C3D1E">西</text>
</svg>`;
document.getElementById('map').appendChild(compassEl);

// 色パレット（古地図・くすんだ琥珀色調）
const COLOR = {
  tea:       '#C8A060',  // 茶産地：深い黄褐色（古地図の陸地色）
  teaBorder: '#3A2008',
  ctx:       '#BCA878',  // コンテキスト省：くすんだ羊皮紙
  ctxBorder: '#6A5030',
  hover:     '#8B5A20',
  label:     '#1E0E04',
};

let geojsonLayer = null;
let labelMarkers = [];

function provinceStyle(feature) {
  return feature.properties.is_tea ? {
    fillColor: COLOR.tea,
    color: COLOR.teaBorder,
    weight: 1.2,
    fillOpacity: 0.75,
  } : {
    fillColor: COLOR.ctx,
    color: COLOR.ctxBorder,
    weight: 0.6,
    fillOpacity: 0.45,
  };
}

function onEachFeature(feature, layer) {
  layer.on({
    mouseover: e => {
      if (feature.properties.is_tea) {
        e.target.setStyle({ fillColor: COLOR.hover, fillOpacity: 0.9 });
      }
    },
    mouseout: e => {
      geojsonLayer.resetStyle(e.target);
    },
  });
}

// 省名ラベルをDivIconで配置
function addProvinceLabels(features) {
  labelMarkers.forEach(m => map.removeLayer(m));
  labelMarkers = [];
  features.forEach(f => {
    const [lat, lng] = f.properties.centroid;
    const name = f.properties.name_zh;
    const isTea = f.properties.is_tea;
    const icon = L.divIcon({
      className: '',
      html: `<span style="font-family:'Noto Serif SC',serif;font-size:${isTea?11:9}px;color:${COLOR.label};opacity:${isTea?'0.85':'0.5'};white-space:nowrap;text-shadow:0 0 3px #E8DCC8,0 0 3px #E8DCC8">${name}</span>`,
      iconSize: [80, 16],
      iconAnchor: [40, 8],
    });
    const m = L.marker([lat, lng], { icon, interactive: false }).addTo(map);
    labelMarkers.push(m);
  });
}

async function loadMap() {
  // GeoJSONと記録データを並行取得
  const [geoData, records] = await Promise.all([
    fetch('/static/images/china_provinces.geojson').then(r => r.json()),
    fetch('/api/records').then(r => r.json()).catch(() => []),
  ]);

  // GeoJSONレイヤー描画
  geojsonLayer = L.geoJSON(geoData, {
    style: provinceStyle,
    onEachFeature,
  }).addTo(map);

  // 地図範囲を中国全土に合わせる
  map.fitBounds([[17, 95], [45, 125]]);

  // 省名ラベル
  addProvinceLabels(geoData.features);

  // 記録データを省ごとに集計
  const byRegion = {};
  for (const rec of records) {
    const region = rec['産地'] || '';
    if (!region) continue;
    if (!byRegion[region]) byRegion[region] = [];
    byRegion[region].push(rec);
  }

  // 各省の重心にピンを配置
  const provinceMap = {};
  for (const f of geoData.features) {
    provinceMap[f.properties.name_zh] = f.properties.centroid;
  }

  for (const [region, recs] of Object.entries(byRegion)) {
    const coords = provinceMap[region];
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

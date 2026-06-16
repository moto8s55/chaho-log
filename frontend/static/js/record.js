// Set today's date
document.getElementById('field-date').valueAsDate = new Date();

// Load dropdowns from API
async function loadDropdowns() {
  try {
    const data = await fetch('/api/dropdowns').then(r => r.json());
    const map = {
      '産地': '産地', '茶類': '茶類', '天気': '天気',
      '海抜': '海抜', '茶山環境': '茶山環境', '茶樹年齢': '茶樹年齢',
      '樹形': '樹形', '土質': '土質', '茶壺材質': '茶壺材質',
      '水質': '水質', '焼水方式': '焼水方式', '口腔濃度': '口腔濃度',
      '回甘': '回甘', '生津': '生津', '喉韻': '喉韻', '推薦度': '推薦度',
    };
    for (const [key, name] of Object.entries(map)) {
      const sel = document.querySelector(`select[name="${name}"]`);
      if (!sel || !data[key]) continue;
      data[key].forEach(opt => {
        const o = document.createElement('option');
        o.value = opt; o.textContent = opt;
        sel.appendChild(o);
      });
    }

    // Checkbox group for 身体反応
    const group = document.getElementById('身体反応-group');
    if (group && data['身体反応']) {
      data['身体反応'].forEach(opt => {
        const lbl = document.createElement('label');
        const cb = document.createElement('input');
        cb.type = 'checkbox'; cb.value = opt; cb.name = '身体反応';
        lbl.appendChild(cb);
        lbl.appendChild(document.createTextNode(opt));
        group.appendChild(lbl);
      });
    }
  } catch (_) { /* offline: dropdowns empty, user types manually */ }
}
loadDropdowns();

// Accordion
document.querySelectorAll('.accordion-header').forEach(btn => {
  btn.addEventListener('click', () => {
    const section = btn.closest('.accordion');
    const body = section.querySelector('.accordion-body');
    const arrow = btn.querySelector('.arrow');
    const isOpen = section.classList.toggle('open');
    body.classList.toggle('hidden', !isOpen);
    arrow.textContent = isOpen ? '▲' : '▼';
  });
});

// Badge: count filled fields per section
function updateBadges() {
  document.querySelectorAll('.accordion').forEach(section => {
    const inputs = section.querySelectorAll('input:not([type=file]):not([type=hidden]):not([type=checkbox]), select, textarea');
    const checkboxes = section.querySelectorAll('input[type=checkbox]:checked');
    const hidden = section.querySelectorAll('input[type=hidden]');
    let count = 0;
    inputs.forEach(el => { if (el.value) count++; });
    count += checkboxes.length;
    hidden.forEach(el => { if (el.value) count++; });
    const badge = section.querySelector('.badge');
    if (count > 0) {
      badge.textContent = count;
      badge.classList.add('visible');
    } else {
      badge.classList.remove('visible');
    }
  });
}
document.getElementById('record-form').addEventListener('change', updateBadges);
document.getElementById('record-form').addEventListener('input', updateBadges);

// Star rating
const stars = document.querySelectorAll('.star-input span');
const starValue = document.getElementById('star-value');
stars.forEach(s => {
  s.addEventListener('click', () => {
    const v = Number(s.dataset.v);
    starValue.value = v;
    stars.forEach(st => st.classList.toggle('on', Number(st.dataset.v) <= v));
    updateBadges();
  });
});

// Toggle buttons
document.querySelectorAll('.toggle-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const field = btn.dataset.field;
    document.querySelectorAll(`.toggle-btn[data-field="${field}"]`).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('drink-again-value').value = btn.dataset.value;
    updateBadges();
  });
});

// Photo preview
function setupPhoto(inputId, previewId) {
  document.getElementById(inputId).addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;
    const preview = document.getElementById(previewId);
    preview.src = URL.createObjectURL(file);
    preview.classList.remove('hidden');
    updateBadges();
  });
}
setupPhoto('photo1', 'photo1-preview');
setupPhoto('photo2', 'photo2-preview');

// Compress image client-side
function compressImage(file, maxPx = 800, quality = 0.7) {
  return new Promise(resolve => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      let { width: w, height: h } = img;
      if (Math.max(w, h) > maxPx) {
        const r = maxPx / Math.max(w, h);
        w = Math.round(w * r); h = Math.round(h * r);
      }
      const canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      canvas.toBlob(resolve, 'image/jpeg', quality);
    };
    img.src = url;
  });
}

// Form submit
document.getElementById('record-form').addEventListener('submit', async e => {
  e.preventDefault();
  const status = document.getElementById('save-status');
  const btn = e.target.querySelector('.btn-save');
  btn.disabled = true;
  status.textContent = '保存中…';

  const fd = new FormData(e.target);
  const record = {};
  for (const [k, v] of fd.entries()) {
    if (['photo1', 'photo2'].includes(k)) continue;
    if (record[k]) {
      record[k] = [record[k], v].flat().join('、');
    } else {
      record[k] = v;
    }
  }

  const photo1File = document.getElementById('photo1').files[0];
  const photo2File = document.getElementById('photo2').files[0];
  const photo1Blob = photo1File ? await compressImage(photo1File) : null;
  const photo2Blob = photo2File ? await compressImage(photo2File) : null;

  if (navigator.onLine) {
    try {
      const postFd = new FormData();
      postFd.append('record_json', JSON.stringify(record));
      if (photo1Blob) postFd.append('photo1', new File([photo1Blob], 'photo1.jpg', { type: 'image/jpeg' }));
      if (photo2Blob) postFd.append('photo2', new File([photo2Blob], 'photo2.jpg', { type: 'image/jpeg' }));
      const res = await fetch('/api/records', { method: 'POST', body: postFd });
      if (res.ok) {
        status.textContent = '✅ 送信しました！';
        setTimeout(() => location.href = '/', 1200);
        return;
      }
    } catch (_) {}
  }

  // Offline: save locally
  await savePending(record, photo1Blob, photo2Blob);
  status.textContent = '📱 端末に保存しました。電波のいい時に自動で送信されます。';
  btn.disabled = false;
  await updateSyncBar();
});

const API = '';  // same origin; set to full URL in production if needed

async function syncPending() {
  const items = await getPending();
  if (items.length === 0) return 0;

  let synced = 0;
  for (const item of items) {
    try {
      const fd = new FormData();
      fd.append('record_json', JSON.stringify(item.record));
      if (item.photo1Blob) fd.append('photo1', new File([item.photo1Blob], 'photo1.jpg', { type: 'image/jpeg' }));
      if (item.photo2Blob) fd.append('photo2', new File([item.photo2Blob], 'photo2.jpg', { type: 'image/jpeg' }));

      const res = await fetch(`${API}/api/records`, { method: 'POST', body: fd });
      if (res.ok) {
        await deletePending(item.id);
        synced++;
      }
    } catch (_) { /* offline, skip */ }
  }
  return synced;
}

async function updateSyncBar() {
  const bar = document.getElementById('sync-bar');
  if (!bar) return;
  const items = await getPending();
  const count = document.getElementById('sync-count');
  if (items.length > 0) {
    count.textContent = items.length;
    bar.classList.remove('hidden');
  } else {
    bar.classList.add('hidden');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateSyncBar();

  const syncBtn = document.getElementById('sync-btn');
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      syncBtn.textContent = '同期中…';
      syncBtn.disabled = true;
      const n = await syncPending();
      await updateSyncBar();
      syncBtn.textContent = '今すぐ同期する';
      syncBtn.disabled = false;
      if (n > 0) location.reload();
    });
  }
});

// Auto sync when coming online
window.addEventListener('online', async () => {
  await syncPending();
  await updateSyncBar();
});

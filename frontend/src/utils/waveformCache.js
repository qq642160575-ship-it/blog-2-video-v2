/**
 * Waveform cache utility using IndexedDB
 * Caches audio waveform data to improve loading performance
 */

const DB_NAME = 'timeline-editor-cache';
const DB_VERSION = 1;
const STORE_NAME = 'waveforms';

/**
 * Open IndexedDB database
 */
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'url' });
      }
    };
  });
}

/**
 * Cache waveform data
 */
export async function cacheWaveform(audioUrl, waveformData) {
  try {
    const db = await openDB();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    const data = {
      url: audioUrl,
      data: waveformData,
      timestamp: Date.now(),
    };

    await new Promise((resolve, reject) => {
      const request = store.put(data);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });

    console.log('Waveform cached:', audioUrl);
  } catch (error) {
    console.error('Failed to cache waveform:', error);
  }
}

/**
 * Get cached waveform data
 */
export async function getCachedWaveform(audioUrl) {
  try {
    const db = await openDB();
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);

    const data = await new Promise((resolve, reject) => {
      const request = store.get(audioUrl);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });

    if (data) {
      // Check if cache is still valid (24 hours)
      const age = Date.now() - data.timestamp;
      const maxAge = 24 * 60 * 60 * 1000; // 24 hours

      if (age < maxAge) {
        console.log('Waveform loaded from cache:', audioUrl);
        return data.data;
      } else {
        // Cache expired, delete it
        await deleteCachedWaveform(audioUrl);
        return null;
      }
    }

    return null;
  } catch (error) {
    console.error('Failed to get cached waveform:', error);
    return null;
  }
}

/**
 * Delete cached waveform
 */
export async function deleteCachedWaveform(audioUrl) {
  try {
    const db = await openDB();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    await new Promise((resolve, reject) => {
      const request = store.delete(audioUrl);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });

    console.log('Waveform cache deleted:', audioUrl);
  } catch (error) {
    console.error('Failed to delete cached waveform:', error);
  }
}

/**
 * Clear all cached waveforms
 */
export async function clearWaveformCache() {
  try {
    const db = await openDB();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    await new Promise((resolve, reject) => {
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });

    console.log('All waveform cache cleared');
  } catch (error) {
    console.error('Failed to clear waveform cache:', error);
  }
}

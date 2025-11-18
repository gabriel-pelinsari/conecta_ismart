const STORAGE_KEY = "ismart_event_covers";

function loadMap() {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed ? parsed : {};
  } catch {
    return {};
  }
}

function saveMap(map) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {
    // ignore storage quota issues
  }
}

export function saveEventCover(eventId, dataUrl) {
  if (!eventId || !dataUrl) return;
  const map = loadMap();
  map[eventId] = dataUrl;
  saveMap(map);
}

export function getEventCover(eventId) {
  if (!eventId) return null;
  const map = loadMap();
  return map[eventId] || null;
}

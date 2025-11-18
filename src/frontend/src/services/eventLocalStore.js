const STORAGE_KEY = "ismart_local_events";

function loadEvents() {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveEvents(events) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  } catch {
    // ignore quota errors
  }
}

export function saveLocalEvent(event) {
  if (!event || !event.id) return;
  const events = loadEvents().filter((item) => item.id !== event.id);
  events.unshift(event);
  saveEvents(events.slice(0, 20));
}

export function getLocalEvents() {
  return loadEvents();
}

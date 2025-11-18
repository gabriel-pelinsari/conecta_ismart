import mockFeed from "../mocks/feed";

function applyFilters(items, { search, category, university }) {
  let filtered = [...items];

  if (search) {
    const term = search.toLowerCase();
    filtered = filtered.filter((item) => {
      return (
        item.title?.toLowerCase().includes(term) ||
        item.description?.toLowerCase().includes(term)
      );
    });
  }

  if (category && category !== "todos") {
    filtered = filtered.filter((item) => {
      if (item.type === "event" || item.type === "poll") {
        const scope = (item.audience || item.type) ?? "geral";
        return scope === category;
      }
      return (item.category || "geral") === category;
    });
  }

  if (category === "faculdade" && university) {
    filtered = filtered.filter((item) => item.audience === "faculdade" || item.category === "faculdade");
  }

  return filtered;
}

export const feedApi = {
  async list({ skip = 0, limit = 20, search = "", category, university } = {}) {
    const filtered = applyFilters(mockFeed, { search, category, university });
    const slice = filtered.slice(skip, skip + limit);
    return new Promise((resolve) => {
      setTimeout(() => resolve(slice), 300);
    });
  },
};

export default feedApi;

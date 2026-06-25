import { fetchJson } from "./client.js";

export function listCategories() {
  return fetchJson("/api/categories");
}

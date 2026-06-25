import { fetchJson } from "./client.js";

export function listNationalities() {
  return fetchJson("/api/nationalities");
}

import { fetchJson } from "./client.js";

export function listAuthors() {
  return fetchJson("/api/authors");
}

export function createAuthor(authorData) {
  return fetchJson("/api/authors", {
    method: "POST",
    body: JSON.stringify(authorData),
  });
}

export function listBooksByAuthor(authorId) {
  return fetchJson(`/api/authors/${authorId}/books`);
}

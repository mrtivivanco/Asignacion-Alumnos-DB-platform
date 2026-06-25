import { fetchJson } from "./client.js";

export function listBooks() {
  return fetchJson("/api/books");
}

export function createBook(bookData) {
  return fetchJson("/api/books", {
    method: "POST",
    body: JSON.stringify(bookData),
  });
}

export function getBook(bookId) {
  return fetchJson(`/api/books/${bookId}`);
}

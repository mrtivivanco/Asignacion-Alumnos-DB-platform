import { createAuthor, listBooksByAuthor } from "../api/authors.js";
import { createBook } from "../api/books.js";
import { renderAuthorBooks } from "./render.js";

export function bindFormHandlers({ loadData, showError }) {
  document.querySelector("#author-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      await createAuthor({
        name: formData.get("name"),
        nationality_id: Number(formData.get("nationality_id")),
      });

      form.reset();
      await loadData();
    } catch (error) {
      showError(error);
    }
  });

  document.querySelector("#book-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      await createBook({
        title: formData.get("title"),
        publication_year: Number(formData.get("publication_year")),
        author_id: Number(formData.get("author_id")),
        category_id: Number(formData.get("category_id")),
      });

      form.reset();
      await loadData();
    } catch (error) {
      showError(error);
    }
  });

  document.querySelector("#load-author-books").addEventListener("click", async () => {
    const authorId = document.querySelector("#books-by-author-select").value;

    try {
      const books = await listBooksByAuthor(authorId);
      renderAuthorBooks(books);
    } catch (error) {
      showError(error);
    }
  });
}

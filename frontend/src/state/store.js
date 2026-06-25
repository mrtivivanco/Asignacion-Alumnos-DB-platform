export const state = {
  nationalities: [],
  categories: [],
  authors: [],
  books: [],
};

export function setReferenceData({ nationalities, categories, authors, books }) {
  state.nationalities = nationalities;
  state.categories = categories;
  state.authors = authors;
  state.books = books;
}

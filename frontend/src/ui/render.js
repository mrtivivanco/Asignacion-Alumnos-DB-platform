function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fillSelect(selector, items, labelFor) {
  const select = document.querySelector(selector);
  const selectedValue = select.value;

  select.innerHTML = items
    .map((item) => `<option value="${item.id}">${escapeHtml(labelFor(item))}</option>`)
    .join("");

  if (selectedValue) {
    select.value = selectedValue;
  }
}

export function setStatusMessage(message) {
  document.querySelector("#status-message").textContent = message;
}

export function renderBooks(books) {
  const list = document.querySelector("#book-list");

  list.innerHTML = books
    .map(
      (book) => `
        <li class="rounded-2xl bg-[#f4efe6] p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <strong class="text-lg font-black">${escapeHtml(book.title)}</strong>
            <span class="rounded-full bg-white px-3 py-1 text-sm font-bold text-[#6d5946]">${book.publication_year}</span>
          </div>
          <p class="mt-2 text-sm text-[#6d5946]">
            ${escapeHtml(book.author.name)} · ${escapeHtml(book.category.name)}
          </p>
        </li>
      `,
    )
    .join("");
}

export function renderAuthors(authors) {
  const list = document.querySelector("#author-list");

  list.innerHTML = authors
    .map(
      (author) => `
        <li class="flex flex-col gap-2 rounded-2xl bg-[#f4efe6] p-4 sm:flex-row sm:items-center sm:justify-between">
          <strong class="text-lg font-black">${escapeHtml(author.name)}</strong>
          <span class="rounded-full bg-white px-3 py-1 text-sm font-bold text-[#6d5946]">
            ${escapeHtml(author.nationality.name)}
          </span>
        </li>
      `,
    )
    .join("");
}

export function renderSelects(state) {
  fillSelect("#author-nationality", state.nationalities, (nationality) => nationality.name);
  fillSelect("#book-author", state.authors, (author) => author.name);
  fillSelect("#book-category", state.categories, (category) => category.name);
  fillSelect("#books-by-author-select", state.authors, (author) => author.name);
}

export function renderAuthorBooks(books) {
  const list = document.querySelector("#author-book-list");

  list.innerHTML = books
    .map(
      (book) => `
        <li class="flex flex-col gap-2 rounded-2xl bg-[#f4efe6] p-4 sm:flex-row sm:items-center sm:justify-between">
          <strong class="text-lg font-black">${escapeHtml(book.title)}</strong>
          <span class="rounded-full bg-white px-3 py-1 text-sm font-bold text-[#6d5946]">
            ${book.publication_year} · ${escapeHtml(book.category.name)}
          </span>
        </li>
      `,
    )
    .join("");
}

export function render(state) {
  renderSelects(state);
  renderBooks(state.books);
  renderAuthors(state.authors);
}

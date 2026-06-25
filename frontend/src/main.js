import "./styles.css";

import { listAuthors } from "./api/authors.js";
import { listBooks } from "./api/books.js";
import { listCategories } from "./api/categories.js";
import { listNationalities } from "./api/nationalities.js";
import { setReferenceData, state } from "./state/store.js";
import { bindFormHandlers } from "./ui/forms.js";
import { render, setStatusMessage } from "./ui/render.js";

async function loadData() {
  setStatusMessage("Loading data from the API...");

  const [nationalities, categories, authors, books] = await Promise.all([
    listNationalities(),
    listCategories(),
    listAuthors(),
    listBooks(),
  ]);

  setReferenceData({ nationalities, categories, authors, books });

  render(state);
  setStatusMessage("Connected. Data is coming from PostgreSQL through FastAPI.");
}

function showError(error) {
  setStatusMessage(`Could not complete request: ${error.message}`);
}

bindFormHandlers({ loadData, showError });

loadData().catch((error) => {
  setStatusMessage(`Could not load API data: ${error.message}`);
});

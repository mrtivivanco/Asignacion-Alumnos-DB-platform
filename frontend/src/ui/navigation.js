const DEFAULT_PAGE = "dashboard";

function pageFromHash() {
  return window.location.hash.replace("#", "") || DEFAULT_PAGE;
}

function closeSidebar() {
  const sidebar = document.querySelector("#app-sidebar");
  const backdrop = document.querySelector("#sidebar-backdrop");

  sidebar.dataset.open = "false";
  backdrop.hidden = true;
}

function openSidebar() {
  const sidebar = document.querySelector("#app-sidebar");
  const backdrop = document.querySelector("#sidebar-backdrop");

  sidebar.dataset.open = "true";
  backdrop.hidden = false;
}

function showPage(pageId) {
  const views = [...document.querySelectorAll("[data-page]")];
  const targetPage = views.some((view) => view.dataset.page === pageId) ? pageId : DEFAULT_PAGE;

  for (const view of views) {
    view.classList.toggle("hidden", view.dataset.page !== targetPage);
  }

  for (const link of document.querySelectorAll("[data-page-link]")) {
    const isCurrent = link.dataset.pageLink === targetPage;
    if (isCurrent) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  }

  closeSidebar();
  window.scrollTo({ top: 0, behavior: "auto" });
}

function bindPageLinks() {
  for (const link of document.querySelectorAll("[data-page-link]")) {
    link.addEventListener("click", (event) => {
      const pageId = link.dataset.pageLink;

      if (!pageId) {
        return;
      }

      event.preventDefault();

      if (window.location.hash === `#${pageId}`) {
        showPage(pageId);
        return;
      }

      window.location.hash = pageId;
    });
  }
}

function bindSidebarToggles() {
  for (const toggle of document.querySelectorAll("[data-sidebar-toggle]")) {
    toggle.addEventListener("click", () => {
      const section = toggle.closest("[data-sidebar-section]");
      const panel = section.querySelector("[data-sidebar-panel]");
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";

      toggle.setAttribute("aria-expanded", String(!isExpanded));
      panel.hidden = isExpanded;
    });
  }
}

function bindMobileSidebar() {
  document.querySelector("#sidebar-toggle").addEventListener("click", openSidebar);
  document.querySelector("#sidebar-close").addEventListener("click", closeSidebar);
  document.querySelector("#sidebar-backdrop").addEventListener("click", closeSidebar);
}

export function bindNavigation() {
  bindPageLinks();
  bindSidebarToggles();
  bindMobileSidebar();

  window.addEventListener("hashchange", () => showPage(pageFromHash()));
  showPage(pageFromHash());
}

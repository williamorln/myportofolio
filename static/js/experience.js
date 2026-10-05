const experienceApp = document.getElementById("experience-app");

if (experienceApp) {
  const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";
  const SEARCH_DEBOUNCE_DELAY = 300;
  const isAuthenticated = experienceApp.dataset.isAuthenticated === "true";
  const isSuperuser = experienceApp.dataset.isSuperuser === "true";
  const isEditor = experienceApp.dataset.isEditor === "true";
  const csrfToken = experienceApp.dataset.csrfToken;

  const filterForm = document.getElementById("experience-filter-form");
  const searchInput = document.getElementById("experience-title");
  const statusSelect = document.getElementById("experience-status");
  const resetButton = document.getElementById("experience-reset");
  const retryButton = document.getElementById("experience-retry");
  const jsonLink = document.getElementById("experience-json-link");
  const resultCount = document.getElementById("experience-result-count");
  const loadingState = document.getElementById("experience-loading");
  const errorState = document.getElementById("experience-error");
  const emptyState = document.getElementById("experience-empty");
  const groupsContainer = document.getElementById("experience-groups");
  const experienceForm = document.getElementById("experience-form");

  let searchDebounceTimer;
  let experienceAbortController;

  function buildItemUrl(template, experienceId) {
    return template.replace(UUID_PLACEHOLDER, experienceId);
  }

  function safeImageUrl(value) {
    const url = String(value ?? "").trim();
    return /^(https?:\/\/|\/static\/)/i.test(url) ? url : "";
  }

  function formatDate(value) {
    if (!value) return "";
    return new Intl.DateTimeFormat("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(value));
  }

  function displayPageSection({
    showLoading = false,
    showError = false,
    showEmpty = false,
    showGroups = false,
  }) {
    loadingState.classList.toggle("hide", !showLoading);
    errorState.classList.toggle("hide", !showError);
    emptyState.classList.toggle("hide", !showEmpty);
    groupsContainer.classList.toggle("hide", !showGroups);
  }

  function buildExperienceCard(item) {
    const experience = item.fields;
    const experienceId = item.pk;
    const thumbnailUrl = safeImageUrl(experience.thumbnail);
    const portraitClass = [
      "Self-Started Floral Business",
      "Academic & Teaching Staff – BETIS Fasilkom UI",
    ].includes(experience.title) ? " experience-thumbnail--portrait" : "";
    const thumbnailHtml = thumbnailUrl
      ? `<div class="experience-thumbnail-frame">
           <img class="experience-thumbnail${portraitClass}"
                src="${escapeHtml(thumbnailUrl)}"
                alt="Thumbnail ${escapeHtml(experience.title)}">
         </div>`
      : "";
    const statusHtml = experience.is_ongoing
      ? '<p class="experience-status experience-status-ongoing">Sedang berlangsung</p>'
      : `<p class="experience-status">Selesai &middot; ${escapeHtml(formatDate(experience.ended_at))}</p>`;

    const starUrl = buildItemUrl(
      experienceApp.dataset.starUrlTemplate,
      experienceId,
    );
    const starTitle = experience.star_count > 0
      ? `Dibintangi oleh ${experience.starred_by_names}`
      : "Jadilah yang pertama memberi star";
    const starHtml = `
      <form method="post" action="${escapeHtml(starUrl)}" class="star-form experience-star-form">
        <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken)}">
        <button type="submit"
                class="button button-star${experience.is_starred ? " is-starred" : ""}"
                title="${escapeHtml(starTitle)}">
          <span aria-hidden="true">★</span>
          ${experience.is_starred ? "Unstar" : "Star"}
          <span class="star-count">${experience.star_count}</span>
        </button>
      </form>`;

    let managementHtml = "";
    if (isSuperuser || isEditor) {
      const updateUrl = buildItemUrl(
        experienceApp.dataset.updateUrlTemplate,
        experienceId,
      );
      managementHtml += `
        <a class="button"
           href="${escapeHtml(updateUrl)}"
           aria-label="Edit ${escapeHtml(experience.title)}">Edit</a>`;
    }
    if (isSuperuser) {
      const deleteUrl = buildItemUrl(
        experienceApp.dataset.deleteUrlTemplate,
        experienceId,
      );
      managementHtml += `
        <a class="button button-danger"
           href="${escapeHtml(deleteUrl)}"
           aria-label="Hapus ${escapeHtml(experience.title)}">Hapus</a>`;
    }

    return `
      <article class="experience-card">
        ${thumbnailHtml}
        <div class="experience-card-body">
          <h3>${escapeHtml(experience.title)}</h3>
          <p class="experience-description">${escapeHtml(experience.description)}</p>
          ${statusHtml}
          <div class="project-actions">
            ${starHtml}
            ${managementHtml}
          </div>
        </div>
      </article>`;
  }

  function renderExperiences(items) {
    const groupedItems = new Map();
    items.forEach((item) => {
      const category = item.fields.category_display;
      if (!groupedItems.has(category)) groupedItems.set(category, []);
      groupedItems.get(category).push(item);
    });

    groupsContainer.innerHTML = Array.from(groupedItems.entries())
      .map(([category, experiences]) => `
        <section class="experience-group">
          <div class="experience-group-heading">
            <h2 class="experience-group-title">${escapeHtml(category)}</h2>
            <span class="experience-group-count">${experiences.length}</span>
          </div>
          <div class="experience-grid">
            ${experiences.map(buildExperienceCard).join("")}
          </div>
        </section>`)
      .join("");
  }

  function currentFilters() {
    return {
      title: searchInput.value.trim(),
      status: statusSelect.value,
    };
  }

  function buildQueryString(filters) {
    const params = new URLSearchParams();
    if (filters.title) params.set("title", filters.title);
    if (filters.status) params.set("status", filters.status);
    return params.toString();
  }

  function syncLinksAndLocation(queryString) {
    const suffix = queryString ? `?${queryString}` : "";
    jsonLink.href = `${experienceApp.dataset.listEndpoint}${suffix}`;
    window.history.replaceState({}, "", `${window.location.pathname}${suffix}`);
  }

  async function fetchExperiences() {
    if (experienceAbortController) experienceAbortController.abort();
    experienceAbortController = new AbortController();
    const queryString = buildQueryString(currentFilters());

    try {
      resultCount.textContent = "";
      displayPageSection({ showLoading: true });
      const endpoint = `${experienceApp.dataset.listEndpoint}${queryString ? `?${queryString}` : ""}`;
      const response = await fetch(endpoint, {
        headers: { Accept: "application/json" },
        signal: experienceAbortController.signal,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const items = await response.json();
      syncLinksAndLocation(queryString);
      resultCount.textContent = `${items.length} pengalaman ditampilkan.`;
      groupsContainer.innerHTML = "";

      if (items.length === 0) {
        displayPageSection({ showEmpty: true });
        return;
      }

      renderExperiences(items);
      displayPageSection({ showGroups: true });
    } catch (error) {
      if (error.name === "AbortError") return;
      console.error("Error loading experiences:", error);
      displayPageSection({ showError: true });
    }
  }

  function scheduleSearch() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(fetchExperiences, SEARCH_DEBOUNCE_DELAY);
  }

  filterForm.addEventListener("submit", (event) => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    fetchExperiences();
  });
  searchInput.addEventListener("input", scheduleSearch);
  statusSelect.addEventListener("change", () => {
    clearTimeout(searchDebounceTimer);
    fetchExperiences();
  });
  resetButton.addEventListener("click", () => {
    searchInput.value = "";
    statusSelect.value = "";
    clearTimeout(searchDebounceTimer);
    fetchExperiences();
  });
  retryButton.addEventListener("click", fetchExperiences);

  groupsContainer.addEventListener("submit", async (event) => {
    const starForm = event.target.closest(".experience-star-form");
    if (!starForm || !isAuthenticated) return;
    event.preventDefault();

    const button = starForm.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      const response = await fetch(starForm.action, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: new FormData(starForm),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      await response.json();
      await fetchExperiences();
    } catch (error) {
      console.error("Error updating star:", error);
      showToast(
        "Gagal memperbarui star",
        "Tidak dapat menyimpan perubahan. Silakan coba lagi.",
        "error",
      );
      button.disabled = false;
    }
  });

  function closeExperienceModal() {
    const modal = document.getElementById("add-experience-modal");
    if (modal && modal.matches(":popover-open")) modal.hidePopover();
  }

  async function addExperience(event) {
    event.preventDefault();
    const submitButton = experienceForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
      const response = await fetch(experienceApp.dataset.createEndpoint, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: new FormData(experienceForm),
      });
      const result = await response.json().catch(() => ({}));

      if (response.ok) {
        experienceForm.reset();
        closeExperienceModal();
        showToast(
          "Berhasil",
          "Pengalaman baru berhasil ditambahkan!",
          "success",
        );
        await fetchExperiences();
      } else {
        const errorMessages = getFormErrorMessages(
          result,
          `Terjadi kesalahan (status ${response.status}).`,
        );
        showToast(
          "Gagal menambahkan pengalaman",
          errorMessages.join(" "),
          "error",
        );
      }
    } catch (error) {
      console.error("Error adding experience:", error);
      showToast(
        "Gagal menambahkan pengalaman",
        "Tidak dapat terhubung ke server. Silakan coba lagi.",
        "error",
      );
    } finally {
      submitButton.disabled = false;
    }
  }

  if (experienceForm) experienceForm.addEventListener("submit", addExperience);
  fetchExperiences();
}

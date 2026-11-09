const experienceApp = document.getElementById("experience-app");

if (experienceApp) {
  const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";
  const SEARCH_DEBOUNCE_DELAY = 300;
  const isAuthenticated = experienceApp.dataset.isAuthenticated === "true";
  const isSuperuser = experienceApp.dataset.isSuperuser === "true";
  const isEditor = experienceApp.dataset.isEditor === "true";

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
  const experienceEditForm = document.getElementById("experience-edit-form");
  const EDITABLE_FIELDS = ["title", "description", "category", "thumbnail", "ended_at"];

  // data terakhir dari API, dipakai untuk mengisi modal edit tanpa request tambahan
  const experienceCache = new Map();
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

  function buildExperienceCard(experience) {
    const experienceId = experience.id;
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

    const starTitle = experience.star_count > 0
      ? `Dibintangi oleh ${experience.starred_by_names}`
      : "Jadilah yang pertama memberi star";
    const starContent = `
      <span aria-hidden="true">★</span>
      ${experience.is_starred ? "Unstar" : "Star"}
      <span class="star-count">${experience.star_count}</span>`;
    const starHtml = isAuthenticated
      ? `<button type="button"
                 class="button button-star${experience.is_starred ? " is-starred" : ""}"
                 data-action="star"
                 data-id="${escapeHtml(experienceId)}"
                 title="${escapeHtml(starTitle)}">${starContent}</button>`
      : `<a href="${escapeHtml(experienceApp.dataset.loginUrl)}"
            class="button button-star"
            title="Login dulu untuk memberi star">${starContent}</a>`;

    let managementHtml = "";
    if (isSuperuser || isEditor) {
      managementHtml += `
        <button type="button"
                class="button"
                data-action="edit"
                data-id="${escapeHtml(experienceId)}"
                aria-label="Edit ${escapeHtml(experience.title)}">Edit</button>`;
      if (experience.is_ongoing) {
        managementHtml += `
        <button type="button"
                class="button button-secondary"
                data-action="finish"
                data-id="${escapeHtml(experienceId)}"
                aria-label="Tandai ${escapeHtml(experience.title)} selesai">Tandai selesai</button>`;
      }
    }
    if (isSuperuser) {
      managementHtml += `
        <button type="button"
                class="button button-danger"
                data-action="delete"
                data-id="${escapeHtml(experienceId)}"
                aria-label="Hapus ${escapeHtml(experience.title)}">Hapus</button>`;
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
      const category = item.category_display;
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
    const jsonParams = new URLSearchParams(queryString);
    jsonParams.set("format", "json");
    jsonLink.href = `${experienceApp.dataset.listEndpoint}?${jsonParams}`;
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
      experienceCache.clear();
      items.forEach((item) => experienceCache.set(item.id, item));
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

  groupsContainer.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;

    const action = button.dataset.action;
    const detailUrl = buildItemUrl(
      experienceApp.dataset.detailUrlTemplate,
      button.dataset.id,
    );
    if (action === "edit") {
      openEditModal(button.dataset.id);
      return;
    }
    if (action === "delete" && !window.confirm("Yakin ingin menghapus pengalaman ini?")) {
      return;
    }

    button.disabled = true;
    try {
      if (action === "star") {
        await sendJson(
          buildItemUrl(experienceApp.dataset.starUrlTemplate, button.dataset.id),
          "POST",
        );
      } else if (action === "finish") {
        // PATCH cukup mengirim satu field, field lain tidak disentuh
        await sendJson(detailUrl, "PATCH", { ended_at: new Date().toISOString() });
        showToast("Berhasil", "Pengalaman ditandai selesai.", "success");
      } else {
        await sendJson(detailUrl, "DELETE");
        showToast("Berhasil", "Pengalaman berhasil dihapus.", "success");
      }
      await fetchExperiences();
    } catch (error) {
      console.error("Error updating experience:", error);
      showToast("Permintaan gagal", error.message, "error");
      button.disabled = false;
    }
  });

  function closeExperienceModal(modalId = "add-experience-modal") {
    const modal = document.getElementById(modalId);
    if (modal && modal.matches(":popover-open")) modal.hidePopover();
  }

  // API mengirim waktu dalam UTC, sama seperti label "(UTC)" pada form
  function formValuesFrom(experience) {
    return {
      title: experience.title,
      description: experience.description,
      category: experience.category,
      thumbnail: experience.thumbnail ?? "",
      ended_at: experience.ended_at ? experience.ended_at.slice(0, 16) : "",
    };
  }

  function openEditModal(experienceId) {
    const experience = experienceCache.get(experienceId);
    const modal = document.getElementById("edit-experience-modal");
    if (!experience || !experienceEditForm || !modal) return;

    const values = formValuesFrom(experience);
    EDITABLE_FIELDS.forEach((name) => {
      experienceEditForm.elements[name].value = values[name];
    });
    experienceEditForm.dataset.id = experienceId;
    modal.showPopover();
  }

  async function saveExperience(event) {
    event.preventDefault();
    const experienceId = experienceEditForm.dataset.id;
    const original = formValuesFrom(experienceCache.get(experienceId));
    const fields = new FormData(experienceEditForm);

    // PATCH hanya mengirim field yang benar-benar berubah
    const changes = {};
    EDITABLE_FIELDS.forEach((name) => {
      if (fields.get(name) !== original[name]) changes[name] = fields.get(name);
    });
    if ("ended_at" in changes) changes.ended_at = changes.ended_at || null;

    if (Object.keys(changes).length === 0) {
      closeExperienceModal("edit-experience-modal");
      showToast("Tidak ada perubahan", "Belum ada data yang diubah.", "normal");
      return;
    }

    const submitButton = experienceEditForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
      await sendJson(
        buildItemUrl(experienceApp.dataset.detailUrlTemplate, experienceId),
        "PATCH",
        changes,
      );
      closeExperienceModal("edit-experience-modal");
      showToast("Berhasil", "Perubahan pengalaman disimpan.", "success");
      await fetchExperiences();
    } catch (error) {
      console.error("Error saving experience:", error);
      showToast("Gagal menyimpan perubahan", error.message, "error");
    } finally {
      submitButton.disabled = false;
    }
  }

  async function addExperience(event) {
    event.preventDefault();
    const submitButton = experienceForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
      const fields = new FormData(experienceForm);
      const payload = Object.fromEntries(
        EDITABLE_FIELDS.map((name) => [name, fields.get(name)]),
      );
      // input tanggal kosong harus dikirim sebagai null, bukan string kosong
      payload.ended_at = payload.ended_at || null;

      await sendJson(experienceApp.dataset.createEndpoint, "POST", payload);
      experienceForm.reset();
      closeExperienceModal();
      showToast("Berhasil", "Pengalaman baru berhasil ditambahkan!", "success");
      await fetchExperiences();
    } catch (error) {
      console.error("Error adding experience:", error);
      showToast("Gagal menambahkan pengalaman", error.message, "error");
    } finally {
      submitButton.disabled = false;
    }
  }

  if (experienceForm) experienceForm.addEventListener("submit", addExperience);
  if (experienceEditForm) experienceEditForm.addEventListener("submit", saveExperience);
  fetchExperiences();
}

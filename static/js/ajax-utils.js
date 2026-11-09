function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getCookie(name) {
  const prefix = `${name}=`;
  for (const item of document.cookie.split(";")) {
    const cookie = item.trim();
    if (cookie.startsWith(prefix)) {
      return decodeURIComponent(cookie.substring(prefix.length));
    }
  }
  return null;
}

function getFormErrorMessages(result, fallbackMessage) {
  if (!result.errors) return [result.message || fallbackMessage];
  return Object.values(result.errors)
    .flat()
    .map((error) => error.message);
}

// error validasi DRF berbentuk {"title": ["..."]}, error umum {"detail": "..."}
function apiErrorMessage(data, status) {
  const messages = Object.values(data)
    .flat()
    .filter((value) => typeof value === "string");
  return messages.join(" ") || `Permintaan gagal (HTTP ${status}).`;
}

async function sendJson(url, method, payload) {
  const response = await fetch(url, {
    method,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
  return data;
}

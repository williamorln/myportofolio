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

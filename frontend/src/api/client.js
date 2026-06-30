export async function fetchJson(url, options = {}) {
  const headers = options.body instanceof FormData
    ? { ...(options.headers ?? {}) }
    : {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      };

  const response = await fetch(url, {
    headers,
    ...options,
  });

  if (!response.ok) {
    throw new Error(`${response.status}: ${await getErrorDetail(response)}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function fetchBlob(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new Error(`${response.status}: ${await getErrorDetail(response)}`);
  }

  return response.blob();
}

async function getErrorDetail(response) {
  try {
    const body = await response.json();
    return formatDetail(body.detail ?? response.statusText);
  } catch {
    return response.statusText;
  }
}

function formatDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }

  if (detail && typeof detail === "object" && typeof detail.message === "string") {
    return detail.message;
  }

  return JSON.stringify(detail);
}

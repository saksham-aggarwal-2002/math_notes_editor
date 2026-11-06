// Calls to the server. Every function throws an Error with the server's message.

export const enc = encodeURIComponent;

export async function api(method, url, body) {
    const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        const detail = typeof error.detail === "string" ? error.detail : "Request failed.";
        throw new Error(detail);
    }

    return response.json();
}

export const subjectUrl = (subject) => `/api/subjects/${enc(subject)}`;
export const noteUrl = (subject, note) => `${subjectUrl(subject)}/notes/${enc(note)}`;

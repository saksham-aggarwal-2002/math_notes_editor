// What the page is showing. The server keeps none of this.

export const state = {
    subject: null,
    note: null,
    notes: [],
    jupyterOrigin: null,
    positions: {},   // scroll positions by key, mirrored in app_data/config.json
};

export const $ = (id) => document.getElementById(id);

/** Remember where you were (a note's scroll, a book's PDF location); survives restarts. */
export function savePosition(key, value) {
    state.positions[key] = value;
    fetch("/api/positions", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
    });
}

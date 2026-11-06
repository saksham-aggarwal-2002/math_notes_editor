// The rendered note beside the editor. The server renders after every save; this reloads
// the preview when the rendered file changes, keeping the scroll position.
import { api, enc, noteUrl } from "./api.js";
import { state, $ } from "./state.js";

const frame = $("quarto-frame");

let lastModified = 0;
let generation = 0;   // bumped on every note switch, so an old poll stops
let pollingGeneration = null;   // the note switch the running poll belongs to

const previewUrl = () =>
    `/files/${enc(state.subject)}/notes/${enc(state.note.replace(/\.qmd$/, ".html"))}?t=${Date.now()}`;

function reload() {
    let x = 0;
    let y = 0;

    try {
        x = frame.contentWindow.scrollX;
        y = frame.contentWindow.scrollY;
    } catch (error) { /* the frame is empty */ }

    frame.onload = () => {
        try { frame.contentWindow.scrollTo(x, y); } catch (error) { /* ignore */ }
    };
    frame.src = previewUrl();
}

async function poll(myGeneration) {
    if (pollingGeneration === myGeneration) return;
    pollingGeneration = myGeneration;

    try {
        for (let i = 0; i < 120 && myGeneration === generation; i++) {
            const status = await api("GET", `${noteUrl(state.subject, state.note)}/preview`);

            if (myGeneration !== generation) return;

            if (status.modified !== lastModified) {
                lastModified = status.modified;
                reload();
            }

            if (!status.rendering) return;

            await new Promise((resolve) => setTimeout(resolve, 500));
        }
    } catch (error) {
        console.log("Could not check the preview.", error);
    } finally {
        if (pollingGeneration === myGeneration) pollingGeneration = null;
    }
}

/** Show the note's rendered page (and follow it while it is being rendered). */
export async function load() {
    generation++;
    lastModified = 0;
    frame.onload = null;
    frame.src = "about:blank";
    const myGeneration = generation;

    try {
        const status = await api("GET", `${noteUrl(state.subject, state.note)}/preview`);

        if (myGeneration !== generation) return;

        lastModified = status.modified;

        if (status.modified) reload();
        if (status.rendering || !status.modified) poll(myGeneration);
    } catch (error) {
        console.log("Could not load the preview.", error);
    }
}

/** A save was sent: watch for the new render. */
export function watch() {
    poll(generation);
}

export function clear() {
    generation++;
    frame.onload = null;
    frame.src = "about:blank";
}

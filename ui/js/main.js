// Startup, the toolbar, subject/note selection and keyboard shortcuts.
import { api, subjectUrl } from "./api.js";
import { state, $ } from "./state.js";
import * as notes from "./notes.js";
import * as python from "./python.js";
import * as images from "./images.js";
import * as settings from "./settings.js";

const VIEWS = ["notes", "python", "settings"];
let view = "notes";

function showView(name) {
    view = name;

    $("notes-view").style.display = name === "notes" ? "flex" : "none";
    $("python-view").style.display = name === "python" ? "block" : "none";
    $("settings-view").style.display = name === "settings" ? "block" : "none";

    for (const other of VIEWS) $(`${other}-button`).classList.toggle("active", other === name);

    if (name === "notes") notes.refresh();
    if (name === "python") python.show();
    if (name === "settings") settings.show();
}

function fillSelect(id, options, selected, emptyText) {
    const select = $(id);
    select.innerHTML = "";

    for (const option of options) {
        const element = document.createElement("option");
        element.value = option;
        element.textContent = option.replace(/\.qmd$/, "");
        element.selected = option === selected;
        select.appendChild(element);
    }

    if (options.length === 0) {
        const element = document.createElement("option");
        element.textContent = emptyText;
        select.appendChild(element);
    }

    select.disabled = options.length === 0;
}

const remember = () => api("PUT", "/api/session", { subject: state.subject, note: state.note });

async function selectNote(note) {
    if (!state.notes.includes(note)) return;

    await notes.flushSave();
    state.note = note;
    fillSelect("note-select", state.notes, note, "No notes in this subject yet");
    await notes.loadNote();
    remember();
}

async function selectSubject(subject, preferredNote) {
    await notes.flushSave();

    state.subject = subject;
    python.reset();

    state.notes = subject === null ? [] : (await api("GET", subjectUrl(subject))).notes;
    state.note = state.notes.includes(preferredNote) ? preferredNote : (state.notes[0] ?? null);

    fillSelect("note-select", state.notes, state.note, "No notes in this subject yet");

    await notes.loadNote();
    remember();

    if (view === "python") python.show();
}

function attempt(action) {
    return (...args) => action(...args).catch((error) => alert(error.message));
}

$("notes-button").onclick = () => showView("notes");
$("python-button").onclick = () => showView("python");
$("settings-button").onclick = () => showView("settings");
$("subject-select").onchange = attempt((event) => selectSubject(event.target.value));
$("note-select").onchange = attempt((event) => selectNote(event.target.value));

document.addEventListener("keydown", (event) => {
    if (!event.metaKey || !event.shiftKey) return;

    const key = event.key.toLowerCase();
    const actions = {
        l: () => (view === "notes" ? notes.aiAtCursor() : view === "python" ? python.openPrompt() : null),
        p: () => view === "notes" && notes.insertPlaceholder(),
        o: () => view === "notes" && notes.addExampleReference(),
        i: () => view === "notes" && images.open(),
    };

    if (actions[key]) {
        event.preventDefault();
        actions[key]();
    }
});

async function start() {
    notes.initEditor();

    const info = await api("GET", "/api/state");
    state.jupyterOrigin = info.jupyterOrigin;

    fillSelect("subject-select", info.subjects, info.session.subject, "No subjects found");

    await selectSubject(info.session.subject, info.session.note);
}

start().catch((error) => alert(error.message));

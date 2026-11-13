// Startup, the toolbar, subject/note selection and keyboard shortcuts.
import { api, subjectUrl } from "./api.js";
import { state, $ } from "./state.js";
import * as notes from "./notes.js";
import { fillTabs } from "./tabs.js";
import * as books from "./books.js";
import * as python from "./python.js";
import * as images from "./images.js";
import * as settings from "./settings.js";

const VIEWS = ["notes", "python", "books", "settings"];
let view = "notes";

function showView(name) {
    view = name;

    $("notes-view").style.display = name === "notes" ? "flex" : "none";
    $("python-view").style.display = name === "python" ? "block" : "none";
    $("books-view").style.display = name === "books" ? "flex" : "none";
    $("settings-view").style.display = name === "settings" ? "block" : "none";

    for (const other of VIEWS) $(`${other}-button`).classList.toggle("active", other === name);

    if (name === "notes") notes.refresh();
    if (name === "python") python.show();
    if (name === "books") books.show();
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

const showNoteTabs = () =>
    fillTabs($("note-tabs"), state.notes, state.note, "No notes in this subject yet", attempt(selectNote));

const remember = () => api("PUT", "/api/session", { subject: state.subject, note: state.note });

async function selectNote(note) {
    if (!state.notes.includes(note)) return;

    await notes.flushSave();
    state.note = note;
    showNoteTabs();
    await notes.loadNote();
    remember();
}

async function selectSubject(subject, preferredNote) {
    await notes.flushSave();

    state.subject = subject;
    python.reset();
    books.reset();

    state.notes = subject === null ? [] : (await api("GET", subjectUrl(subject))).notes;
    state.note = state.notes.includes(preferredNote) ? preferredNote : (state.notes[0] ?? null);

    showNoteTabs();

    await notes.loadNote();
    remember();

    if (view === "python") python.show();
    if (view === "books") books.show();
}

function attempt(action) {
    return (...args) => action(...args).catch((error) => alert(error.message));
}

$("notes-button").onclick = () => showView("notes");
$("python-button").onclick = () => showView("python");
$("books-button").onclick = () => showView("books");
$("settings-button").onclick = () => showView("settings");
$("subject-select").onchange = attempt((event) => selectSubject(event.target.value));

function switchView(step) {
    showView(VIEWS[(VIEWS.indexOf(view) + step + VIEWS.length) % VIEWS.length]);
}

// Ctrl+Option+Left/Right pressed inside Jupyter is forwarded by the extension.
window.addEventListener("message", (event) => {
    if (event.origin === state.jupyterOrigin && event.data?.type === "math_notes_editor-switch-tab") {
        switchView(event.data.step);
    }
});

function switchTab(delta) {
    if (view === "books") return books.step(delta);

    const { notes: names, note } = state;

    if (view === "notes" && names.length > 1) {
        attempt(selectNote)(names[(names.indexOf(note) + delta + names.length) % names.length]);
    }
}

document.addEventListener("keydown", (event) => {
    if (event.altKey && event.ctrlKey && !event.metaKey && !event.shiftKey) {
        const step = { ArrowLeft: -1, ArrowRight: 1 }[event.code];   // between Notes, Experiments, ...
        const delta = { ArrowUp: -1, ArrowDown: 1 }[event.code];     // between notes / books

        if (step || delta) {
            event.preventDefault();
            if (step) switchView(step);
            else switchTab(delta);
        }
        return;
    }

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
}, true);

async function start() {
    notes.initEditor();

    const info = await api("GET", "/api/state");
    state.jupyterOrigin = info.jupyterOrigin;
    state.positions = info.positions;

    fillSelect("subject-select", info.subjects, info.session.subject, "No subjects found");

    await selectSubject(info.session.subject, info.session.note);
}

start().catch((error) => alert(error.message));

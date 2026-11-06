// The Markdown editor: loading, folding, autosave, and the helpers that insert text.
import { api, noteUrl, subjectUrl } from "./api.js";
import { state, $ } from "./state.js";
import { askForText, askForReference } from "./prompt.js";
import * as preview from "./preview.js";

const AI_MARKER = "<!-- AI_GENERATING -->";
const SAVE_DELAY_MS = 500;

let editor;
let saveTimer = null;
let pendingSave = null;   // {subject, note, content} waiting for the timer
let loading = false;

/* Folding: ::: boxes and headings. */
CodeMirror.registerHelper("fold", "quarto", (cm, start) => {
    const line = start.line;
    const text = cm.getLine(line);
    const lastLine = cm.lineCount() - 1;

    if (/^\s*:::\s*/.test(text)) {
        for (let i = line + 1; i <= lastLine; i++) {
            if (/^\s*:::\s*$/.test(cm.getLine(i))) {
                return {
                    from: CodeMirror.Pos(line, text.length),
                    to: CodeMirror.Pos(i, cm.getLine(i).length),
                };
            }
        }
        return;
    }

    const heading = text.match(/^\s*(#{1,6})\s+/);

    if (heading) {
        let end = lastLine;

        for (let i = line + 1; i <= lastLine; i++) {
            const next = cm.getLine(i).match(/^\s*(#{1,6})\s+/);

            if (next && next[1].length <= heading[1].length) {
                end = i - 1;
                break;
            }
        }

        return {
            from: CodeMirror.Pos(line, text.length),
            to: CodeMirror.Pos(end, cm.getLine(end).length),
        };
    }
});

export function initEditor() {
    editor = CodeMirror.fromTextArea($("editor"), {
        mode: "markdown",
        lineNumbers: true,
        lineWrapping: true,
        foldGutter: { rangeFinder: (cm, start) => CodeMirror.fold.quarto(cm, start) },
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    });

    editor.on("change", () => {
        if (!loading) scheduleSave();
    });
}

export const refresh = () => editor.refresh();
export const focus = () => editor.focus();

export function insertAtCursor(text) {
    editor.replaceRange(text, editor.getCursor());
}

/* Loading and saving. Each save names its own subject and note, so a late save can
   never land in a note that has since been switched to. */

export async function loadNote() {
    loading = true;

    try {
        if (state.note === null) {
            editor.setValue("");
            editor.setOption("readOnly", "nocursor");
            preview.clear();
            return;
        }

        const { content } = await api("GET", noteUrl(state.subject, state.note));

        editor.setOption("readOnly", false);
        editor.setValue(content);
        editor.clearHistory();

        for (let i = 0; i < editor.lineCount(); i++) {
            if (/^#\s+/.test(editor.getLine(i))) editor.foldCode(CodeMirror.Pos(i, 0));
        }
    } finally {
        loading = false;
    }

    if (state.note !== null) preview.load();
}

function scheduleSave() {
    clearTimeout(saveTimer);
    pendingSave = { subject: state.subject, note: state.note, content: editor.getValue() };
    saveTimer = setTimeout(flushSave, SAVE_DELAY_MS);
}

/** Send any edit that is still waiting. Call before switching subject or note. */
export async function flushSave() {
    clearTimeout(saveTimer);
    const save = pendingSave;
    pendingSave = null;

    if (!save) return;

    try {
        await api("PUT", noteUrl(save.subject, save.note), { content: save.content });
        if (save.subject === state.subject && save.note === state.note) preview.watch();
    } catch (error) {
        alert("Could not save: " + error.message);
    }
}

/* Inserting text. */

export function insertPlaceholder() {
    const cursor = editor.getCursor();

    editor.replaceRange(
        '::: {.box}\n\n[content describing the placeholder]{style="color: red;"}.\n\n:::\n',
        cursor
    );
    editor.setCursor({ line: cursor.line + 2, ch: 1 });
    editor.focus();
}

export function addExampleReference() {
    askForReference((heading, tag) => {
        insertAtCursor(`See [${heading}](#${tag})`);

        const lastLine = editor.lineCount() - 1;
        editor.replaceRange(
            `\n\n### ${heading}  {#${tag}}\n`,
            CodeMirror.Pos(lastLine, editor.getLine(lastLine).length)
        );
        editor.focus();
    });
}

/** Ask for a request and insert the AI's answer at the cursor. */
export function aiAtCursor() {
    askForText("What should I insert?", async (request) => {
        const subject = state.subject;

        insertAtCursor(AI_MARKER);
        editor.focus();

        const replaceMarker = (text) => {
            const at = editor.getValue().indexOf(AI_MARKER);

            if (at === -1) return;

            editor.replaceRange(text, editor.posFromIndex(at), editor.posFromIndex(at + AI_MARKER.length));
        };

        try {
            const { content } = await api("POST", `${subjectUrl(subject)}/ai/quarto`, {
                content: editor.getValue(),
                request,
            });
            replaceMarker(content);
        } catch (error) {
            replaceMarker("");
            alert("AI generation failed: " + error.message);
        }
    });
}

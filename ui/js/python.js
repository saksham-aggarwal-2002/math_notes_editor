// The Python tab: JupyterLab in an iframe, started for the current subject on first use,
// plus the AI shortcut. The extension in Jupyter (jupyter_extension/) speaks the messages below.
import { api, subjectUrl } from "./api.js";
import { state, $ } from "./state.js";
import { askForText } from "./prompt.js";

const frame = $("jupyter-frame");
const message = $("python-message");

let shownFor = null;

function showMessage(text) {
    frame.style.display = "none";
    message.style.display = "block";
    message.textContent = text;
}

/** Call when the Python tab is opened. */
export async function show() {
    const subject = state.subject;

    if (subject === null) return showMessage("No subject is selected.");
    if (shownFor === subject) return;

    shownFor = subject;
    showMessage("Starting Python...");

    try {
        const result = await api("POST", `${subjectUrl(subject)}/jupyter`);

        if (shownFor !== subject) return;   // switched subject meanwhile

        if (!result.available) {
            shownFor = null;
            return showMessage("Python is unavailable: " + result.reason);
        }

        message.style.display = "none";
        frame.style.display = "block";
        frame.src = state.jupyterOrigin + "/lab";
    } catch (error) {
        shownFor = null;
        showMessage("Python is unavailable: " + error.message);
    }
}

/** Call when the subject changes: Jupyter will be restarted for the new one on next visit. */
export function reset() {
    shownFor = null;
    frame.src = "about:blank";
}

const post = (payload) => frame.contentWindow.postMessage(payload, state.jupyterOrigin);

/** Ask for a request, then fill a new cell below the active one with generated code. */
export function openPrompt(requestId = crypto.randomUUID(), notebookPath = null) {
    askForText("What Python code should I insert?", async (request) => {
        post({ type: "math_notes_editor-create-placeholder", requestId });

        try {
            const { content } = await api("POST", `${subjectUrl(state.subject)}/ai/python`, {
                notebook: notebookPath,
                request,
            });

            if (!content) throw new Error("AI returned no content.");

            post({ type: "math_notes_editor-insert-text", text: content, requestId });
        } catch (error) {
            alert("AI generation failed: " + error.message);
        }
    });
}

// Cmd+Shift+L pressed inside Jupyter is forwarded by the extension.
window.addEventListener("message", (event) => {
    if (event.origin !== state.jupyterOrigin) return;
    if (!event.data || event.data.type !== "math_notes_editor-open-python-prompt") return;

    openPrompt(event.data.requestId, event.data.notebookPath);
});

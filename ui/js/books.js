// The Books tab: the PDFs in the subject's books/ folder, one at a time in the browser's PDF viewer.
import { api, subjectUrl } from "./api.js";
import { state, $, savePosition } from "./state.js";
import { fillTabs } from "./tabs.js";

const tabs = $("book-tabs");
const frame = $("book-frame");
const message = $("books-message");

let shownFor = null;
let current = { book: null, books: [] };

function showMessage(text) {
    frame.style.display = "none";
    message.style.display = "block";
    message.textContent = text;
}

const bookKey = (book) => `${state.subject}/books/${book}`;

/** Remember the page and zoom of the PDF viewer as you scroll, keyed by the book it shows. */
function trackPosition(key) {
    frame.onload = async () => {
        // Keys pressed inside the PDF viewer never reach the page, so pass the tab shortcut on.
        // Capture phase, so the viewer's own key handling can't swallow it first.
        frame.contentWindow.addEventListener("keydown", (event) => {
            if (event.altKey && event.ctrlKey && event.code.startsWith("Arrow")) {
                event.preventDefault();
                event.stopPropagation();
                document.dispatchEvent(new KeyboardEvent("keydown", {
                    code: event.code, key: event.key, altKey: true, ctrlKey: true,
                }));
            }
        }, true);

        const app = frame.contentWindow.PDFViewerApplication;

        if (!app) return;

        await app.initializedPromise;

        app.eventBus.on("updateviewarea", (event) => {
            if (frame.dataset.key === key) savePosition(key, event.location.pdfOpenParams);
        });
    };
}

function open(book, books) {
    const key = bookKey(book);
    const file = `/files/${encodeURIComponent(state.subject)}/books/${encodeURIComponent(book)}`;
    const where = state.positions[key] ?? "";   // like "#page=12&zoom=auto,-1,300"

    current = { book, books };
    fillTabs(tabs, books, book, "", (name) => open(name, books));
    savePosition(`${state.subject}/last-book`, book);

    message.style.display = "none";
    frame.style.display = "block";
    frame.dataset.key = key;
    trackPosition(key);
    frame.src = `/vendor/pdfjs/web/viewer.html?file=${encodeURIComponent(file)}${where}`;
}

/** Call when the Books tab is opened. */
export async function show() {
    const subject = state.subject;

    if (subject === null) return showMessage("No subject is selected.");
    if (shownFor === subject) return;

    const { books } = await api("GET", `${subjectUrl(subject)}/books`);

    if (state.subject !== subject) return;   // switched subject meanwhile

    shownFor = subject;
    if (books.length === 0) {
        fillTabs(tabs, [], null, "No books", () => {});
        return showMessage("No PDFs in this subject's books folder.");
    }

    const last = state.positions[`${subject}/last-book`];

    open(books.includes(last) ? last : books[0], books);
}

/** Switch to the next (1) or previous (-1) book, wrapping around. */
export function step(delta) {
    const { book, books } = current;

    if (books.length > 1) open(books[(books.indexOf(book) + delta + books.length) % books.length], books);
}

/** Call when the subject changes: the list is reloaded on next visit. */
export function reset() {
    shownFor = null;
    current = { book: null, books: [] };
    frame.dataset.key = "";
    frame.src = "about:blank";
}

// Cmd+Shift+I: pick one of the subject's images and insert it at the cursor.
import { api, enc, subjectUrl } from "./api.js";
import { state, $ } from "./state.js";
import { insertAtCursor, focus } from "./notes.js";

const picker = $("image-picker");
const search = $("image-search");
const list = $("image-list");

let all = [];
let shown = [];
let selected = 0;

export async function open() {
    picker.style.display = "block";
    search.value = "";
    selected = 0;

    try {
        all = await api("GET", `${subjectUrl(state.subject)}/images`);
        shown = [...all];
        render();
        search.focus();
    } catch (error) {
        alert("Could not load images: " + error.message);
        close();
    }
}

function close() {
    picker.style.display = "none";
}

function insert(image) {
    insertAtCursor(`::: {.text-center}\n![](images/${image.name})\n:::\n`);
    close();
    focus();
}

function render() {
    list.innerHTML = "";

    if (shown.length === 0) {
        const empty = document.createElement("div");
        empty.style.padding = "20px";
        empty.style.color = "#777";
        empty.textContent = "No images found.";
        list.appendChild(empty);
        return;
    }

    shown.forEach((image, index) => {
        const item = document.createElement("div");
        item.className = "image-item" + (index === selected ? " selected" : "");

        const thumbnail = document.createElement("img");
        thumbnail.className = "image-thumbnail";
        thumbnail.src = `/files/${enc(state.subject)}/notes/images/${enc(image.name)}`;

        const name = document.createElement("div");
        name.className = "image-name";
        name.textContent = image.name;

        item.append(thumbnail, name);
        item.onclick = () => insert(image);
        list.appendChild(item);
    });
}

function move(step) {
    if (shown.length === 0) return;

    selected = Math.max(0, Math.min(selected + step, shown.length - 1));
    render();

    const item = document.querySelector(".image-item.selected");
    if (item) item.scrollIntoView({ block: "nearest" });
}

search.addEventListener("input", () => {
    const query = search.value.toLowerCase().trim();
    shown = all.filter((image) => image.name.toLowerCase().includes(query));
    selected = 0;
    render();
});

search.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        event.preventDefault();
        close();
        focus();
    } else if (event.key === "ArrowDown") {
        event.preventDefault();
        move(1);
    } else if (event.key === "ArrowUp") {
        event.preventDefault();
        move(-1);
    } else if (event.key === "Enter") {
        event.preventDefault();
        if (shown.length) insert(shown[selected]);
    }
});

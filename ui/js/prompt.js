// The small box over the page: one text field for AI requests, or heading + tag for references.
import { $ } from "./state.js";

const box = $("ai-prompt");
const input = $("ai-request");
const referenceFields = $("reference-fields");
const heading = $("reference-heading");
const tag = $("reference-tag");

let submitText = null;
let submitReference = null;

function close() {
    box.style.display = "none";
    referenceFields.style.display = "none";
    input.style.display = "block";
    submitText = null;
    submitReference = null;
}

export function askForText(placeholder, onSubmit) {
    submitText = onSubmit;
    box.style.display = "block";
    input.style.display = "block";
    input.value = "";
    input.placeholder = placeholder;
    input.focus();
}

export function askForReference(onSubmit) {
    submitReference = onSubmit;
    box.style.display = "block";
    input.style.display = "none";
    referenceFields.style.display = "block";
    heading.value = "";
    tag.value = "";
    heading.focus();
}

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        const text = input.value.trim();
        const submit = submitText;

        if (text && submit) {
            close();
            submit(text);
        }
    }

    if (event.key === "Escape") {
        close();
    }
});

function referenceKey(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        const headingText = heading.value.trim();
        const tagText = tag.value.trim();
        const submit = submitReference;

        if (headingText && tagText && submit) {
            close();
            submit(headingText, tagText);
        }
    }

    if (event.key === "Escape") {
        event.preventDefault();
        close();
    }
}

heading.addEventListener("keydown", referenceKey);
tag.addEventListener("keydown", referenceKey);

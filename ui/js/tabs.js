// A row of tabs, one per name (note or book), with the selected one highlighted.

/** Fill `container` with a tab per name; clicking one calls onSelect(name). */
export function fillTabs(container, names, selected, emptyText, onSelect) {
    container.innerHTML = "";

    for (const name of names) {
        const tab = document.createElement("button");
        tab.className = "file-tab" + (name === selected ? " active" : "");
        tab.textContent = name.replace(/\.(qmd|pdf)$/i, "");
        tab.title = tab.textContent;
        tab.onclick = () => onSelect(name);
        container.appendChild(tab);
    }

    if (names.length === 0) {
        const empty = document.createElement("span");
        empty.className = "file-tabs-empty";
        empty.textContent = emptyText;
        container.appendChild(empty);
    }
}

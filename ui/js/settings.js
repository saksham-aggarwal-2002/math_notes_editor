// The Settings tab: where the data lives.
import { api } from "./api.js";
import { $ } from "./state.js";

export async function show() {
    const info = await api("GET", "/api/state");

    $("settings-data-folder").textContent = info.dataFolder;
    $("settings-app-data").textContent = info.appDataDir;
}

for (const button of document.querySelectorAll(".open-folder")) {
    button.onclick = () =>
        api("POST", "/api/open-folder", { which: button.dataset.folder }).catch((error) => alert(error.message));
}

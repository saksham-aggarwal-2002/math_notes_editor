// What the page is showing. The server keeps none of this.

export const state = {
    subject: null,
    note: null,
    notes: [],
    jupyterOrigin: null,
};

export const $ = (id) => document.getElementById(id);

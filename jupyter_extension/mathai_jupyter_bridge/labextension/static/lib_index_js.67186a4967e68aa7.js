"use strict";
(self["rspackChunkmathai_jupyter_bridge"] = self["rspackChunkmathai_jupyter_bridge"] || []).push([["lib_index_js"], {
"./lib/index.js"(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_notebook__rspack_import_0 = __webpack_require__("webpack/sharing/consume/default/@jupyterlab/notebook");
/* import */ var _jupyterlab_notebook__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__rspack_import_0);

const MATHAI_ORIGIN = 'http://127.0.0.1:8000';
function sendToMathAI(response) {
    window.parent.postMessage(response, MATHAI_ORIGIN);
}
const plugin = {
    id: 'mathai-jupyter-bridge',
    description: 'Bridge between MathAI and JupyterLab.',
    autoStart: true,
    requires: [_jupyterlab_notebook__rspack_import_0.INotebookTracker],
    activate: (app, tracker) => {
        console.log('MathAI Jupyter bridge loaded.');
        /*
         * Cmd+Shift+L
         *
         * Listen during the capture phase so that
         * JupyterLab's own keyboard handling does not
         * prevent us from seeing the event.
         */
        document.addEventListener('keydown', event => {
            if (event.metaKey &&
                event.shiftKey &&
                event.key.toLowerCase() === 'l') {
                event.preventDefault();
                event.stopPropagation();
                window.parent.postMessage({
                    type: 'mathai-open-python-prompt'
                }, MATHAI_ORIGIN);
            }
        }, true);
        /*
         * Listen for commands from MathAI.
         */
        window.addEventListener('message', event => {
            if (event.origin !== MATHAI_ORIGIN) {
                return;
            }
            const message = event.data;
            if (!message ||
                message.type !==
                    'mathai-insert-text') {
                return;
            }
            try {
                if (typeof message.text !==
                    'string') {
                    throw new Error('No text was provided.');
                }
                const panel = tracker.currentWidget;
                if (!panel) {
                    throw new Error('No notebook is currently open.');
                }
                const notebook = panel.content;
                if (notebook.activeCellIndex < 0) {
                    throw new Error('No active cell.');
                }
                /*
                 * Create a new code cell immediately
                 * below the active cell.
                 */
                _jupyterlab_notebook__rspack_import_0.NotebookActions.insertBelow(notebook);
                const newCell = notebook.activeCell;
                if (!newCell) {
                    throw new Error('Could not access the new cell.');
                }
                newCell.model.sharedModel.setSource(message.text);
                sendToMathAI({
                    type: 'mathai-insert-result',
                    success: true
                });
            }
            catch (error) {
                console.error('MathAI insertion failed:', error);
                sendToMathAI({
                    type: 'mathai-insert-result',
                    success: false,
                    error: String(error)
                });
            }
        });
    }
};
/* export default */ const __rspack_default_export = (plugin);


},

}]);
//# sourceMappingURL=lib_index_js.67186a4967e68aa7.js.map
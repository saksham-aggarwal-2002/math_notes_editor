import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  INotebookTracker,
  NotebookActions
} from '@jupyterlab/notebook';


interface MathAIMessage {
  type: string;
  text?: string;
  requestId?: string;
}


interface MathAIResponse {
  type: string;
  success: boolean;
  error?: string;
  requestId?: string;
}


const MATHAI_ORIGIN = 'http://127.0.0.1:8000';


function sendToMathAI(response: MathAIResponse): void {

  window.parent.postMessage(
    response,
    MATHAI_ORIGIN
  );

}


const plugin: JupyterFrontEndPlugin<void> = {

  id: 'mathai-jupyter-bridge',

  description:
    'Bridge between MathAI and JupyterLab.',

  autoStart: true,

  requires: [INotebookTracker],


  activate: (
    app: JupyterFrontEnd,
    tracker: INotebookTracker
  ) => {


    console.log(
      'MathAI Jupyter bridge loaded.'
    );


    /*
     * Store the cell that initiated each AI request.
     *
     * The cell object itself is stored rather than its
     * index, because cells can be inserted or deleted
     * while the AI request is running.
     */

    const pendingCells =
      new Map<string, any>();


    /*
     * Cmd+Shift+L
     */

    document.addEventListener(
      'keydown',
      event => {

        if (
          event.metaKey &&
          event.shiftKey &&
          event.key.toLowerCase() === 'l'
        ) {

          event.preventDefault();

          event.stopPropagation();


          try {

            const panel =
              tracker.currentWidget;


            if (!panel) {

              console.error(
                'MathAI: no notebook is open.'
              );

              return;

            }


            const notebook =
              panel.content;


            const cell =
              notebook.activeCell;


            if (!cell) {

              console.error(
                'MathAI: no active cell.'
              );

              return;

            }


            const requestId =
              crypto.randomUUID();


            pendingCells.set(
              requestId,
              cell
            );


            window.parent.postMessage(
              {
                type:
                  'mathai-open-python-prompt',

                requestId:
                  requestId
              },
              MATHAI_ORIGIN
            );


          } catch (error) {

            console.error(
              'MathAI: could not prepare AI request:',
              error
            );

          }

        }

      },
      true
    );


    /*
     * Listen for commands from MathAI.
     */

    window.addEventListener(
      'message',
      event => {

        if (
          event.origin !== MATHAI_ORIGIN
        ) {

          return;

        }


        const message =
          event.data as MathAIMessage;


        if (!message) {

          return;

        }


        /*
         * Insert AI-generated Python below the
         * cell that originally started the request.
         */

        if (
          message.type ===
          'mathai-insert-text'
        ) {

          const requestId =
            message.requestId;


          if (!requestId) {

            sendToMathAI({

              type:
                'mathai-insert-result',

              success:
                false,

              error:
                'No request ID was provided.'

            });

            return;

          }


          const originalCell =
            pendingCells.get(
              requestId
            );


          pendingCells.delete(
            requestId
          );


          if (!originalCell) {

            sendToMathAI({

              type:
                'mathai-insert-result',

              success:
                false,

              requestId:
                requestId,

              error:
                'The original notebook cell could not be found.'

            });

            return;

          }


          try {

            if (
              typeof message.text !==
              'string'
            ) {

              throw new Error(
                'No text was provided.'
              );

            }


            const panel =
              tracker.currentWidget;


            if (!panel) {

              throw new Error(
                'No notebook is currently open.'
              );

            }


            const notebook =
              panel.content;


            /*
             * Find the original cell again.
             *
             * This gives us its current position even
             * if cells were added while the AI request
             * was running.
             */

            const cellIndex =
              notebook.widgets.indexOf(
                originalCell
              );


            if (cellIndex < 0) {

              throw new Error(
                'The original cell no longer exists.'
              );

            }


            /*
             * Make the original cell active.
             *
             * NotebookActions.insertBelow()
             * inserts relative to the active cell.
             */

            notebook.activeCellIndex =
              cellIndex;


            NotebookActions.insertBelow(
              notebook
            );


            const newCell =
              notebook.activeCell;


            if (!newCell) {

              throw new Error(
                'Could not access the new cell.'
              );

            }


            newCell.model.sharedModel.setSource(
              message.text
            );


            sendToMathAI({

              type:
                'mathai-insert-result',

              success:
                true,

              requestId:
                requestId

            });


          } catch (error) {

            console.error(
              'MathAI insertion failed:',
              error
            );


            sendToMathAI({

              type:
                'mathai-insert-result',

              success:
                false,

              requestId:
                requestId,

              error:
                String(error)

            });

          }


          return;

        }


      }
    );

  }

};


export default plugin;
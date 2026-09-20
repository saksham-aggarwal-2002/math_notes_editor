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
     * Store the placeholder cell associated
     * with each AI request.
     *
     * The cell object is stored rather than
     * its index, because cells can be inserted
     * or deleted while the AI request is running.
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


            /*
             * Make sure the current cell is active.
             */

            notebook.activeCellIndex =
              notebook.widgets.indexOf(cell);


            /*
             * Immediately create a new cell below
             * the current cell.
             */

            NotebookActions.insertBelow(
              notebook
            );


            const placeholderCell =
              notebook.activeCell;


            if (!placeholderCell) {

              console.error(
                'MathAI: could not create placeholder cell.'
              );

              return;

            }


            /*
             * Show the placeholder while the AI
             * request is running.
             */

            placeholderCell.model.sharedModel.setSource(
              '<!-- AI_GENERATING -->'
            );


            /*
             * Store the placeholder cell itself.
             *
             * This lets us replace exactly this cell
             * when the AI response arrives, regardless
             * of what happens to the notebook in the
             * meantime.
             */

            pendingCells.set(
              requestId,
              placeholderCell
            );


            /*
             * Tell the parent MathAI application
             * to open the Python prompt.
             */

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
         * Replace the placeholder cell with
         * AI-generated Python.
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


          const placeholderCell =
            pendingCells.get(
              requestId
            );


          pendingCells.delete(
            requestId
          );


          if (!placeholderCell) {

            sendToMathAI({

              type:
                'mathai-insert-result',

              success:
                false,

              requestId:
                requestId,

              error:
                'The AI placeholder cell could not be found.'

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


            /*
             * Replace the placeholder with
             * the generated Python.
             */

            placeholderCell.model.sharedModel.setSource(
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
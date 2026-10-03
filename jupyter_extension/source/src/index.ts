import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  INotebookTracker,
  NotebookActions
} from '@jupyterlab/notebook';


interface MathNotesEditorMessage {
  type: string;
  text?: string;
  requestId?: string;
}


interface MathNotesEditorResponse {
  type: string;
  success: boolean;
  error?: string;
  requestId?: string;
}


const MATH_NOTES_EDITOR_ORIGIN = 'http://127.0.0.1:8000';


function sendToMathNotesEditor(response: MathNotesEditorResponse): void {

  window.parent.postMessage(
    response,
    MATH_NOTES_EDITOR_ORIGIN
  );

}


const plugin: JupyterFrontEndPlugin<void> = {

  id: 'math_notes_editor-jupyter-bridge',

  description:
    'Bridge between math_notes_editor and JupyterLab.',

  autoStart: true,

  requires: [INotebookTracker],


  activate: (
    app: JupyterFrontEnd,
    tracker: INotebookTracker
  ) => {


    console.log(
      'math_notes_editor Jupyter bridge loaded.'
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

            /*
             * Only open the parent prompt here.
             * The placeholder cell is created later,
             * after the user submits the prompt.
             */

            window.parent.postMessage(
              {
                type:
                  'math_notes_editor-open-python-prompt',

                requestId:
                  crypto.randomUUID()
              },
              MATH_NOTES_EDITOR_ORIGIN
            );


          } catch (error) {

            console.error(
              'math_notes_editor: could not open AI prompt:',
              error
            );

          }

        }

      },
      true
    );


    /*
     * Listen for commands from math_notes_editor.
     */

    window.addEventListener(
      'message',
      event => {

        if (
          event.origin !== MATH_NOTES_EDITOR_ORIGIN
        ) {

          return;

        }


        const message =
          event.data as MathNotesEditorMessage;


        if (!message) {

          return;

        }


        /*
         * Create the placeholder cell only after
         * the user submits the prompt.
         */

        if (
          message.type ===
          'math_notes_editor-create-placeholder'
        ) {

          const requestId =
            message.requestId;


          if (!requestId) {

            sendToMathNotesEditor({

              type:
                'math_notes_editor-create-placeholder-result',

              success:
                false,

              error:
                'No request ID was provided.'

            });

            return;

          }


          try {

            const panel =
              tracker.currentWidget;


            if (!panel) {

              throw new Error(
                'No notebook is open.'
              );

            }


            const notebook =
              panel.content;


            const cell =
              notebook.activeCell;


            if (!cell) {

              throw new Error(
                'No active cell.'
              );

            }


            notebook.activeCellIndex =
              notebook.widgets.indexOf(cell);


            NotebookActions.insertBelow(
              notebook
            );


            const placeholderCell =
              notebook.activeCell;


            if (!placeholderCell) {

              throw new Error(
                'Could not create placeholder cell.'
              );

            }


            placeholderCell.model.sharedModel.setSource(
              '<!-- AI_GENERATING -->'
            );


            pendingCells.set(
              requestId,
              placeholderCell
            );


            sendToMathNotesEditor({

              type:
                'math_notes_editor-create-placeholder-result',

              success:
                true,

              requestId:
                requestId

            });


          } catch (error) {

            console.error(
              'math_notes_editor placeholder creation failed:',
              error
            );


            sendToMathNotesEditor({

              type:
                'math_notes_editor-create-placeholder-result',

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


        /*
         * Replace the placeholder cell with
         * AI-generated Python.
         */

        if (
          message.type ===
          'math_notes_editor-insert-text'
        ) {

          const requestId =
            message.requestId;


          if (!requestId) {

            sendToMathNotesEditor({

              type:
                'math_notes_editor-insert-result',

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

            sendToMathNotesEditor({

              type:
                'math_notes_editor-insert-result',

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


            sendToMathNotesEditor({

              type:
                'math_notes_editor-insert-result',

              success:
                true,

              requestId:
                requestId

            });


          } catch (error) {

            console.error(
              'math_notes_editor insertion failed:',
              error
            );


            sendToMathNotesEditor({

              type:
                'math_notes_editor-insert-result',

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
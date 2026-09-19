c.ServerApp.port = 8890
c.ServerApp.token = ""
c.ServerApp.password = ""

c.ServerApp.allow_origin = "http://127.0.0.1:8000"

c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://127.0.0.1:8000"
    }
}

c.MappingKernelManager.default_kernel_name = "jupyter_venv"
"""
The following code needs to be run to register a virtual environment as jupyter_venv:

python -m pip install ipykernel
python -m ipykernel install --user --name=jupyter_venv --display-name "Python (jupyter_venv)"


"""
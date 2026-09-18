c.ServerApp.port = 8890
c.ServerApp.token = ""
c.ServerApp.password = ""

c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://127.0.0.1:8000"
    }
}
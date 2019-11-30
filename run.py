from build.app import init_dash

# Init and run the app
app = init_dash()
if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
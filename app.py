from mizimob import app
import eventlet.wsgi


if __name__ == '__main__':
    # app.run(host="0.0.0.0",port=7000,debug=True)
    port = 7000
    eventlet.wsgi.server(eventlet.listen(('', port)), app)

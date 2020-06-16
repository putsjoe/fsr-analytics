
import json
import datetime

import redis
from flask import Flask, render_template, request, abort, make_response
from flask_basicauth import BasicAuth
from user_agents import parse as parse_agent


app = Flask(
    __name__, static_url_path='', static_folder='static',
    template_folder='templates')
app.secret_key = b'_5#y2L"sjjw8sdfds27F4sd8z\n\xec]/'

REDIS_STREAM_NAME = 'analytics'
COOKIE_NAME = 'analytics-tracker'

app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'analytics'
basic_auth = BasicAuth(app)

r = redis.Redis(decode_responses=True)

print(f'Using redis stream name {REDIS_STREAM_NAME}')


def get_remote():
    if request.headers.getlist("X-Forwarded-For"):
        return ','.join(request.access_route) 
    else:
        return str(request.remote_addr)

@app.route('/noscript.gif')
def serve():
    r.xadd(REDIS_STREAM_NAME, {
        'args': json.dumps(request.args),
        'remote_addr': get_remote(),
        'user_agent': str(parse_agent(request.user_agent.string)),
        'referrer': str(request.referrer),
    })
    response = make_response(app.send_static_file('noscript.gif'))
    # Dont allow the gif to be cached, ensuring all pageviews are recorded.
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/analytics.js')
def servejs():
    return app.send_static_file('a.js')


@app.route('/a')
def server():
    print(request.args)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/')
@basic_auth.required
def home():
    alldata = r.xrevrange(REDIS_STREAM_NAME)
    data = []
    for d in alldata:
        data.append([
            d[0],
            redis.client.timestamp_to_datetime(int(d[0][:10])),
            d[1].get('remote_addr'),
            d[1].get('user_agent'),
            d[1].get('referrer'),
            d[1].get('args'),
        ])

    return render_template('index.html', data=data)

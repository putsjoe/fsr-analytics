
import json

import redis
from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from user_agents import parse as parse_agent


app = Flask(
    __name__, static_url_path='', static_folder='static',
    template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"sjjw8sdfds27F4sd8z\n\xec]/'

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
from models import Hit

app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'analytics'
basic_auth = BasicAuth(app)

REDIS_STREAM_NAME = 'analytics'
COOKIE_NAME = 'analytics-tracker'

r = redis.Redis(decode_responses=True)


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
        'user_agent': request.user_agent.string,
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


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/import')
@basic_auth.required
def imp():
    from importdata import import_data
    return import_data()


@app.route('/live')
@basic_auth.required
def live():
    alldata = r.xrevrange(REDIS_STREAM_NAME)
    data = []
    for d in alldata:
        data.append([
            d[0],
            redis.client.timestamp_to_datetime(int(d[0][:10])),
            d[1].get('remote_addr'),
            d[1].get('user_agent'),
            parse_agent(d[1].get('user_agent')),
            d[1].get('referrer'),
            d[1].get('args'),
        ])
    return render_template('live.html', data=data)


def get_fields(fieldname):
    text = f'SELECT {fieldname} FROM hit Group BY {fieldname}'
    return [r[0] for r in db.engine.execute(text)]


@app.route('/')
@basic_auth.required
def alldata():
    alldata = Hit.query.order_by(Hit.added.desc())
    try:
        first_date = alldata[-1].added
        latest_date = alldata[0].added
    except IndexError:
        return '<p>No data available</p>'

    unique = alldata.filter_by(unique=True).count()
    nonunique = alldata.filter_by(unique=False).count()
    allvisits = alldata.count()

    deviced = {
        d: Hit.query.filter_by(ua_device=d).count()
        for d in get_fields('ua_device')}
    browserd = {
        b: Hit.query.filter_by(ua_browser=b).count()
        for b in get_fields('ua_browser')}
    platformd = {
        p: Hit.query.filter_by(ua_platform=p).count()
        for p in get_fields('ua_platform')}
    agentdata = dict(Device=deviced, Browser=browserd, Platform=platformd)

    pagedata = {
        p: Hit.query.filter_by(url=p).count()
        for p in get_fields('url')
    }
    referdata = [
        (r[0], r[1], r[2])
        for r in db.engine.execute(
            'SELECT referrer, url, COUNT(*) FROM hit GROUP BY referrer'
        )
        if r[0] != ''
    ]

    eventdata = {
        e: Hit.query.filter_by(event=e).count()
        for e in get_fields('event')
        if e and e != ''
    }

    ipdata = {
        i: Hit.query.filter_by(remote_addr=i).count()
        for i in get_fields('remote_addr')
    }
    return render_template(
        'data.html',
        first_date=first_date, latest_date=latest_date,
        unique=unique, nonunique=nonunique, allvisits=allvisits,
        agentdata=agentdata,
        pagedata=pagedata, referdata=referdata,
        eventdata=eventdata,
        ipdata=ipdata,
    )


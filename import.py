
import json
import redis
from app import db, REDIS_STREAM_NAME, r
from models import Hit
from user_agents import parse as parse_agent


data = r.xrange(REDIS_STREAM_NAME)

for d in data:
    dat = d[1]
    args = json.loads(dat.get('args'))

    def getarg(arg):
        if args:
            return args.get(arg)
        return ''

    def getunique():
        if 'unique' in args:
            return True
        return False

    db.session.add(
        Hit(
            redisid=d[0],
            added=redis.client.timestamp_to_datetime(int(d[0][:10])),
            remote_addr=dat.get('remote_addr'),
            referrer=getarg('referrer'),
            ua_device=parse_agent(dat.get('user_agent')).device.family,
            ua_platform=parse_agent(dat.get('user_agent')).os.family,
            ua_browser=parse_agent(dat.get('user_agent')).browser.family,
            url=dat.get('referrer'),
            unique=getunique(),
            uid=getarg('id'),
            event=getarg('event')
    ))
db.session.commit()

r.xdel(REDIS_STREAM_NAME, *[ d[0] for d in data ])


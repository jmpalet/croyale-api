from flask import Flask
from flask_cors import CORS
from redis import Redis
import warlog
import datetime
import pickle
import os
import logging

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)
if os.environ.get("REDIS_HOST") and os.environ.get("REDIS_PORT"):
    redis = Redis(
        host=os.environ.get("REDIS_HOST"),
        port=int(os.environ.get("REDIS_PORT")),
        password=os.environ.get("REDIS_PASSWORD")
    )
allowed_clan_tags = [
    '2PUGVU8U',
    '2GCRPJ0',
]


@app.route('/')
def hello():
    return 'Welcome to Clash Royale War Stats API!'


@app.route('/clan/<clan_tag>/warlog')
def clan_war_log(clan_tag):
    result = {}
    if redis.ping():
        if redis.exists(clan_tag):
            result = pickle.loads(redis.get(clan_tag))
        else:
            if clan_tag in allowed_clan_tags:
                result = warlog.get(clan_tag)
                redis.set(clan_tag, pickle.dumps(result))
                redis.expire(clan_tag, datetime.timedelta(seconds=result['ttl']))
            else:
                return {
                    'clanTag': clan_tag,
                    'error': 'Unauthorized',
                }, 401
    return result, 200


@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception('An error occurred during a request.')
    return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

from flask import Flask
from flask import render_template
from flask import request
from unbabel.api import UnbabelApi, Translation
from celery import Celery
import redis
import json
from collections import OrderedDict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
api = UnbabelApi(username='fullstack-challenge',
                 api_key='9db71b322d43a6ac0f681784ebdcc6409bb83359',
                 sandbox=True)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
db = redis.Redis("localhost", 6379)


@celery.task
def get_async_translation(id):
    with app.app_context():
        pipe = db.pipeline()
        trans = Translation()
        trans = api.get_translation(id)
        if trans.uid:
            transredis = {'status': trans.status,
                          'uid': trans.uid,
                          'text': trans.text,
                          'translation': trans.translation}
            rval = json.dumps(transredis)
            db.set("k_{}".format(trans.uid), rval)
            pipe.execute()


@celery.task
def get_sync_translation(query):
    with app.app_context():
        trans = Translation()
        trans = api.post_translations(text=query,
                                      target_language="es",
                                      source_language="en",)

        if trans.uid:
            transredis = {'status': trans.status,
                          'uid': trans.uid,
                          'text': trans.text,
                          'translation': trans.translation}
            rval = json.dumps(transredis)
            db.set("k_{}".format(trans.uid), rval)
            get_async_translation.apply_async(args=[trans.uid], countdown=30)


@app.route("/", methods=['GET', 'POST'])
def get_translations():

    if request.method == 'POST':
        querytext = request.form.get('querytext')
        if querytext:
            get_sync_translation.apply_async(args=[querytext], countdown=3)

        mydict = {}
        for key in db.scan_iter(match="k_*"):
            data = db.get(key)
            mydict[str(key, 'utf-8')] = json.loads(data)

        alpha = OrderedDict(sorted(mydict.items(),
                                   key=lambda x: len(x[1]['text'])))
        return render_template("latorre.html", mydict=alpha)

    return render_template("latorre.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)

Quick Setup (Python 3.6.5)
-----------

1.  Clone this repository.
2.  Create a virtualenv `python -m virtualenv latorre/` and install the requirements (requirements.txt).
2.a This proposal uses UnbabelApi, once you have downloaded it, please change next lines (or use six library, as suggested on a recent pull request):
    259, 280: ...v in locals().items()...
    491: ...except Exception as e... 
3.  Open a second terminal window and start a local Redis server (redis://localhost:6379).
4.  Open a third terminal window. Then start a Celery worker: `celery worker -A latorre.celery --loglevel=info`.
5.  Start the Flask application on your original terminal window: `python latorre.py`.
6.  Go to `http://localhost:5000/`




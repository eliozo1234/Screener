from serverless_wsgi import handle_request
from main import app

def handler(event, context):
    return handle_request(app, event, context)

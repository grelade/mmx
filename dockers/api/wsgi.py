import os
from server import gen_app

mongodb_url = os.environ.get('MONGODB_URL')
print('wsgi:',mongodb_url)
application = gen_app(mongodb_url)

if __name__ == "__main__":
	app.run()

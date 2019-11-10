import sys

import os


# establishes python virual env
python_home = '/var/www/virtual_envs/alpha-wvFlood'
activate_this = python_home + '/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

# adds app files to the path
sys.path.append('/var/www/pythonApps/alpha-wvFlood')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

application = get_wsgi_application()

# Deploy this project on PythonAnywhere

These instructions deploy the Django app in `careerpath/` as a PythonAnywhere
WSGI website. They assume the code is in a GitHub repository and that you are
creating a fresh deployment. The repository's local SQLite database and media
files are ignored by Git, so local accounts and uploaded files will not be
copied to the website.

PythonAnywhere's current guide uses a virtual environment, a manually
configured WSGI file, migrations, and a static file mapping. See the [official
existing Django project guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/).

## 1. Upload the code

Create a PythonAnywhere account, open a **Bash console**, and clone your
repository. Replace the placeholder with your actual GitHub URL:

```bash
cd ~
git clone https://github.com/REPLACE_WITH_YOUR_ACCOUNT/REPLACE_WITH_YOUR_REPOSITORY.git career-system
cd ~/career-system
```

The Django `manage.py` file should now be at `~/career-system/careerpath/manage.py`.

## 2. Install dependencies

Create and activate a Python 3.11 virtual environment, then install the
repository requirements:

```bash
mkvirtualenv --python=/usr/bin/python3.11 career-system-venv
cd ~/career-system
pip install -r requirements.txt
```

If Python 3.11 is not available for your account, choose a Python version
supported by both the PythonAnywhere account and the pinned project
dependencies.

## 3. Configure Django for your domain

In the PythonAnywhere **Web** tab, note your assigned domain, such as
`yourusername.pythonanywhere.com`. In `careerpath/careerpath/settings.py`, set
the production values before exposing the site:

```python
SECRET_KEY = 'a-long-private-random-value'
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = ['https://yourusername.pythonanywhere.com']
```

Replace the example hostname with the exact domain shown in your account. Keep
the secret key private and do not commit it to GitHub. For repeatable
deployments, read it from an environment variable configured for the web app;
the project currently supports `DJANGO_SECRET_KEY` for the key, but currently
sets `DEBUG` and `ALLOWED_HOSTS` directly in settings.

The project already trusts the forwarded HTTPS header and has a
`QR_PUBLIC_BASE_URL` setting. Set `QR_PUBLIC_BASE_URL` to
`https://yourusername.pythonanywhere.com` in the web app environment if QR
codes should always use the public address.

## 4. Create the PythonAnywhere web app

In the **Web** tab:

1. Select **Add a new web app** and choose your PythonAnywhere domain.
2. Choose **Manual configuration** and Python 3.11 (or the version used for
   the virtual environment).
3. Set **Virtualenv** to `/home/yourusername/.virtualenvs/career-system-venv`.
4. Open the generated WSGI configuration file. Replace its Django section
   with the following, updating the username and directory if needed:

```python
import os
import sys

project_path = '/home/yourusername/career-system/careerpath'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerpath.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5. Initialize the database and static files

In the Bash console:

```bash
cd ~/career-system/careerpath
python manage.py migrate
python manage.py populate_initial_data
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`check --deploy` should be reviewed for any remaining warnings. Do not ignore a
warning without understanding the setting it concerns.

Back in the **Web** tab, add a static files mapping:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/yourusername/career-system/careerpath/staticfiles` |

Save and press **Reload**. Open the site and try registration, login,
assessment, and the admin URL (`/admin/`). If it fails, open the error log link
on the Web tab; PythonAnywhere's [Django deployment guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
describes the WSGI and error-log checks.

## Database and uploaded files

The project uses SQLite. PythonAnywhere makes SQLite available, so it can be
adequate for a low-traffic demo, but PythonAnywhere warns that filesystem
latency and concurrent access can make SQLite slow or unreliable for a
production site. For sustained use, migrate to a managed database and keep
regular backups. [PythonAnywhere database options](https://help.pythonanywhere.com/pages/KindsOfDatabases/)

The app stores uploads under `careerpath/media/`. Git ignores this directory,
so uploads need a separate backup and restore process when redeploying. Do not
add a public `/media/` mapping unless every uploaded file is intended to be
publicly accessible.

## Updating the deployed site

After pushing changes to GitHub, update and collect static files in the Bash
console, then reload the web app:

```bash
cd ~/career-system
git pull
cd careerpath
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the PythonAnywhere Web tab.

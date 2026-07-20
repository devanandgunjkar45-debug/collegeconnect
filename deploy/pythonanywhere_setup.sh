#!/usr/bin/env bash
set -euo pipefail

# Usage: ./pythonanywhere_setup.sh <pythonanywhere-username> [python_version]
# Example: ./pythonanywhere_setup.sh yourusername 3.12

USER_ARG="${1:-}"
PYVER_ARG="${2:-3.12}"

if [ -z "$USER_ARG" ]; then
  echo "Usage: $0 <pythonanywhere-username> [python_version]"
  exit 1
fi

PA_USER="$USER_ARG"
PYTHON_BIN="python${PYVER_ARG}"
PROJECT_DIR="/home/${PA_USER}/project"
VENV_DIR="/home/${PA_USER}/venv/campusconnect"

echo "Project dir: $PROJECT_DIR"
echo "Virtualenv: $VENV_DIR"
echo "Python: $PYTHON_BIN"

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

if [ ! -d .git ]; then
  echo "Cloning repository into $PROJECT_DIR"
  git clone https://github.com/devanandgunjkar45-debug/collegeconnect.git .
else
  echo "Repository already present; pulling latest changes"
  git pull origin main
fi

echo "Creating virtualenv (this may take a minute)..."
$PYTHON_BIN -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "Running migrations and collecting static files"
cd "$PROJECT_DIR"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo
echo "Setup complete. Next steps:"
echo " - In the PythonAnywhere Web tab, set Working directory to: $PROJECT_DIR"
echo " - Set Virtualenv path to: $VENV_DIR"
echo " - Set environment variables (DJANGO_SECRET_KEY, DJANGO_DEBUG=False, DJANGO_ALLOWED_HOSTS=collegeconnect.pythonanywhere.com)"
echo " - Edit WSGI file to point to campusconnect.wsgi as documented in README.md"
echo " - Reload the web app from the Web tab"

exit 0

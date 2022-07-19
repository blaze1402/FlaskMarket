from market import app
import os

# Run this command to run -e refers to the environment variable which let's run the app in debug mode.
# docker build . -t flask_app_dev
# docker run -p 5000:5000 -e DEBUG=1 flask_app_dev
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('DEBUG') == '1')
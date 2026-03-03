# Twitter Clone — Python Flask & Google Cloud

A Twitter clone built with Python, Flask, Firebase Authentication, and Google Cloud Datastore.

---

## Prerequisites

Make sure the following are installed before getting started:

- [Python 3.14](https://www.python.org/downloads/) (recommended)
- [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install)
- A Google Cloud project with Datastore enabled
- A Firebase project linked to the same Google Cloud project

---

## Project Structure

```
project-twitter-website/
├── main.py               # Flask app entry point
├── requirements.txt      # Python dependencies
├── app.yaml              # GCP App Engine config
├── index.yaml            # Cloud Datastore index config
├── static/               # CSS, JS, images
├── templates/            # HTML templates (Jinja2)
└── your-service-key.json # GCP service account key (DO NOT commit this)
```

---

## Local Setup

### 1. Clone the repository

```cmd
git clone https://github.com/pnaraltnsk/project-twitter-website.git
cd project-twitter-website
```

### 2. Create and activate a virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

> On Mac/Linux: `source venv/bin/activate`

You should see `(venv)` appear at the start of your terminal prompt.

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

> If you get build errors, try: `venv\Scripts\python.exe -m pip install -r requirements.txt`

### 4. Add your GCP service account key

- Go to [console.cloud.google.com](https://console.cloud.google.com)
- Navigate to **IAM & Admin → Service Accounts**
- Select your service account → **Keys** tab → **Add Key → Create new key → JSON**
- Download the JSON file and place it in the project root folder
- Add the filename to `.gitignore` so it is never committed:

```
echo your-service-key.json >> .gitignore
```

### 5. Set the credentials environment variable

**Windows Command Prompt:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=your-service-key.json
```

**Mac/Linux:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="your-service-key.json"
```

> This must be run every time you open a new terminal session before starting the app.

### 6. Run the app

```cmd
python main.py
```

The app will be available at: `http://127.0.0.1:8080`

---

## Authentication

This project uses **Firebase Authentication** — there are no passwords stored in Datastore. To log in you need a Firebase account.

### Adding a user

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Authentication → Users**
4. Click **Add user** and enter an email and password
5. Use those credentials to log in through the app

---

## Deploying to Google Cloud App Engine

```cmd
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy Datastore indexes first
gcloud datastore indexes create index.yaml

# Deploy the app
gcloud app deploy app.yaml
```

---

## requirements.txt (updated for Python 3.11+)

```
Flask==3.1.0
Werkzeug==3.1.3
Jinja2==3.1.4
MarkupSafe==3.0.2
click==8.1.8
itsdangerous==2.2.0
google-cloud-datastore==2.20.1
google-auth==2.38.0
google-api-python-client==2.163.0
requests==2.32.3
certifi==2025.1.31
urllib3==2.3.0
idna==3.10
httplib2==0.22.0
uritemplate==4.1.1
pyparsing==3.2.1
pyasn1==0.6.1
rsa==4.9
cachetools==5.5.2
six==1.17.0
```

---

## Security Notes

- **Never commit your service account JSON key to git**
- Always add it to `.gitignore` before placing it in the project folder
- If a key is accidentally committed, delete it immediately in GCP (**IAM & Admin → Service Accounts → Keys**) and create a new one

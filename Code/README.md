# Syllabus Management System

## Setup for Windows

### 1. Installing Python (includes Pip)
- Go to https://www.python.org/downloads/
- Download and install the newest version of Python 2 and 3
- While installing, make sure to check box for adding python to the system PATH

### 2. Installing VirtualEnv with Pip
- Open up command prompt, and type in the following command:
> pip install virtualenv
- Once virtualenv is installed, in command prompt navigate to your user folder (where documents, pictures, etc. are)
- Type in the following command
> virtualenv virtualenv

### 3. Installing Project Requirements with Pip
- In command prompt, navigate to the project folder (where requirements.txt is)
- Type in the following command
> pip install -r requirements.txt

### 4. Running Server
- While in the project folder, type the following command
> python run.py
- The server is now running, and viewable at the printed address (likely https://127.0.0.1:5000/)

## Centos 7 Setup

### 1. Install all dependencies

    yum install python-devel python-virtualenv libffi-devel gcc openssl-devel sqlite

### 2. Setup a virtual environment
    virtualenv /path/to/venv
	source /path/to/venv/bin/activate
	pip install -U pip

### 3. Install requirements
    pip install -r requirements.txt

### 4. Run the server
	python run.py

## Debian Jessie Setup

### 1. Install all dependencies

    apt install python3-dev python3-venv libffi-dev gcc libssl-dev sqlite3

### 2. Setup a virtual environment
    python3 -m venv /path/to/venv
	source /path/to/venv/bin/activate

### 3. Install requirements
    pip install -r requirements.txt

### 4. Run the server
	python run.py

The server will be running on https://localhost:5000

### Usage notes:
- When an administrator adds a course, it is not immediately removable: only courses with approved syllabi are available, and they are only marked inactive
- To change the new course template, edit the template in config.py
- If you want to change the Client ID or Secret for example to set up OAuth with a different email it can be found in the config.py file in the Auth class under CLIENT_ID, and CLIENT_SECRET.
- If you want to see the settings that we already have set up, log into google as "capstone.ad.one@gmail.com", with the password "capstone". And navigate to credentials in the sidebar.
- When on a Unix-like operating system, the supplied bootstrap.sh script can be used after activating the virtual environment to start with a clean database
- To use your own ssl keys, overwrite ssl.cert with you certificate file and ssl.key with your private key

### Creating OAuth:
- First create a gmail account.
- Navigate to https://console.developers.google.com/apis/
- Click Credentials in the left sidebar
- Click Create Credentials -> OAuth Client ID
- Choose Web Application
- Follow on screen instructions until the Client ID, and Secret is displayed.
- Change values of respective variables in config.py
	- Note: There are two instances of client Secret in the config file

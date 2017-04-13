# Cerpstern!

## Todo:

### Code Related:

#### OH SHIT stuff:
* Search algorithm, and results page
* Input validation / DB homogeneity

 Aestetic
* Make admin landing page 2 column / redesign
* Edit Page 
	* Button Positioning
	* General Syllabus Formatting


Functional
* Search Related
	* Add 'Course' Text Field.
	* Fuzzy Search for seach_text field
	* Create a '/results' page (jinja template) to display search results.

### Course Related / Due:
* Thurs -> Peer Evaluations
* Email Samba With preferred Presentation Date

## Setup for Windows

### 1. Installing Python (includes Pip)
- Go to https://www.python.org/downloads/
- Download and install the newest version of Python 3
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

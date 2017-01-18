# Teacher's Aide Website

Builds on [original Teacher's Aide project](https://github.com/steph-rage/TeachersAide) and the [Python web server project](https://github.com/steph-rage/PracticeServer) to create a Teacher's Aide website. Teachers can create or log in to a profile where they can create and store multiple choice tests. 

## Getting Started

This is a website, built on a Python server using http libraries.  

### Prerequisites

Download the requirements.txt file and run

		pip install -r requirements.txt

### Running

After installing the program, start the server by running 

		python3 Teachers_aide_server.py

This will show no activity on your command line, but the server will be running. Now open up a browser and navigate to "localhost:8000". Once here, you will see a login screen. You can create your own user, or login to the sample user using:

username: TestUser

password: password

to see current tests, or to create a new test. 

*Note as of 1/18/17: the current iteration is for some reason not playing nicely with Chrome. Cookies in Chrome apparently behave differently than expected. Open the site in Firefox and everything should be fine.*
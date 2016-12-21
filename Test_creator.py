from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from jinja2 import Template

from Tests import Test


class Handler(BaseHTTPRequestHandler):

	#Browser sends a GET request to load the original page
	def do_GET(self):
		#Talk to the browser
		self.send_response(200)
		self.end_headers()

		#Load the html template, render using Jinja and send to browser
		with open('New_test.html', 'r') as html_file:
			html = Template(html_file.read()).render()
		self.wfile.write(bytes(html, 'utf8'))
		return

	#When POST data is sent via the html forms, it will call do_POST
	def do_POST(self):
		global new_test

		#Talk to the browser
		self.send_response(200)
		self.end_headers()

		#Get the POST data and parse it into meaningful pieces
		form_input = parse.unquote_plus(self.rfile.read(int(self.headers.get('content-length'))).decode('utf8')).split('=')

		#When data being submitted is a name and the creation of a new test
		if form_input[0] == 'test_name':
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			#In case both forms are not filled in
			if test_name == '' or number_of_choices == '':
				with open('New_test.html', 'r') as html_file:
					html = Template(html_file.read()).render()
				self.wfile.write(bytes(html, 'utf8'))
			#Create an instance of class Test using input information
			number_of_choices = int(number_of_choices)
			new_test = Test(test_name, number_of_choices)

		#When data being submitted is a new question with answer choices
		else:
			question_text = form_input[1].split('&')[0]
			answers = []
			correct_answer = ''
			for i in range(new_test.choices + 1):
				next_answer = form_input[i+2].split('&')[0]
				if next_answer == 'on':
					correct_answer = form_input[i+3].split('&')[0]
				else:
					answers.append(next_answer)
			answers.append(new_test.answer_choices[answers.index(correct_answer)])
			new_test.add_question(question_text, answers)

		#Variables to pass to html template
		template_vars = {
			'test_name': new_test.name,
			'number_of_choices': new_test.choices,
			'letters': new_test.answer_choices,
			'questions': new_test.questions,
		}
		with open('Add_questions.html', 'r') as html_file:
			html = Template(html_file.read()).render(template_vars)
		self.wfile.write(bytes(html, 'utf8'))
		return




def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run()

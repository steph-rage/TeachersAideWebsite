from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
from jinja2 import Template

from Tests import Test


class Handler(BaseHTTPRequestHandler):

	tests = {}

	def load_test_creator(self, test_name, number_of_choices):
		#In case both forms are not filled in
		if test_name == '' or number_of_choices == '':
			with open('Templates/New_test.html', 'r') as html_file:
				html = Template(html_file.read()).render()
			self.wfile.write(bytes(html, 'utf8'))
		#Create an instance of class Test using input information
		number_of_choices = int(number_of_choices)
		return Test(test_name, number_of_choices)

	def load_add_questions(self, form_input, test):
		question_text = form_input[1].split('&')[0]
		answers = []
		correct_answer = ''
		for i in range(test.choices + 1):
			next_answer = form_input[i+2].split('&')[0]
			if next_answer == 'on':
				correct_answer = form_input[i+3].split('&')[0]
			else:
				answers.append(next_answer)
		answers.append(test.answer_choices[answers.index(correct_answer)])
		test.add_question(question_text, answers)
		return test


	#Browser sends a GET request to load the original page
	def do_GET(self):
		self.send_response(200)
		self.end_headers()

		
		if 'editor' in self.path:

			#Go to test creator
			if 'new' in self.path:
				with open('Templates/New_test.html') as html_file:
					page_display = Template(html_file.read()).render()
				self.wfile.write(bytes(page_display, 'utf8'))

			elif 'question' in self.requestline:
				info = self.path.split('/')
				test_name = parse.unquote_plus(info[2])
				print(test_name)
				print(info)
				question_number = int(info[3].split('question')[1].split('detail')[0])
				print(question_number)
				question = list(self.tests[test_name].questions.items())[question_number - 1][0]
				#current_question = 
				template_vars = {
					'question_number': question_number,
					'test_name': test_name,
					'question': question,
				}
				#Load html template for detail on an individual question
				with open('Templates/question_detail.html', 'r') as html_file:
					html = Template(html_file.read()).render(template_vars)
				self.wfile.write(bytes(html, 'utf8')) 

			#Go to main page for test editor
			else:
				editor_variables = {
					'current_tests': self.tests,
					'path': self.path,
				}
				with open('Templates/Test_editor.html') as html_file:
					page_display = Template(html_file.read()).render(editor_variables)
				self.wfile.write(bytes(page_display, 'utf8'))

		#Load home screen with login
		else:
			with open('Templates/Login_page.html') as html_file:
				page_display = Template(html_file.read()).render()
				self.wfile.write(bytes(page_display, 'utf8'))


	
		return

	#When POST data is sent via the html forms, it will call do_POST
	def do_POST(self):
		global new_test
		#Talk to the browser
		self.send_response(200)
		self.end_headers()

		#Get the POST data and parse it into meaningful pieces
		form_input = parse.unquote_plus(self.rfile.read(int(self.headers.get('content-length'))).decode('utf8')).split('=')
		print(form_input)
		#if form_input[0] == 'username':
			#access teacher's profile

		#When data being submitted is a name and the creation of a new test
		if form_input[0] == 'test_name':
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			new_test = self.load_test_creator(test_name, number_of_choices)
			self.tests[test_name] = new_test
			
		#When data being submitted is a new question with answer choices
		else:
			new_test = self.load_add_questions(form_input, new_test)

		questions_with_numbers = []
		for question in new_test.questions:
			questions_with_numbers.append(question)
		number_of_questions = len(questions_with_numbers)
		#Variables to pass to html template
		template_vars = {
			'test_name_url': parse.quote_plus(new_test.name),
			'test_name': new_test.name,
			'number_of_choices': new_test.choices,
			'letters': new_test.answer_choices,
			'questions': questions_with_numbers,
			'number_of_questions': number_of_questions,
			'path': self.path,
		}
		with open('Templates/Add_questions.html', 'r') as html_file:
			html = Template(html_file.read()).render(template_vars)
		self.wfile.write(bytes(html, 'utf8'))
		return




def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run()

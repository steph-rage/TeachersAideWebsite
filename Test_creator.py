from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
from jinja2 import Template

from Tests import Test


class Handler(BaseHTTPRequestHandler):

	#Will eventually be taken care of by the teacher profile, once incorporated
	tests = {}

	def load_test_editor(self):
		editor_variables = {
			'current_tests': self.tests,
			'path': self.path,
		}
		with open('Templates/Test_editor.html') as html_file:
			page_display = Template(html_file.read()).render(editor_variables)
		self.wfile.write(bytes(page_display, 'utf8'))

	def load_new_test(self):
		with open('Templates/New_test.html') as html_file:
			page_display = Template(html_file.read()).render()
		self.wfile.write(bytes(page_display, 'utf8'))

	def load_question_detail(self, url_info):
		new_path = url_info[0:-1]
		('/').join(new_path)
		test_name = parse.unquote_plus(url_info[2])
		question_number = int(url_info[3].split('question')[1].split('detail')[0])
		question = list(self.tests[test_name].questions.items())[question_number - 1][0]
		template_vars = {
			'path': new_path,
			'question_number': question_number,
			'test_name': test_name,
			'question': question,
			'number_of_choices': self.tests[test_name].choices,
			'answers': self.tests[test_name].questions[question],
		}
		with open('Templates/question_detail.html', 'r') as html_file:
			html = Template(html_file.read()).render(template_vars)
		self.wfile.write(bytes(html, 'utf8')) 

	def load_add_questions(self, url_info, test_name):
		test = self.tests[test_name]
		questions_with_numbers = []
		for question in test.questions:
			questions_with_numbers.append(question)
		number_of_questions = len(questions_with_numbers)
		template_vars = {
			'test_name_url': url_info[-1],
			'test_name': test_name,
			'number_of_choices': test.choices,
			'letters': test.answer_choices,
			'questions': questions_with_numbers,
			'number_of_questions': number_of_questions,
			'path': self.path,
		}
		with open('Templates/Add_questions.html', 'r') as html_file:
			html = Template(html_file.read()).render(template_vars)
		self.wfile.write(bytes(html, 'utf8'))

	def create_new_test(self, test_name, number_of_choices):
		#In case both forms are not filled in
		if test_name == '' or number_of_choices == '':
			with open('Templates/New_test.html', 'r') as html_file:
				html = Template(html_file.read()).render()
			self.wfile.write(bytes(html, 'utf8'))
		#Create an instance of class Test using input information
		number_of_choices = int(number_of_choices)
		return Test(test_name, number_of_choices)

	def add_question_to_test(self, form_input, test):
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

		#Any get request in the editor part of the site, after successful login
		if 'editor' in self.path:
			url_info = self.path.split('/')
			pretty_url_info_last = parse.unquote_plus(url_info[-1])

			#Go to test creator, where a new test is given a name and number of multiple choice answers
			if len(url_info) >= 3 and'new' in url_info[2]:
				self.load_new_test()

			#Go to editable detail on a specific question which has already been entered
			elif len(url_info) >= 4 and 'question' in url_info[3]:
				self.load_question_detail(url_info)

			elif pretty_url_info_last in self.tests:
				test_name = pretty_url_info_last
				self.load_add_questions(url_info, test_name)

			#Go to main page for test editor
			else:
				self.load_test_editor()

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

		#if form_input[0] == 'username':
			#access teacher's profile

		#When data being submitted is a name and the creation of a new test
		if form_input[0] == 'test_name':
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			new_test = self.create_new_test(test_name, number_of_choices)
			self.tests[test_name] = new_test
			
		#When data being submitted is a new question with answer choices
		else:
			new_test = self.add_question_to_test(form_input, new_test)

		questions_with_numbers = []
		for question in new_test.questions:
			questions_with_numbers.append(question)
		number_of_questions = len(questions_with_numbers)
		path_to_editor = self.path.split('/')
		path_to_editor.pop()
		path_to_editor = ('/').join(path_to_editor)
		#Variables to pass to html template
		template_vars = {
			'test_name_url': parse.quote_plus(new_test.name),
			'test_name': new_test.name,
			'number_of_choices': new_test.choices,
			'letters': new_test.answer_choices,
			'questions': questions_with_numbers,
			'number_of_questions': number_of_questions,
			'path': self.path,
			'path_to_editor': path_to_editor,
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

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
from jinja2 import Template

from Tests import Test


class Handler(BaseHTTPRequestHandler):

	#Will eventually be taken care of by the teacher profile, once incorporated
	tests = {}

	def load_test_editor(self):
		path = self.path.translate({ord('?'): None})
		print(path)
		editor_variables = {
			'current_tests': self.tests,
			'path': path,
		}
		with open('Templates/Test_editor.html') as html_file:
			page_display = Template(html_file.read()).render(editor_variables)
		self.wfile.write(bytes(page_display, 'utf8'))

	def load_new_test(self, url_info):
		path = ('/').join(url_info)
		variables = {
			'path': path
		}
		with open('Templates/New_test.html') as html_file:
			page_display = Template(html_file.read()).render(variables)
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
		pretty_url_info_last = parse.unquote_plus(url_info[-1])
		test_name_url = self.path if pretty_url_info_last == test_name else self.path + '/' + parse.quote_plus(test_name)
		questions_with_numbers = []
		for question in test.questions:
			questions_with_numbers.append(question)
		number_of_questions = len(questions_with_numbers)
		path_to_editor = self.path.split('/')
		path_to_editor.pop()
		path_to_editor = ('/').join(path_to_editor)
		template_vars = {
			'test_name_url': test_name_url,
			'test_name': test_name,
			'number_of_choices': test.choices,
			'letters': test.answer_choices,
			'questions': questions_with_numbers,
			'number_of_questions': number_of_questions,
			'path': self.path,
			'path_to_editor': path_to_editor,
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

			#Go to editable detail on a specific question which has already been entered
			if len(url_info) >= 4 and 'question' in url_info[3]:
				self.load_question_detail(url_info)

			#Go to screen to add questions to a specific test
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


	def do_POST(self):
		global new_test
		self.send_response(200)
		self.end_headers()

		url_info = self.path.split('/')
		form_input = parse.unquote_plus(self.rfile.read(int(self.headers.get('content-length'))).decode('utf8')).split('=')


		#Go to test creator, where a new test is given a name and number of multiple choice answers
		if len(url_info) >= 3 and'new' in url_info[2]:
			url_info.pop()
			self.load_new_test(url_info)

		#Create a new instance of class Test, and go to screen to add questions to that test
		elif len(form_input) >= 1 and form_input[0] == 'test_name':
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			new_test = self.create_new_test(test_name, number_of_choices)
			self.tests[test_name] = new_test
			self.load_add_questions(url_info, test_name)
			
		#Add a question to the existing test and remain on the same screen
		else:
			new_test = self.add_question_to_test(form_input, new_test)
			self.load_add_questions(url_info, new_test.name)

		return



def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
	run()

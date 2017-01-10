from http.server import HTTPServer, BaseHTTPRequestHandler
from http import cookies
from urllib import parse, request
from jinja2 import Template

import json

from Test_creator import Test
from Profile_creator import TeacherProfile


class Handler(BaseHTTPRequestHandler):

	#Will eventually be taken care of by the teacher profile, once incorporated
	tests = {}

	def load_login_page(self):
		with open('Templates/Login_page.html') as html_file:
				page_display = Template(html_file.read()).render()
				self.wfile.write(bytes(page_display, 'utf8'))
	

	def load_test_editor(self):
		path = self.path.translate({ord('?'): None})
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
		new_path = ('/').join(new_path)
		test_name = parse.unquote_plus(url_info[2])
		test = self.tests[test_name]
		question_number = int(url_info[3].split('question')[1].split('detail')[0])
		question = test.question_list[question_number - 1]
		answers = self.tests[test_name].questions[question]
		correct_answer = answers[-1]
		correct_answer_index = test.answer_choices.index(correct_answer)
		template_vars = {
			'path': new_path,
			'question_number': question_number,
			'test_name': test_name,
			'question': question,
			'number_of_choices': test.choices,
			'answers': answers,
			'correct_answer_index': correct_answer_index,
		}

		with open('Templates/question_detail.html', 'r') as html_file:
			html = Template(html_file.read()).render(template_vars)
		self.wfile.write(bytes(html, 'utf8')) 


	def load_add_questions(self, url_info, test_name):
		test = self.tests[test_name]
		pretty_url_info_last = parse.unquote_plus(url_info[-1])
		test_name_url = self.path if pretty_url_info_last == test_name else self.path + '/' + test.url_name
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
			'questions': test.question_list,
			'number_of_questions': len(test.question_list),
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
		number_of_choices = int(number_of_choices)

		return Test(test_name, number_of_choices)



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
			self.load_login_page()

		return


	def do_POST(self):
		self.send_response(200)
		self.end_headers()

		url_info = self.path.split('/')
		form_input = parse.unquote_plus(self.rfile.read(int(self.headers.get('content-length'))).decode('utf8')).split('=')

		#Go to test creator, where a new test is given a name and number of multiple choice answers
		if len(url_info) >= 3 and'new' in url_info[2]:
			url_info.pop()
			self.load_new_test(url_info)

		#Create a new instance of class Test, and go to screen to add questions to that test
		elif form_input[0] == 'test_name':
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			new_test = self.create_new_test(test_name, number_of_choices)
			self.tests[test_name] = new_test
			self.load_add_questions(url_info, test_name)

		#Add a question to the existing test and remain on the same screen
		elif form_input[0] == 'new_question':
			test_name = parse.unquote_plus(url_info[-1])
			test = self.tests[test_name]
			test = test.add_question(form_input, url_info)
			self.load_add_questions(url_info, test_name)

		#Change a question on the existing test and return to the add questions screen
		elif 'edited_question' in form_input[0]:
			question_number = int(form_input[0].split(' ')[1])
			test_name = parse.unquote_plus(url_info[-1])
			test = self.tests[test_name]
			test = test.edit_question(question_number, form_input, url_info)
			self.load_add_questions(url_info, test_name)

		elif 'delete' in form_input[0]:
			question_number = int(form_input[0].split(' ')[1])
			test_name = parse.unquote_plus(url_info[-1])
			test = self.tests[test_name]
			test = test.delete_question(question_number)
			self.load_add_questions(url_info, test_name)

		elif form_input[0] == 'username':
			try:
				username = form_input[1].split('&')[0]
				with open(username + '.json', 'r', encoding='utf-8') as f:
					profile_vars = json.load(f)
				print(profile_vars)
			except FileNotFoundError:
				self.load_login_page()

		return



def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
	run()

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
from jinja2 import Template

import json
import re

from Test_creator import Test
from Profile_creator import TeacherProfile


class Handler(BaseHTTPRequestHandler):

	def load_login_page(self):
		with open('Templates/Login_page.html') as html_file:
				page_display = Template(html_file.read()).render()
				self.wfile.write(bytes(page_display, 'utf8'))
	

	def load_new_profile(self):
		with open('Templates/New_profile.html') as html_file:
				page_display = Template(html_file.read()).render()
				self.wfile.write(bytes(page_display, 'utf8'))


	def load_test_editor(self, user_profile):
		editor_variables = {
			'current_tests': user_profile.tests,
			'path': self.path,
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


	def load_question_detail(self, url_info, user_profile):
		new_path = url_info[0:-1]
		new_path = ('/').join(new_path)
		test_name = parse.unquote_plus(url_info[-2])
		test = user_profile.tests[test_name]
		question_number = int(url_info[-1].split('question')[1].split('detail')[0])
		question = test.question_list[question_number - 1]
		answers = user_profile.tests[test_name].questions[question]
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


	def load_add_questions(self, url_info, test_name, user_profile):
		test = user_profile.tests[test_name]
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


	def send_cookie(self, username):
		self.send_header('Set-Cookie', 'user={}; path=/; HTTPOnly'.format(username))


	def validate_user(self):
		username = (re.search('Cookie:.*user=([\w\-_\.\*]*)', self.headers.as_string())).group(1)
		with open(username + '.json', 'r', encoding='utf-8') as f:
			profile_vars = json.load(f)
		current_user = TeacherProfile(profile_vars['username'], profile_vars['password'])
		user_tests_JSON = profile_vars['tests']
		user_tests_obj = {}
		print(user_tests_JSON)
		for test_name, test_vars in user_tests_JSON.items():
			test_obj = Test(test_vars['name'], test_vars['choices'])
			for test_variable in test_vars:
				test_obj.test_variable = test_variable
			user_tests_obj[test_name] = test_obj
		current_user.tests = user_tests_obj
		return current_user


	def create_new_test(self, test_name, number_of_choices):
		#This will get moved to teacher profile also, I think
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
			user_profile = self.validate_user()

			#Go to editable detail on a specific question which has already been entered
			if 'question' in url_info[-1]:
				self.load_question_detail(url_info, user_profile)

			#Go to screen to add questions to a specific test
			elif pretty_url_info_last in user_profile.tests:
				test_name = pretty_url_info_last
				self.load_add_questions(url_info, test_name, user_profile)

			#Go to main page for test editor
			else:
				self.load_test_editor(user_profile)
			print(user.username, user.tests)
			user_profile.save()

		#Load home screen with login
		else:
			self.load_login_page()

		return


	def do_POST(self):
		self.send_response(200)
		try:
			user_profile = self.validate_user()
		except AttributeError:
			pass
		url_info = self.path.split('/')
		form_input = parse.unquote_plus(self.rfile.read(int(self.headers.get('content-length'))).decode('utf8')).split('=')

		#Go to test creator, where a new test is given a name and number of multiple choice answers
		if url_info[-1] == 'new':
			self.end_headers()
			url_info.pop()
			self.load_new_test(url_info)

		elif url_info[-1] == 'new_profile':
			self.end_headers()
			self.load_new_profile()


		#Create a new instance of class Test, and go to screen to add questions to that test
		elif form_input[0] == 'test_name':
			self.end_headers()
			test_name = form_input[1].split('&')[0]
			number_of_choices = form_input[2]
			new_test = self.create_new_test(test_name, number_of_choices)
			user_profile.tests[test_name] = new_test
			self.load_add_questions(url_info, test_name, user_profile)

		#Add a question to the existing test and remain on the same screen
		elif form_input[0] == 'new_question':
			self.end_headers()
			test_name = parse.unquote_plus(url_info[-1])
			test = user_profile.tests[test_name]
			print(test.question_list)
			test = test.add_question(form_input, url_info)
			self.load_add_questions(url_info, test_name, user_profile)

		#Change a question on the existing test and return to the add questions screen
		elif 'edited_question' in form_input[0]:
			self.end_headers()
			question_number = int(form_input[0].split(' ')[1])
			test_name = parse.unquote_plus(url_info[-1])
			test = user_profile.tests[test_name]
			test = test.edit_question(question_number, form_input, url_info)
			self.load_add_questions(url_info, test_name)

		elif 'delete' in form_input[0]:
			self.end_headers()
			question_number = int(form_input[0].split(' ')[1])
			test_name = parse.unquote_plus(url_info[-1])
			test = user_profile.tests[test_name]
			test = test.delete_question(question_number)
			self.load_add_questions(url_info, test_name)

		elif form_input[0] == 'new_username':
			username = form_input[1].split('&')[0]
			password = form_input[2]
			user_profile = TeacherProfile(username, password)
			self.send_cookie(username)
			self.end_headers()
			self.load_test_editor(user_profile)

		elif form_input[0] == 'username':
			self.end_headers()
			try:
				username = form_input[1].split('&')[0]
				password = form_input[2]
				with open(username + '.json', 'r', encoding='utf-8') as f:
					profile_vars = json.load(f)
			except FileNotFoundError:
				self.load_login_page()

		try:
			user_profile.save()
		except:
			pass
		return



def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
	run()

#!/usr/bin/python3
import json

from Test_creator import Test


class TeacherProfile:
	def __init__(self, username, password):
		self.username = username
		self.password = password 
		self.tests = {}
		self.averages = {}
		self.students = {}

	def save(self):
		for test_name, test in self.tests.items():
			self.tests[test_name] = vars(test)
		with open(self.username + '.json', mode='w', encoding='utf-8') as f:
			json.dump(vars(self), f, indent=4)

	def create_new_test(self, test_name, number_of_choices):
		if test_name == '' or number_of_choices == '':
			with open('Templates/New_test.html', 'r') as html_file:
				html = Template(html_file.read()).render()
			self.wfile.write(bytes(html, 'utf8'))
		number_of_choices = int(number_of_choices)
		new_test = Test(test_name, number_of_choices)
		self.tests[test_name] = new_test
		self.averages[test_name] = new_test.average
		return new_test

	
	def administer_test(self):
		test_name = ''
		password = ''
		while test_name not in self.tests:
			print("\nYour current saved tests are: ")
			for test in self.tests:
				print(test)
			test_name = input("\nWhich test would you like to administer? ")

		student_info = self.tests[test_name].administer()
		student_name = student_info[0]
		student_grade = student_info[1]

		self.averages[test_name] = student_grade

		#Adds the student's score to their current grades in the class
		if student_name not in self.students:
			self.students[student_name] = {}
		self.students[student_name][test_name] = student_grade

		#Requires the correct teacher's password to continue after the test is taken
		#Note: using getpass instead of input protects the user's password as they enter it
		#but inhibits the ability of the testing bot to interact with the program.
		#For full functionality, this could be changed to getpass
		while password != self.password:
			password = input("\nPlease enter the teacher password to continue to the Test Manager: ")
		which_mode(self)

	#Shows each test with the average score of all the students
	def view1(self):
		print("\nTest        Average\n--------------------")
		for name, test in self.tests.items():
			print("{}        {}%".format(name, self.averages[name]))
	
	#Shows the individual student scores for a selected test
	def view2(self):
		which_test = ''
		while which_test not in self.tests:
			print("\nThe tests available to view scores for are:")
			for test_name in self.tests:
				print(test_name)
			which_test = input("Which test would you like to view? ")
		self.tests[which_test].show_results()
	
	#Needs to be able to show a list of each student who has taken any test, along
	#with their test grades and average grade
	def view3(self):
		which_student = ''
		total_grade = 0
		test_counter = 0
		while which_student not in self.students:
			print("\nThe students in your class who have taken tests are::")
			for student_name in self.students:
				print(student_name)
			which_student = input("Which student would you like to view? ")
		print("\nShowing grades for {}:".format(which_student))
		print("\nTest        Grade\n--------------------")
		for test, grade in self.students[which_student].items():
			print("{}          {}".format(test, grade))
			total_grade += grade
			test_counter += 1
		average = round(total_grade / test_counter, 2)
		print("{}'s overall grade for this class is: {}".format(which_student, average))


	#Uses the three helper view functions to show whichever view the teacher selects
	def view_results(self):
		test_view = ''
		test_views = {'1': self.view1, '2': self.view2, '3': self.view3}
		while test_view not in test_views:
			print("\nYour view options are:\n1: View each test with its average\n2: View all student scores for a selected test\n3: View all test scores for a selected student")
			test_view = input(">> ")
		test_views[test_view]()
		which_mode(self)

	#Quit the program when done and save the profile for later using pickle
	def quit(self):
		with open(self.username, 'wb') as save_file:
			pickle.dump(self, save_file, pickle.HIGHEST_PROTOCOL)




#The function which shifts between the three available modes
def which_mode(current_profile):
	mode = ''
	modes = {'1': current_profile.create_test, '2': current_profile.administer_test, '3': current_profile.view_results, 'q': current_profile.quit}
	while mode not in modes:
		mode = input("\n------------------\n1: To create a test, type '1'\n2: To administer a test, type '2'\n3: To view the results of a test, type '3'\nTo quit the Test Manager, type 'q'\n>>")
	modes[mode]()



if __name__ == '__main__':
	current_profile = load_teacher_profile()
	which_mode(current_profile)
	


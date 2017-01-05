#!/usr/bin/python3
import os

from urllib import parse
from collections import OrderedDict


#Possible answer choices for students: reasonable assumption made that teachers 
#will not want to have more than 10 answer choices per question
letters = ['A', "B", "C", "D", "E", "F", "G", "H", "I", "J"]


#Used from within Teachers_aide any time a teacher wants to create a new test
#or interact with an existing test
class Test:
	def __init__(self, name, choices):
		self.name = name
		self.choices = choices
		self.questions = {}
		self.question_list = []
		self.answer_choices = letters[:choices]
		self.scored_students = {}
		self.average = 0
		self.url_name = parse.quote_plus(name)

	def add_question(self, question_text, answers):
		self.questions[question_text] = answers
		self.question_list.append(question_text)

	def administer(self):
		#Clear the terminal so that a student cannot scroll backwards and see test answers
		clear = lambda:os.system('tput reset')
		clear()

		print("-------{}-------".format(self.name))
		student_name = input("Student name: ")
		if student_name in self.scored_students:
			print("That student has already taken this test. Their score was: {}".format(self.scored_students[student_name]))
		else:
			total_correct = 0

			#Change this to work with refactored way of doing question_list
			for question, answers in self.questions.items():
				print("\n{}".format(question))
				for choice in answers[:len(answers) - 1]:
					print("{}: {}".format(letters[answers.index(choice)], choice))
				answer = ''
				while answer not in self.answer_choices:
					answer = input("Your answer choice: ").upper()
				print(answer)
				if answer == answers[self.choices]:
					total_correct += 1
			score = round(total_correct / len(self.questions) * 100, 2)
			#Give student their score immediately
			print("\nThat's the end of the test! Your score was {}%".format(score))

			#Add the student and their score to the list of students who have taken the test
			self.scored_students[student_name] = score

			#And return a new average for all students who have taken the test
			self.average = round(((len(self.scored_students)-1)*self.average + score)/len(self.scored_students), 2)
			return [student_name, self.average]

	def show_results(self):
		print('\nShowing student results for {}:\n---------------------'.format(self.name))
		for student, score in self.scored_students.items():
			print("{}        {}%".format(student, score))
		print("------------\nAverage = {}%".format(self.average))




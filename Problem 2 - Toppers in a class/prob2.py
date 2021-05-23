##Time Complexity: O(n) where n is the number of students

import csv

with open('Student_marks_list.csv', 'r') as student_list:
    students = csv.reader(student_list)
    next(students, None)
    top_names = [None, None, None, None, None, None]
    top_marks = [0, 0, 0, 0, 0, 0]
    (first, second, third) = (None, None, None)
    (first_marks, second_marks, third_marks) = (0, 0, 0)
    for student in students:
    	for i in range(6):
    		if top_marks[i] < int(student[i + 1]):  #checking if the marks of the current student is greater than the current top marks
    			top_marks[i] = int(student[i + 1])
    			top_names[i] = student[0]
    	total = sum([int(mark) for mark in student[1: ]])
    	if first_marks < total:	#Setting the ranks according to the total marks
    		(second_marks, third_marks) = (first_marks, second_marks)
    		first_marks = total
    		(second, third) = (first, second)
    		first = student[0]
    	elif second_marks < total:
    		third_marks = second_marks
    		second_marks = total
    		third = second
    		second = student[0]
    	elif third_marks < total:
    		third_marks = total
    		third = student[0]
    	
    print("Topper in Maths", top_names[0])
    print("Topper in Biology", top_names[1])
    print("Topper in English", top_names[2])
    print("Topper in Physics", top_names[3])
    print("Topper in Chemistry", top_names[4])
    print("Topper in Hindi", top_names[5])
    print("Best students in the class are {}, {}, {}".format(first, second, third))
    	

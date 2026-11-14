import re
import os.path

path = ''

#Finds the python file to be converted

while True:
    path = input("Please input the file name (with .py) > ")
    if (os.path.exists(path)):
        f = open(path, 'r')
        print("exist")
        break
    else:
        path = input("We can't find your file, please enter full path to the file > ")
        try:
            f = open(path, 'r')
            print("exist")
            print("Processing...")
            print("Done!")
            break
        except:
            print('Cannot find')

#Converts the file into an array
lines_0 = f.readlines()

#Function to make tabs for indentation
#Note: for the converter to work each indent in the python code must be 4 spaces
def make_tabs(n):
    str = ""
    for i in range(n):
        str += "    "
    return str

#Function to count how many indentations a line is under
def indent_space(x):
    str = "    "
    count = x.count(str)
    return count

#The code array is where the corresponding pseudocode will be written
#We rewrote the pseudocode onto another array instead of modifying the original one
#so that we still have the original python code as the framework
#This is a technique we use throughout the program

code = []
elif_indent = 0 #The number of indents to be added due to elif statements
indent = 0 #The number of indents in the current line
indent_old = 0 #The number of indents in the previous line

#Removing the new line character at the end of each line to avoid
#string issues later on
if len(lines_0) > 1:
    for i in range(0, len(lines_0)-1):
        lines_0[i] = lines_0[i][:-1]

#The pseudocode framework we followed didn't allow for elif statements
#Instead elif statements were to be expressed as separate else and if statements
#This included modifying the indentation in order to nest these statements inside each other

trigger = 0
for i in lines_0:
    indent = indent_space(i)
    if 'elif' in i:
        code.append(make_tabs(indent+elif_indent)+"else:")
        elif_indent += 1
    if indent_space(i)+1 < indent_old and elif_indent >= 1:
        #If the number of indents of a line is at least 2 less than that of the previous line,
        #that means the nested if and else branch has finished and this is the final else section
        #Therefore the number of indents due to elif statements is reduced by one
        elif_indent -= 1
        trigger += 1
    
    #if the indentation gets reduced significantly again (measured by a variable called trigger)
    #then that means the final else section has been converted and we are out of the nested branch
    #Therefore the number of indents due to elif statements is set back to 0
    if trigger == 2:
        elif_indent = 0

    code.append(make_tabs(elif_indent)+i)
    indent_old = indent

code = [w.replace('elif', 'if') for w in code]

#Warning: Hashtags and comments in the python file may mess with the converter. Please remove
#for maximal accuracy

#--------------------------------------------------------- RETURN AS code

#Finds the position of a string in a line
def find_string(line, obj):
	position = []
	value = 0
	for a in range (0, len(line)- len(obj) + 1):
		appearance = 0
		for b in range (0, len(obj)):
            #checking if each character in the string matches
			if line[a+b] == obj[b]:
				appearance += 1

		if appearance == len(obj):
			for c in range (0, len(obj)):
				position.append(a+c)
                #Returns the position of each character in that string
                #This method prevents duplicate characters being detected by mistake

			value = 1
			break

	if value == 1:
		return position[-1]
        #Returns the final position of the string

#This function makes sure a python command is not inside a string or after a hashtag
def not_in_string_hashtag(line, obj):
    not_in_hashtag = True
    not_in_string = False

    if "#" in line:
        if find_string(line, obj) < find_string(line, "#"):
            not_in_hashtag = True
        else:
            not_in_hashtag = False

    counter = 0
    for i in range (0, find_string(line, obj)+2-len(obj)):
        x = line[i]
        if x == "\"":
            counter += 1
        if counter % 2 == 0 and i == find_string(line, obj)+1-len(obj):
            not_in_string = True
    
    if not_in_string and not_in_hashtag:
        return True

#Creating an array containing information about the indentations for each line
#Note: whenever the python code produces a prompt asking for the input, the
#resulting pseudocode will have 2 lines dedicated to it. One line for outputting
#the prompt and the other asking for the input of a variable.
#for example, variable = input("Type something") will be represented as:
#OUTPUT Type something
#INPUT Variable
#Which is why the number of indents is appended twice
#If there is an int(input("")) command then an extra line is needed, according to
#the pseudocode guide, therefore the number of indents is appended again.
indentation = []

for x in range (0, len(code)):
    i = code[x]
    if 'input("' in i and not_in_string_hashtag(i, 'input("'):
        indentation.append(indent_space(i))
        if " int(" in i and not_in_string_hashtag(i, " int("):
            indentation.append(indent_space(i))
    indentation.append(indent_space(i))

#Since we already have the information of the indentation backed up, we remove
#it from all the lines of code so its easier to perform syntax changes.
code = [j.replace("    " ,'') for j in code]

arr = [] #This array is where the final pseudocode will be written


#Pseudocode involves commands in capital letters
def make_capital(line, obj):
	res = list(line)
	last_letter_position = find_string(line, obj)

	for e in range (len(obj)):
		res[last_letter_position-e] = obj[len(obj)-e-1].capitalize()

	new_line = "".join(res)

	return new_line

#This function converts the for loop into pseudocode
def For(x:str):
    if "for " in x and " range" not in x:
        x = make_capital(x, "for ")
        x = make_capital(x, " in ")
        return x + "\n"
    if "for " and " range" in x:
        lst = x.split('range')
        identify = lst[0]
        identify = identify.split(' ')
        identify = identify[1]
        lst = lst[1]
        lst = lst.strip()
        arr = list(lst)
        arr[0] = ''
        for index in range (len(arr)-1, 0, -1):
            if arr[index] == ')':
                arr[index] = ''
                break
        lst = "".join(arr)
        res = lst.split(',')
		#construction
        if len(res) == 1:
            return("FOR {} <-- 0 TO {}\n".format(identify,res[0]))
        elif len(res) == 2:
            return("FOR {} <-- {} TO{}\n".format(identify,res[0],res[1]))
        elif len(res) == 3:
            return("FOR {} <-- {} TO{} STEP{}\n".format(identify,res[0],res[1],res[2]))

#The pseudocode will be written on a file called result.txt on your computer
fill = open("result.txt", "w")
func = 0

#This mega for loop goes through each line and converts each python command one by one
for i in code:
    q = 1 #if q does not become 0 then the line was not modified so is added to the new array as it is
    i = i.replace("_", "")

    operations = ["+", "-", "/", "*"]

    #Changing the format of the arithmetic of variables
    for x in operations:
        change = x + "="
        variable = ""
        value = ""

        if change in i and not_in_string_hashtag(i, change):
            q = 0
            for y in range (0, find_string(i, change)-2):
                variable += i[y]

            for y in range (find_string(i, change)+2, len(i)):
                value += i[y]

            variable_new = variable.lstrip()
            arr.append(variable + " <-- " + variable_new + " " + x + " " + value+"\n")

    #Converting input prompts into OUTPUT and INPUT statements and converting to integer
    if "input(" in i and not_in_string_hashtag(i, "input("):
        q = 0
        prompt = ""
        variable = ""
        
        if i[-1] == ")" and i[-2] == ")":
            for x in range (find_string(i, "input")+2, len(i)-2):
                prompt += i[x]
        else:
            for x in range (find_string(i, "input")+2, len(i)-1):
                prompt += i[x]

        if prompt != "":
            arr.append("OUTPUT "+prompt+"\n")

        if "int" not in i:
            for x in range (0, find_string(i, "input")-7):
                variable += i[x]

            arr.append("INPUT "+variable+"\n")

        elif not_in_string_hashtag(i, "int"):
            for x in range (0, find_string(i, "input")-11):
                variable += i[x]

            arr.append("INPUT "+variable+"\n")
            arr.append(variable + " <-- " + "STRING_TO_NUM(" + variable + ")"+"\n")

    else:
        if " = " in i and not_in_string_hashtag(i, " = "):
            q = 0
            #Changing the format of the assignment of variables
            i = i.replace(" = ", " <-- ")
            arr.append(i+"\n")

    #Converting print to OUTPUT
    if "print(" in i and not_in_string_hashtag(i, "print("):
        q = 0
        output = ""

        for x in range (find_string(i, "print")+2, len(i)-1):
            output += i[x]

        output = output.replace("+", ", ")
        arr.append("OUTPUT "+ output + "\n")

    #Converting functions into pseudocode
    if "def " in i and not_in_string_hashtag(i, "def "):
        q = 0
        func = 1
        functional = i.split("f ")
        parameter = ""
        start_count = False
        #start_count is used to separate out the parameter of the function
        for x in functional[1]:
            if x == ")":
                start_count = False
            if start_count:
                parameter += x
            if x == "(":
                start_count = True

        if parameter == "":
            action = functional[-1].replace("()", "")
            arr.append("PROCEDURE " + action + "\n")
        else:
            arr.append("FUNCTION " + functional[1]+"\n")

    #The way a function is called is converted to pseudocode
    if '(' in i and ')' in i and func == 1 and not_in_string_hashtag(i, '(') and not_in_string_hashtag(i, ')'):
        lines = i.split('(')
        for x in functional:
            lists = x.split('(')
            if lists[0] == lines[0]:
                arr.append("CALL {} ({}\n".format(lines[0], lines[1]))
                q = 0
    
    #Some syntax changes
    if "return" in i and not_in_string_hashtag(i, "return"):
        i = make_capital(i, "return")
        arr.append(i+"\n")
        q = 0

    if "break" in i and not_in_string_hashtag(i, "break"):
        arr.append("BREAK\n")
        q = 0

    if "continue" in i and not_in_string_hashtag(i, "continue"):
        arr.append("CONTINUE\n")
        q = 0

    #Sorting out the conditional statements and loops
    logic = ["and", "or", "not"]
    for x in logic:
        if x in i and not_in_string_hashtag(i, x) and i[find_string(i, x) - len(x)] == " ":
            i = make_capital(i, x)
            q = 0

    i = i.replace(" == ", " = ")
    i = i.replace(" % ", " MOD ")
    i = i.replace(" != ", " <> ")

    if "if " in i and not_in_string_hashtag(i, "if"):
        arr.append(make_capital(i, "if")+"\n")
        q = 0

    if "else:" in i and not_in_string_hashtag(i, "else"):
        arr.append(make_capital(i, "else")+"\n")
        q = 0

    if "for " in i and not_in_string_hashtag(i, "for"):
        arr.append(For(i))
        q = 0

    if "while " in i and not_in_string_hashtag(i, "while"):
        arr.append(make_capital(i, "while")+"\n")
        q = 0

    if i == "":
        arr.append(i + "\n")
        q = 0
    
    if q != 0:
        arr.append(i + "\n")
    
#Final syntax changes and adding back the indentation
arr = [w.replace(':', '') for w in arr]
arr = [make_tabs(indentation[i]) + arr[i] for i in range (0, len(arr))]

arr = [i.replace(' str(', ' NUM_TO_STRING(') for i in arr]
arr = [i.replace(' int(', ' STRING_TO_NUM(') for i in arr]

#--------------------------------------------------------- RETURN AS arr

#Whenever a loop or conditional statement ends, an ENDFOR or ENDIF statement is added
#including its necessary indentation

stack = []
indent_stack = []
indent = 0
last_indent = indent_space(arr[-1])

#making extra entries in the array for the ENDIF, ENDFOR etc. statements
for j in range(indent_space(arr[-1]) -1, -1, -1):
    arr.append(make_tabs(j))

#Rewriting everything onto another array (code)
code = []

for x in range(0, len(arr)):
    #Making sure the line is not a comment
    if len(arr[x].strip()) != 0:
        if arr[x][0] == '#' or arr[x].strip()[0] == '#':
            code.append(arr[x])
            continue

    #if the indentation decreases that means a loop, conditional statement or function has ended
    #so that is when the END statement is added
    if indent_space(arr[x]) < indent:
        sub = indent - indent_space(arr[x])
        for i in range(sub, 0, -1):
            code.append(make_tabs(indent_stack[-1])+"END"+stack[-1].upper()+'\n')
            indent_stack.pop()
            stack.pop()
    if 'FOR' in arr[x] and not_in_string_hashtag(arr[x], 'FOR'):
        stack.append('for')
        indent_stack.append(indent_space(arr[x]))
    elif 'WHILE' in arr[x] and not_in_string_hashtag(arr[x], 'WHILE'):
        stack.append('while')
        indent_stack.append(indent_space(arr[x]))
    elif 'FUNCTION' in arr[x] and not_in_string_hashtag(arr[x], 'FUNCTION'):
        stack.append('function')
        indent_stack.append(indent_space(arr[x]))
    elif 'PROCEDURE' in arr[x] and not_in_string_hashtag(arr[x], 'PROCEDURE'):
        stack.append('procedure')
        indent_stack.append(indent_space(arr[x]))
    elif 'IF' in arr[x] and not_in_string_hashtag(arr[x], 'IF'):
        stack.append('if')
        indent_stack.append(indent_space(arr[x]))
    elif 'ELSE' in arr[x] and not_in_string_hashtag(arr[x], 'ELSE'):
        stack.append('if')
        indent_stack.append(indent_space(arr[x]))
    code.append(arr[x])
    indent = indent_space(arr[x])

endif = [] #This array is used to find the position of incorrect ENDIF statements

#Some more syntax for loops
for k in range(0, len(code)):
    if 'WHILE ' in code[k] and not_in_string_hashtag(code[k], 'WHILE '):
        code[k] = code[k][:-1] + " DO\n"
    if 'IF ' in code[k] and not_in_string_hashtag(code[k], 'IF'):
        code[k] = code[k][:-1] + " THEN\n"
    if "ELSE" in code[k] and not_in_string_hashtag(code[k], 'ELSE'):
        endif.append(k-1)

endif.reverse()

#'End if' statements should only be added after a pair of if/else branch has finished
#But the original code added 'end if' statements after each if branch had finished as well
#as after each else branch had finished, therefore some 'end if' statements need to be removed

#For example: IF x = 1 THEN
#               x <-- x + 2
#             ENDIF
#             ELSE
#               x <-- x - 1
#             ENDIF
#is corrected to:
#             IF x = 1 THEN
#               x <-- x + 2
#             ELSE
#               x <-- x - 1
#             ENDIF

for z in endif:
    code.pop(z)

#Writing the pseudocode onto a file
for z in code:
    fill.write(z)
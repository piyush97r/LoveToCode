from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from . import functions
import re
import logging
import subprocess
import os
logging.basicConfig(filename='first.log', level=logging.DEBUG,
                    format=' %(asctime)s -%(levelname)s- %(message)s')
# logging.disable(logging.CRITICAL)#->Comment this if debugging


def index(request):
    """
    This is the index Page.
    The if statement is true only when the user enters the contact form.
    The entered data is stored in the file.
    """
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        functions.save_in_file(
            '/Dashboard/files/messages.txt', user_name, email, subject, message)
        return render(request, 'Dashboard/index.html')
    else:
        return render(request, 'Dashboard/index.html')


def signup(request):
    """
    Has 2 parts.
    1->If the request method is POST(i.e if the user enters the data and clicks signup):
           Take the contents from the form and writes in the file(signup.txt).
           Login Page is opened.
    2->Else:
            Signup page is opened.
    """
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        if not functions.check_if_exist('/Dashboard/files/signup.txt', user_name, email):
            logging.debug(
                tuple([user_name, password, email, phone_number]))
            id = functions.save_in_file(
                '/Dashboard/files/signup.txt', user_name, password, email, phone_number)
            functions.create_points_entry(id, -1, 0, user_name)
            # redirect is used because the url is not changed when render is done..
            return redirect('http://127.0.0.1:8000/index/login/')
        else:
            return HttpResponse("The username is already used.....!")
    else:
        return render(request, 'Dashboard/signup.html')


def login(request):
    """
    Has 2 parts.
    1->If the form is not filled it waits and displays the form(else part).
    2->If the form is filled.
           When the login button is clicked then the authentication is done and the respective pages are opened.
    """
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        id = functions.authenticate(
            '/Dashboard/files/signup.txt', user_name, password)
        if id:
            # Saves the username in session(Dictionary like DataStructure).Saving it in session
            # because we cannot pass 2nd argument to redirect...
            request.session['id'] = id
            request.session['username'] = user_name
            return redirect('http://127.0.0.1:8000/index/dashboard/')
        else:
            return HttpResponse("Not Authenticated....!Please Signup First.....!")
    else:
        return render(request, 'Dashboard/login.html')


    
def dashboard(request):
    questions = functions.get_contents('/Dashboard/files/questions.txt')
    questions = (map(lambda x: x.split('|'), questions))
    return render(request, "Dashboard/dashboard.html", {'id': request.session.get('username'),'questions':questions})


def discussion(request):
    """
    Gets the contents from the file and displays it
    If is executed if the comment is done and sibmitted.
    The else part displays the comments.
    """
    if request.method == 'POST':
        comment = request.POST.get('message')
        # Every question has a different file for comments numbered based on their questions.
        # We will take the question number from the url path save the comment in that file.
        #functions.save_in_file('/Dashboard/files/discussions/discussion{}.txt'.format(
        #    request.get_full_path().split('/')[-2]), comment)
        functions.add_username('/Dashboard/files/discussions/discussion{}.txt'.format(request.get_full_path().split('/')[-2]), comment, request.session['username'])
        discussions = functions.get_comments(
            '/Dashboard/files/discussions/discussion{}.txt'.format(request.get_full_path().split('/')[-2]))
        #functions.add_username(request.session['user_name'], '/Dashboard/files/discussions/discussion{}.txt'.format(request.get_full_path().split('/')[-2]))
        # required = []
        # for discussion in discussions:
        #     required.append(discussion.split('###'))
        required = [x.split("###") for x in discussions]
        logging.debug(required)
        required = tuple(map(tuple, required))#Required to get the username of the guy who commented
        return render(request, "Dashboard/discussion.html", {'discussions': required, 'user_name': request.session.get('user_name'), 'length': len(discussions), 'question_number': request.get_full_path().split('/')[-2]})
    else:
        # Since each discussion has its own file for comments we will display the contents only from that file the number is again got from the url path.
        discussions = functions.get_comments(
            '/Dashboard/files/discussions/discussion{}.txt'.format(request.get_full_path().split('/')[-2]))
        required = [x.split("###") for x in discussions]
        required = list(map(tuple, required))
        logging.debug(required)
        return render(request, "Dashboard/discussion.html", {'discussions': required, 'user_name': request.session.get('user_name'), 'length': len(discussions), 'question_number': request.get_full_path().split('/')[-2]})


def practice(request):
    """
    Returns the view of practice.html and pass the questions as dictionary.
    """
    questions = functions.get_contents('/Dashboard/files/questions.txt')
    # This was done to remove the Question number from The questions...(see the questions.txt)..to get an idea
    # temp = []
    # for question in questions:
    #     temp.append(question[2:])
    # questions = temp
    # zip with range is required so that there will be the question numbers along with the question.
    # These question numbers will be seen in the url After a question is clicked
    # questions = zip(questions,range(len(questions)))
    # ->Thought this one line would be much more efficient than the above lines
    questions = (map(lambda x: x.split('|'), questions))
    logging.debug(questions)
    return render(request, 'Dashboard/practice.html', {'questions': questions})


def question(request):
    """
    Returns the page which displays the questions And waits for user to give the answer.
    The files are opened and the contents the sent to the html file.
    """
    # If works only if the answer is written and submitted.
    question_number = request.get_full_path().split('/')[-1]
    request.session['question'] = question_number
    # We should pass the Regular expression to the function
    # '#####' -> is used to deifferentiate between records....
    pattern = re.compile(r'\$\${}.*?#####'.format(question_number), re.DOTALL)
    contents = functions.get_contents(
        "/Dashboard/files/question_details.txt", pattern)
    # '#' -> Each feild is separated by #
    contents = contents.split('#')
    # This is the Header(Question)...Which was selected.
    name = functions.get_question(
        "/Dashboard/files/questions.txt", question_number)
    # if request.method == 'POST':
    #     error = False
    #     success = False
    #     language = request.POST.get('language')
    #     program = request.POST.get('program')
    #     #Get The extension of the program written
    #     if language == 'Python3.6':
    #         #Open a file with the extension found
    #         with open('temp.py','w') as file:
    #             #Write the program in the file
    #             file.write(program)
    #         #Compile
    #         os.popen('python3.5 temp.py 2> error.txt 1>out.txt')
    #     elif language == 'C':
    #         with open('temp.c','w') as file:
    #             file.write(program)
    #         os.popen('cc temp.c 2> error.txt')
    #         os.popen('./a.out 2> error.txt 1> out.txt')
    #     elif language == 'C++':
    #         with open('temp.cpp','w') as file:
    #             file.write(program)
    #         os.popen('cpp temp.cpp 2> error.txt')
    #         os.popen('g++ temp.cpp 2> error.txt 1> out.txt')
    #     elif language == 'Java':
    #         with open('temp.java','w') as file:
    #             file.write(program)
    #         os.popen('javac temp.java 2> error.txt')
    #         os.popen('java temp 2> error.txt 1> out.txt')
    #         logging.debug(os.getcwd())
    #     error_message = open('error.txt').read()
    #     logging.debug(error_message)
    #     if error_message != '':
    #         error = True
    #     else:
    #         success = True
    #     # return redirect(request, "")
    #     # return render(request, "Dashboard/error_or_out.html",{"error":error, "success":success})
    #     return render(request,"Dashboard/question.html",{'task':contents[0],'input_format':contents[1],'output_format':contents[2],'sample_input':contents[3],'sample_output':contents[4],'name':name,'question_number':question_number, 'error':error, 'success':success})
    #     # return redirect("http://127.0.0.1:8000/index/dashboard/practice/question/"+question_number)
    # #Get the question selected we can get this from the path(url)
    # #request.get_full_path() -> Gives the full url....
    # else:
        # Pass all as different because it was not working as expected
    return render(request, "Dashboard/question.html", {'task': contents[0], 'input_format': contents[1], 'output_format': contents[2], 'sample_input': contents[3], 'sample_output': contents[4], 'name': name, 'question_number': question_number, 'error': False, 'success': False})


def leaderboard(request):
    users = functions.get_points()
    logging.debug(users)
    return render(request, "Dashboard/leaderboard.html", {'users': users})


def admin(request):
    return render(request,'Dashboard/admin.html')

def answer(request):
    answer = functions.get_answer(
        "/Dashboard/files/answers.txt", request.get_full_path().split('/')[-2])
    # Question should be sent so that it can go back to that question.....!
    functions.remove_points(request.session['id'], request.session['question'])
    answer = "<br />".join(answer)
    return render(request, "Dashboard/answer.html", {'question_number': request.get_full_path().split('/')[-2], 'answer': answer})


def profile(request):
    if request.method == 'POST':
        username = request.POST.get('new_username')
        #current_password = request.POST['currentPassword']
        password = request.POST.get('newPassword')
        if username:
            functions.update(request.session['username'], request.session['id'], 0, username)
            request.session['username'] = username
        if password:
            functions.update(request.session['username'], request.session['id'], 1, password)
        return render(request, "Dashboard/profile.html", {'u':request.session['username']})
    return render(request, "Dashboard/profile.html", {'u':request.session['username']})


def error_or_out(request):
    """
    Calls as ajax call when the code is written and submitted.....!
    """
    out,error = 0,0
    language = request.POST.get('language')
    program = request.POST.get('program')
    #Get the test cases
    question_number = request.get_full_path().split('/')[-2]
    #pattern = re.compile(r'#{}\n([^#.]*)'.format(question_number), re.DOTALL)
    test_case = re.findall(r'#{}\n([^#.]*)'.format(request.session['question']), open('test_cases.txt').read(), re.DOTALL)
    #logging.debug("question_number is "+question_number+" full path is "+request.get_full_path())
    with open("test_file.txt",'w') as f:
        f.write(test_case[0])
    logging.debug("Question Number is "+request.session['question']+"The test case is "+" ".join(test_case))
    # Get The extension of the program written
    if language == 'Python3.6':
        # Open a file with the extension found
        with open('temp.py', 'w') as file:
            # Write the program in the file
            file.write(program)
        # Compile
        # os.popen('python3.5 temp.py 2> error.txt 1>out.txt') -> subprocess.Popen was much easier.....!
        process = subprocess.Popen('python3.5 temp.py<test_file.txt', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,error = process.communicate()
    elif language == 'C':
        with open('temp.c','w') as file:
            file.write(program)
        # os.popen('cc temp.c 2> error.txt')
        # os.popen('./a.out 2> error.txt 1> out.txt')
        process = subprocess.Popen("cc temp.c", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        error = process.communicate()[-1]#Get only The error Part
        if error.decode("utf-8") == "":
            process = subprocess.Popen("./a.out<test_file.txt", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out,error = process.communicate()
    elif language == 'C++':
        with open('temp.cpp','w') as file:
            file.write(program)
        # os.popen('cpp temp.cpp 2> error.txt')
        # os.popen('g++ temp.cpp 2> error.txt 1> out.txt')
        process = subprocess.Popen("cpp temp.c", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        error = process.communicate()[-1]#Compile Time Error
        if error.decode("utf-8") == "":
            process = subprocess.Popen("g++ temp.c<test_file.txt", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out,error = process.communicate()#Runtime Error
    elif language == 'Java':
        with open('temp.java','w') as file:
            file.write(program)
        # os.popen('javac temp.java 2> error.txt')
        # os.popen('java temp 2> error.txt 1> out.txt')
        process = subprocess.Popen("javac temp.java", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        error = process.communicate()[-1]
        if error.decode("utf-8") == "":
            process = subprocess.Popen("java temp<test_file.txt", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out,error = process.communicate()
    else:
        return HttpResponse("Please Select A Language")
    if error.decode("utf-8") != '':
        response = HttpResponse(error.decode("utf-8").replace('\n','<br/>'))#Convert the error message from Bytes to ascii
        response.status_code = 400
        return response
    else:
        # flag = False
        # question_number = request.get_full_path().split('/')[-1]
        # pattern = re.compile(r'\|1\\n(.*)[^\|]')
        # pattern.findall(open('test_cases.txt'))
        
        # if :
        #     response = HttpResponse("Your code did not pass the Test Case.....")
        #     response.status_code = 400
        #     return response
        #Check if the program passes the test case
        out_file = open("expected_output.txt").read()
        expected_output = re.findall(r'#{}\n([^#.]*)'.format(request.session['question']), out_file, re.DOTALL)
        logging.debug("The Excepted output is "+expected_output[0]+" Actual output is "+out.decode("utf-8"))
        if expected_output[0].strip() != out.decode("utf-8").strip():
            response = HttpResponse("Your code did not pass the test cases.....!")
            response.status_code = 400
            return response
        functions.give_points(request.session['question'],request.session['id'])
        return HttpResponse('Congratulations You Passed the test....!')
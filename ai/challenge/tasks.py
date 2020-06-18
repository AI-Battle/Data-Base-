from celery import shared_task
from challenge import compiler
from challenge.models import Submission

@shared_task
def submission_task(data):
    submit = Submission.objects.filter(id = data['file'])[0]
    if submit.language == 'python': ans = compiler.python(submit.id)
    elif submit.language == 'c++': ans = compiler.cpp(submit.id)
    elif submit.language == 'go': ans = compiler.go(submit.id)
    elif submit.language == 'java': ans = compiler.java(submit.id)
    if ans == 1 :
        pass
        # run the code with id of submission
    else:
        submit.delete()
    return ans
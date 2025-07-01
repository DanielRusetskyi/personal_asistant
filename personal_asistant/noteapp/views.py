from django.shortcuts import render

# Create your views here.

def main(request):
    return render(request, 'noteapp/index.html')

def calendar(request):
    return render(request, 'noteapp/calendar.html')

def task(request):
    return render(request, 'noteapp/task.html')

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from myapp.serializers import StudentSerializer
from myapp.models import Student

@csrf_exempt

def studentApi(request,id=0):
    if request.method == 'GET':
        if id == 0:
            students = Student.objects.all()
            student_serializer = StudentSerializer(students, many=True)
            return JsonResponse(student_serializer.data, safe=False)
        else:
            try:
                student = Student.objects.get(id=id)
                student_serializer = StudentSerializer(student)
                return JsonResponse(student_serializer.data, safe=False)
            except Student.DoesNotExist:
                return JsonResponse({"error": "Student not found"}, status=404)
    elif request.method=='POST':
        student_data=JSONParser().parse(request)
        student_serializer=StudentSerializer(data=student_data)
        if student_serializer.is_valid():
            student_serializer.save()
            return JsonResponse("Added Successfully",safe=False)
        return JsonResponse("Failed to Add",safe=False)
    elif request.method=='PUT':
        student_data=JSONParser().parse(request)
        student=Student.objects.get(id=id)
        student_serializer=StudentSerializer(student,data=student_data)
        if student_serializer.is_valid():
            student_serializer.save()
            return JsonResponse("Updated Successfully",safe=False)
        return JsonResponse("Failed to Update")
    elif request.method=='DELETE':
        student=Student.objects.get(id=id)
        student.delete()
        return JsonResponse("Deleted Successfully",safe=False)

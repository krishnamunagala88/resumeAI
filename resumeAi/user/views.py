from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

@csrf_exempt
def generate_resume(request):
    if request.method == 'POST':
        try:
            # Handle both JSON and form-data
            if request.content_type == "application/json":
                user_data = json.loads(request.body)  # ✅ Parse JSON data correctly
            else:
                user_data = request.POST.dict()  # ✅ Extract form-data
            
            print("Received data:", user_data)  # 🔍 Debug received data

            # Validate data
            fullname = user_data.get("fullname", "").strip()
            if not fullname:
                return JsonResponse({"error": "Fullname not provided"}, status=400)

            # Load the LaTeX template
            template_path = "resume_template.tex"
            if not os.path.exists(template_path):
                return JsonResponse({"error": "Template file not found"}, status=500)

            with open(template_path, "r", encoding="utf-8") as file:
                template_content = file.read()

            # Format responsibilities and project details as LaTeX itemized lists
            def format_list(key):
                items = user_data.get(key, [])
                if isinstance(items, str):
                    items = [items]  # Convert single string to list
                return "\n".join([f"\\item {item}" for item in items]) if items else "\\item None"

            responsibilities1 = format_list("responsibilities1")
            responsibilities2 = format_list("responsibilities2")
            details1 = format_list("details1")
            details2 = format_list("details2")

            # Dictionary of placeholders and values (handling None values)
            placeholders = {
                "fullname": fullname,
                "email": user_data.get("email", ""),
                "phone": user_data.get("phone", ""),
                "linkedin": user_data.get("linkedin", ""),
                "summary": user_data.get("summary", ""),
                "university1": user_data.get("university1", ""),
                "graduation1": user_data.get("graduation1", ""),
                "grade1": user_data.get("grade1", ""),
                "program1": user_data.get("program1", ""),
                "coursework1": user_data.get("coursework1", ""),
                "university2": user_data.get("university2", ""),
                "graduation2": user_data.get("graduation2", ""),
                "grade2": user_data.get("grade2", ""),
                "program2": user_data.get("program2", ""),
                "coursework2": user_data.get("coursework2", ""),
                "category1": user_data.get("category1", ""),
                "skills1": user_data.get("skills1", ""),
                "category2": user_data.get("category2", ""),
                "skills2": user_data.get("skills2", ""),
                "category3": user_data.get("category3", ""),
                "skills3": user_data.get("skills3", ""),
                "company1": user_data.get("company1", ""),
                "location1": user_data.get("location1", ""),
                "position1": user_data.get("position1", ""),
                "duration1": user_data.get("duration1", ""),
                "responsibilities1": responsibilities1,
                "company2": user_data.get("company2", ""),
                "location2": user_data.get("location2", ""),
                "position2": user_data.get("position2", ""),
                "duration2": user_data.get("duration2", ""),
                "responsibilities2": responsibilities2,
                "title1": user_data.get("title1", ""),
                "project_duration1": user_data.get("project_duration1", ""),
                "keyHighlight1": user_data.get("keyHighlight1", ""),
                "details1": details1,
                "title2": user_data.get("title2", ""),
                "project_duration2": user_data.get("project_duration2", ""),
                "keyHighlight2": user_data.get("keyHighlight2", ""),
                "details2": details2
            }

            # Replace placeholders in the template
            for placeholder, value in placeholders.items():
                template_content = template_content.replace(f"{{{{{placeholder}}}}}", value)

            # Save the rendered resume as a .tex file
            output_filename = f"{fullname.replace(' ', '_')}_resume.tex"
            with open(output_filename, "w", encoding="utf-8") as output_file:
                output_file.write(template_content)

            return JsonResponse({"message": "Resume generated successfully!", "filename": output_filename})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

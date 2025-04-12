from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import os
import subprocess
import shutil

def generate_pdf(tex_file: str, cls_file: str, output_dir: str = "output"):
    tex_file = 'resume.tex'
    cls_file = 'resume.cls'

    # Ensure the .cls file is in the same directory as the .tex file
    # shutil.copy(cls_file, cls_file)  # Redundant, but keeping in case of future changes
    
    output_dir = "output"

    try:
        print("I got into try")
        result = subprocess.run(
            
            ["pdflatex", "-output-directory", output_dir, tex_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"PDF successfully created in '{output_dir}'")
    except subprocess.CalledProcessError as e:
        print("Error during PDF generation:")
        print("STDOUT:", e.stdout.decode())
        print("STDERR:", e.stderr.decode())


    
@csrf_exempt
def generate_resume(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('fullname', 'Unknown')
            email = data.get('email', 'unknown@example.com')
            phone = data.get('phone', 'N/A')
            linkedin = data.get('linkedin', 'N/A')
            summary = data.get('summary', 'No summary provided')
            education = data.get('education', [])
            skills = data.get('skills', [])
            experience = data.get('experience', [])
            projects = data.get('projects', [])
            
            # Read the template from a file
            with open('resume_template.tex', 'r', encoding='utf-8') as file:
                template = file.read()
            
            def escape_tex_chars(text):
                return re.sub(r'(\d+)%', r'\1\\%', text.replace('&', '\\&').replace('#', '\\#'))
            
            # Generate the education section dynamically
            education_section = "\\begin{educationSection}{Education}\n"
            for i, edu in enumerate(education):
                university = escape_tex_chars(edu.get('university', 'Unknown University'))
                program = escape_tex_chars(edu.get('program', 'Unknown Program'))
                coursework = escape_tex_chars(edu.get('coursework', 'None'))
                
                education_section += f"    \\educationItem[\n"
                education_section += f"        university={{{university}}},\n"
                education_section += f"        graduation={{{edu.get('graduation', 'Unknown')}}},\n"
                education_section += f"        grade={{{edu.get('grade', 'N/A')}}},\n"
                education_section += f"        program={{{program}}},\n"
                education_section += f"        coursework={{{coursework}}}\n"
                education_section += f"    ]"
                if i < len(education) - 1:
                    education_section += " \\\\ \n"
                else:
                    education_section += "\n"
            education_section += "\\end{educationSection}"
            
            # Generate the skills section dynamically
            skills_section = "\\begin{skillsSection}{Technical Skills}\n"
            for i, skill in enumerate(skills):
                category = escape_tex_chars(skill.get('category', 'Unknown Category'))
                skill_list = escape_tex_chars(skill.get('skills', 'None'))
                
                skills_section += f"    \\skillItem[\n"
                skills_section += f"        category={{{category}}},\n"
                skills_section += f"        skills={{{skill_list}}}\n"
                skills_section += f"    ]"
                if i < len(skills) - 1:
                    skills_section += " \\\\ \n"
                else:
                    skills_section += "\n"
            skills_section += "\\end{skillsSection}"
            
            # Generate the experience section dynamically
            experience_section = "\\begin{experienceSection}{Work Experience}\n"
            for exp in experience:
                company = escape_tex_chars(exp.get('company', 'Unknown Company'))
                location = escape_tex_chars(exp.get('location', 'Unknown Location'))
                position = escape_tex_chars(exp.get('position', 'Unknown Position'))
                duration = escape_tex_chars(exp.get('duration', 'Unknown Duration'))
                
                experience_section += f"    \\experienceItem[\n"
                experience_section += f"        company={{{company}}},\n"
                experience_section += f"        location={{{location}}},\n"
                experience_section += f"        position={{{position}}},\n"
                experience_section += f"        duration={{{duration}}}\n"
                experience_section += f"    ]\n"
                experience_section += f"    \\begin{{itemize}}\n"
                experience_section += f"        \\itemsep -6pt {{}}\n"
                for item in exp.get('responsibilities', []):
                    experience_section += f"        \\item {escape_tex_chars(item)}\n"
                experience_section += f"    \\end{{itemize}}\n"
            experience_section += "\\end{experienceSection}"
            
            # Generate the projects section dynamically
            projects_section = "\\begin{experienceSection}{Projects}\n"
            for proj in projects:
                title = escape_tex_chars(proj.get('title', 'Unknown Project'))
                duration = escape_tex_chars(proj.get('duration', 'Unknown Duration'))
                key_highlight = escape_tex_chars(proj.get('keyHighlight', ''))
                
                projects_section += f"    \\projectItem[\n"
                projects_section += f"        title={{{title}}},\n"
                projects_section += f"        duration={{{duration}}},\n"
                projects_section += f"        keyHighlight={{{key_highlight}}}\n"
                projects_section += f"    ]\n"
                projects_section += f"    \\begin{{itemize}}\n"
                projects_section += f"        \\itemsep -6pt {{}}\n"
                for item in proj.get('details', []):
                    projects_section += f"        \\item {escape_tex_chars(item)}\n"
                projects_section += f"    \\end{{itemize}}\n"
            projects_section += "\\end{experienceSection}"
            
            # Replace placeholders with actual values
            resume_text = (template
                .replace('$$fullname$$', full_name)
                .replace('$$email$$', email)
                .replace('$$phone$$', phone)
                .replace('$$linkedin$$', linkedin)
                .replace('$$summary$$', summary)
                .replace('$$education$$', education_section)
                .replace('$$skills$$', skills_section)
                .replace('$$experience$$', experience_section)
                .replace('$$projects$$', projects_section)
            )
            
            # Save the updated content into a new file
            # filename = f"{full_name.replace(' ', '_')}.tex"
            # with open(filename, 'w', encoding='utf-8') as output_file:
            #     output_file.write(resume_text)

            # from resume_text you are writing into resume.tex
            filename = "resume.tex"
            with open(filename, 'w', encoding='utf-8') as output_file:
                output_file.write(resume_text) 
            
            base_dir = os.path.dirname(__file__)
            tex_path = os.path.join(base_dir, 'resume.tex')
            cls_path = os.path.join(base_dir, 'resume.cls')
            output_dir = os.path.join(base_dir, 'pdf_output')

            # Call the function correctly
            generate_pdf(tex_path, cls_path, output_dir)

            return JsonResponse({'message': f'Resume saved as {filename}'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except FileNotFoundError:
            return JsonResponse({'error': 'Template file not found'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

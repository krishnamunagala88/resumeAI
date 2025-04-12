from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import pytesseract
from PIL import Image
import spacy
import json
import requests
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import os
import subprocess
import shutil

def generate_pdf(tex_file: str, cls_file: str, output_dir: str = "output_modified"):
    tex_file = 'updated_resume.tex'
    cls_file = 'resume.cls'

    # Ensure the .cls file is in the same directory as the .tex file
    # shutil.copy(cls_file, cls_file)  # Redundant, but keeping in case of future changes
    
    output_dir = "output_modified"

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

# Function to extract keywords from job description (unchanged)
def extract_keywords(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and token.pos_ in {"NOUN", "ADJ", "VERB"}]
    return set(keywords)

# Use Gemini API for intelligent updates
def integrate_keywords(resume_text, keywords):
    print(keywords)
    prompt = f"""
    Here is a resume (LaTeX format):
    {resume_text}

    Below are some job description keywords:
    {', '.join(keywords)}

    Rewrite the *content* of the resume (between `\\\documentclass{{resume}}` and `\\end{{document}}`) to naturally include these keywords while maintaining professionalism, coherence, and correct LaTeX syntax. Just give me the updated resume *content* as a string.  Make sure the LaTeX code is valid and will compile. Make sure the length remains almost the same that fits in one page without exceeding and the structure should be same.
    It should *not* exceed one page, the word count should remain same, it can be 2 words less not more at all.
    I repeat the amount of content should remain same with that of the original latex file.
    Critically, maintain the \\\\ double backslash between educationItem and skillItem entries, and between skillItem entries within the skillsSection, to prevent formatting errors. 
    Critically, also maintain the introduction mandatory, sometimes it is getting missed out.
    The LaTeX syntax should remain intact always, including special characters and symbols.
    """

    api_key = "AIzaSyD7w5kNVdkd9S2UcgJcO6h2L35YzJw43Ko"  # Replace with your actual Gemini API key
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        updated_resume_content = result['candidates'][0]['content']['parts'][0]['text']

        # Remove code fences (```tex and ''')
        updated_resume_content = updated_resume_content.replace("```tex", "").replace("'''", "").strip()

        # Extract the body of the original resume
        body_start = resume_text.find(r"\begin{document}") + len(r"\begin{document}")
        body_end = resume_text.rfind(r"\end{document}")
        original_body = resume_text[body_start:body_end].strip()

        # Replace the original body with the updated content
        interim_resume = resume_text[:body_start] + "\n" + updated_resume_content + "\n" + resume_text[body_end:]

        # --- NEW: Call Gemini again to correct LaTeX errors ---
        correction_prompt = f"""
        Here is a LaTeX resume:
        {interim_resume}

        Please correct any LaTeX syntax errors, remove any extra text outside of the LaTeX document structure (like "latex" at the beginning), and ensure that the LaTeX code will compile without errors.  
        Return only the corrected LaTeX code. 
        Do not include explanations.Make sure the length remails almost same with no less or more that fits in one page without exceeding and the structure should be same
        """

        correction_data = {
            "contents": [{"parts": [{"text": correction_prompt}]}]
        }

        correction_response = requests.post(url, headers=headers, json=correction_data)
        correction_response.raise_for_status()
        corrected_resume = correction_response.json()['candidates'][0]['content']['parts'][0]['text']
        corrected_resume = corrected_resume.replace("```latex", "").replace("'''", "").strip()  # Remove code fences

        return corrected_resume

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Gemini API: {e}")
        return None

    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini API response: {e}")
        print(response.text) # Print the raw response for debugging
        return None

@csrf_exempt
def update_resume(request):
    if request.method == 'POST':
        try:
            # Define paths to the files
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resume_path = os.path.join(BASE_DIR, 'resume.tex')
            job_description_path = os.path.join(BASE_DIR, 'job_description.txt')

            # Read the job description
            with open(job_description_path, "r") as f:
                job_description = f.read()

            # Read the resume
            with open(resume_path, "r") as f:
                latex_content = f.read()

            # Extract keywords
            keywords = extract_keywords(job_description)

            # Integrate keywords into the resume
            updated_resume = integrate_keywords(latex_content, keywords)

            if updated_resume:
                # Save the updated resume to a file
                updated_resume_path = os.path.join(BASE_DIR, 'updated_resume.tex')
                with open(updated_resume_path, "w", encoding="utf-8") as f:
                    f.write(updated_resume)

                # Return the updated resume content as a JSON response
                response = JsonResponse({'updated_resume': updated_resume})
                response['Content-Disposition'] = 'attachment; filename="updated_resume.tex"'

                base_dir = os.path.dirname(__file__)
                tex_path = os.path.join(base_dir, 'updated_resume.tex')
                cls_path = os.path.join(base_dir, 'resume.cls')
                output_dir = os.path.join(base_dir, 'pdf_output1')
                # Call the function correctly
                generate_pdf(tex_path, cls_path, output_dir)
                return response
            else:
                return JsonResponse({'error': 'Failed to update resume.'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
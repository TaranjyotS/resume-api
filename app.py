from flask import Flask, render_template, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import torch
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Set upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt', 'rtf'}

# Load pre-trained GPT-2 model (You can replace this with GPT-Neo or GPT-J)
model_name = "gpt2"  # You can also use "EleutherAI/gpt-neo-1.3B"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to split text into chunks for long inputs
def split_text_into_chunks(text, max_length=1024):
    tokens = tokenizer.encode(text)
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    return chunks

# Function to generate the cover letter
def generate_cover_letter(job_description, resume_text):
    # Split job description and resume into chunks
    job_description_chunks = split_text_into_chunks(job_description)
    resume_chunks = split_text_into_chunks(resume_text)

    cover_letter = ""
    for chunk in job_description_chunks + resume_chunks:
        input_text = tokenizer.decode(chunk, skip_special_tokens=True)
        inputs = tokenizer.encode(input_text, return_tensors="pt")
        
        # Set attention mask and pad_token_id for the generation process
        attention_mask = torch.ones(inputs.shape, device=inputs.device)
        pad_token_id = tokenizer.eos_token_id

        # Use max_new_tokens to generate the desired output length
        outputs = model.generate(inputs, attention_mask=attention_mask, pad_token_id=pad_token_id, max_new_tokens=500, num_return_sequences=1, no_repeat_ngram_size=2)
        cover_letter += tokenizer.decode(outputs[0], skip_special_tokens=True) + "\n"

    return cover_letter

# Function to generate ATS optimized resume
def generate_ats_resume(job_description, resume_text):
    resume_template = f"Based on the job description '{job_description}', generate an ATS-optimized resume for the following resume text:\n{resume_text}"
    inputs = tokenizer.encode(resume_template, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=600, num_return_sequences=1, no_repeat_ngram_size=2)
    ats_resume = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return ats_resume

# Function to generate personalized email
def generate_email(job_description):
    input_text = f"Generate a personalized email to apply for the following job: {job_description}"
    inputs = tokenizer.encode(input_text, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=300, num_return_sequences=1, no_repeat_ngram_size=2)
    email = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return email

# Function to generate LinkedIn message
def generate_linkedin_message(job_description):
    input_text = f"Generate a 300-character LinkedIn message for applying to the following job: {job_description}"
    inputs = tokenizer.encode(input_text, return_tensors="pt")
    outputs = model.generate(inputs, max_length=300, num_return_sequences=1, no_repeat_ngram_size=2)
    linkedin_msg = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return linkedin_msg

# Function to generate company overview
def generate_company_overview(job_description):
    company_info = f"Provide an overview of a company hiring for the role: {job_description}. Include its goals, recent developments, projects, hiring process, and salary range."
    inputs = tokenizer.encode(company_info, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=600, num_return_sequences=1, no_repeat_ngram_size=2)
    company_overview = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return company_overview

# Function to generate culture fit questions
def generate_culture_fit_questions(job_description):
    culture_fit = f"Generate a set of culture fit questions with answers for the role: {job_description}"
    inputs = tokenizer.encode(culture_fit, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=600, num_return_sequences=1, no_repeat_ngram_size=2)
    culture_fit_questions = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return culture_fit_questions

# Function to generate mock interview
def generate_mock_interview(job_description):
    interview = f"Generate a mock interview for the role: {job_description}"
    inputs = tokenizer.encode(interview, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=600, num_return_sequences=1, no_repeat_ngram_size=2)
    mock_interview = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return mock_interview

# Flask route to handle form submissions
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.form['job_description']
        resume = request.files['resume']
        
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)

            # Extract resume text (assuming a text file, modify for PDF/Word parsing)
            try:
                with open(resume_path, 'r', encoding='utf-8', errors='ignore') as file:
                    resume_text = file.read()
            except UnicodeDecodeError as e:
                return jsonify({"error": f"Error reading file: {str(e)}"})

            # Generate content
            cover_letter = generate_cover_letter(job_description, resume_text)
            ats_resume = generate_ats_resume(job_description, resume_text)
            email = generate_email(job_description)
            linkedin_msg = generate_linkedin_message(job_description)
            company_overview = generate_company_overview(job_description)
            culture_fit_questions = generate_culture_fit_questions(job_description)
            mock_interview = generate_mock_interview(job_description)

            # Return generated content to the user
            return render_template('result.html', cover_letter=cover_letter,
                                   ats_resume=ats_resume, email=email,
                                   linkedin_msg=linkedin_msg, company_overview=company_overview,
                                   culture_fit_questions=culture_fit_questions,
                                   mock_interview=mock_interview)

    return render_template('index.html')

# Handle file upload logic here
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return 'No resume file part'
    resume = request.files['resume']
    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(resume_path)
        return jsonify({'message': 'Resume uploaded successfully'})
    else:
        return jsonify({'error': 'Invalid file format. Please upload a valid resume.'})

if __name__ == '__main__':
    app.run(debug=True)

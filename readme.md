# Resume Job Matcher

## Quick Setup for Evaluation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   Create a `.env` file with your API keys:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

3. **Run the Application:**
   ```bash
   python run_server.py
   ```

4. **Access Web Interface:**
   Open `http://127.0.0.1:5000` in your browser

5. **Test with Sample Data:**
   - Upload any job description (PDF/TXT/DOCX)
   - Upload a ZIP file containing resume PDFs
   - Watch the AI analyze and rank candidates in real-time

## Overview

**Resume Job Matcher** is a Python script that automates the process of matching resumes to a job description using AI. It leverages the Anthropic Claude API or OpenAI's GPT API to analyze resumes and provide a match score along with personalized email responses for candidates.


## Features

- 🔥 **Comprehensive Resume Processing**
  - Multiple outputs: PDF and Markdown generation
  - Standardization for fair evaluation
  - Font customization (sans-serif, serif, monospace)
  - Command-line options for flexibility

- 🧠 **Advanced AI-Powered Analysis**
  - Resume-job comparison using Claude/GPT API
  - Dual AI support with runtime selection
  - Efficient model interaction
  - Structured data handling with Pydantic

- 📊 **In-depth Evaluation & Scoring**
  - Smart parsing with PyPDF2
  - Multi-factor assessment: skills, experience, education, certifications
  - Visual and content-based quality assessment
  - 🚩 Red flag detection in critical areas
  - Detailed scoring with emoji and color-coded results

- 📈 **Comprehensive Analytics & Reporting**
  - Statistical insights: top, average, median, standard deviation scores
  - Candidate distribution summary
  - Match analysis with improvement suggestions
  - Job description optimization recommendations

- 🌐 **Enhanced Candidate Profiling**
  - Website integration for improved matching
  - Personalized email generation

- 🛠️ **Robust System Management**
  - Advanced logging and error handling
  - Improved user feedback and reliability


## Usage

### Web Application (Recommended)

For the best user experience, use the modern web interface:

```bash
python run_server.py
```

Then open your browser to `http://127.0.0.1:5000` to access the web interface with:
- Drag-and-drop file uploads
- Real-time processing status
- Interactive results dashboard
- Direct candidate contact features

### Command Line Interface

Alternatively, run the script directly with CLI options:

```bash
python resume_matcher.py [--sans-serif|--serif|--mono] [--pdf] [job_desc_file] [pdf_folder]
```

- Use `--sans-serif`, `--serif`, or `--mono` to select a font preset
- Use `--pdf` to generate PDF versions of unified resumes
- Optionally specify custom paths for the job description file and PDF folder

### Cloud Deployment (Render)

For hosting on Render.com:

1. **Push to GitHub**: Upload your code to a GitHub repository
2. **Connect to Render**: 
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Choose "Web Service"
3. **Configure Environment**:
   - Set `OPENROUTER_API_KEY` in environment variables
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app --timeout 300`
4. **Deploy**: Render will automatically build and deploy your app

📋 **See `RENDER_DEPLOYMENT.md` for detailed deployment instructions**

## Customization

### Adjust Logging Level

Modify the logging level at the beginning of the script:

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### Change Scoring Model

To change the AI model used, update the `model` parameter in the `match_resume_to_job` function:

```python
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    ...
)
```

### Modify AI Provider

To switch between Anthropic and OpenAI APIs, modify the `choose_api` function call at the beginning of the script:

```python
def choose_api():
    global chosen_api
    prompt = "Use OpenAI API instead of Anthropic? [y/N]: "
    choice = input(colored(prompt, "cyan")).strip().lower()
    
    if choice in ["y", "yes"]:
        chosen_api = "openai"
    else:
        chosen_api = "anthropic"
```

### Adjust AI Model

To change the AI model used, update the `model` parameter in the `talk_fast` function:

```python
response = client.chat.completions.create(
    model="gpt-4o",  # Change this to the desired model
    ...
)
```

## Score Calculation

The final score for each resume is calculated using a combination of two factors:

1. **AI-Generated Match Score (75% weight)**: This score is based on how well the resume matches the job description, considering factors such as skills, experience, education, and other relevant criteria.

2. **Resume Quality Score (25% weight)**: This score assesses the visual appeal and clarity of the resume itself, including formatting, layout, and overall presentation.

The calculation process is as follows:

1. The AI-generated match score and the resume quality score are both normalized to a 0-100 scale.
2. A weighted average is calculated: 
   `(AI_Score * 0.75 + Quality_Score * 0.25)`
3. The result is clamped to ensure it falls within the 0-100 range.

This combined approach ensures that both the content relevance and the presentation quality of the resume are taken into account in the final score.

### Modify Scoring Criteria

Adjust the scoring logic in the `match_resume_to_job` function's prompt as needed to better fit your specific requirements.

## Troubleshooting

### Common Issues

- **No Resumes Found**: Ensure that resume PDFs are placed in the correct directory (`src` by default).
- **Job Description Not Found**: Confirm that `job_description.txt` exists in the script's directory or provide the correct path.
- **API Key Errors**: Verify that the `CLAUDE_API_KEY` environment variable is set correctly.
- **Dependency Errors**: Install all required Python packages using `pip`.

### Adjusting Timeouts and Retries

If you experience network-related errors when fetching personal websites, you may adjust the `timeout` parameter in the `check_website` function.

```python
response = requests.get(url, timeout=10)
```

## Best Practices

- **Data Privacy**: Ensure that all candidate data is handled in compliance with relevant data protection laws and regulations.
- **API Usage**: Be mindful of API rate limits and usage policies when using the Anthropic Claude API.

## Project Overview

This project was developed for a hackathon to demonstrate AI-powered resume matching capabilities. It showcases how modern AI can streamline the recruitment process by automatically analyzing and scoring candidate resumes against job requirements.

## Acknowledgments

- **Anthropic Claude API**: For providing advanced AI capabilities.
- **OpenAI GPT API**: For additional AI-powered analysis capabilities.

---

Enjoy using the Resume Job Matcher script to streamline your recruitment process!

## Python Packages

The following Python packages are required for this project:

- PyPDF2: For extracting text from PDF resumes
- anthropic: To interact with the Anthropic Claude API for AI-powered analysis
- tqdm: For displaying progress bars during processing
- termcolor: To add colored output in the console
- json5: For parsing JSON-like data with added flexibility
- requests: To make HTTP requests for fetching website content
- beautifulsoup4: For parsing HTML content from personal websites
- openai: To interact with the OpenAI API for AI-powered analysis
- pydantic: For data validation and settings management using Python type annotations

To install these packages, you can use pip:

```bash
pip install PyPDF2 anthropic openai tqdm termcolor json5 requests beautifulsoup4 pydantic
```


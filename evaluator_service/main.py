import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WORKING_MODEL_NAME = None

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    # List available models and find a working one
    try:
        models = genai.list_models()
        print("Available Gemini models:")
        model_names_to_try = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                print(f"  - {model_name}")
                model_names_to_try.append(model_name)
        
        # Try to find a working model
        for model_name in model_names_to_try:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content("test")
                WORKING_MODEL_NAME = model_name
                print(f"\n✓ Using model: {WORKING_MODEL_NAME}")
                break
            except Exception as e:
                continue
        
        if not WORKING_MODEL_NAME:
            print("\n⚠ Warning: Could not find a working model. Will try common names at runtime.")
    except Exception as e:
        print(f"Could not list models: {e}")

app = FastAPI()

class QuestionRequest(BaseModel):
    role: str
    num_questions: int = 5

class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    role: str # Optional: for role-specific evaluation criteria

class Question(BaseModel):
    id: int
    text: str

class EvaluationResult(BaseModel):
    score: float
    feedback: str

# In-memory store for questions (replace with actual Gemini API call)
mock_questions_db = {
    "software_engineer": [
        Question(id=1, text="Explain the difference between a list and a tuple in Python."),
        Question(id=2, text="What is a REST API?"),
        Question(id=3, text="Describe the concept of Object-Oriented Programming."),
    ],
    "product_manager": [
        Question(id=1, text="How do you prioritize features for a new product?"),
        Question(id=2, text="What are some common KPIs for a SaaS product?"),
    ]
}

@app.post("/fetch-questions", response_model=list[Question])
async def fetch_questions(request: QuestionRequest):
    """
    Fetches role-based questions.
    Currently uses a mock database. Will be replaced with Gemini API.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    try:
        # Try to use the working model, or try common model names
        model_names = [WORKING_MODEL_NAME] if WORKING_MODEL_NAME else []
        model_names.extend(['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro'])
        
        model = None
        for model_name in model_names:
            if not model_name:
                continue
            try:
                model = genai.GenerativeModel(model_name)
                break
            except:
                continue
        
        if not model:
            raise Exception("No working Gemini model found")
            
        prompt = f"Generate {request.num_questions} interview questions for a {request.role} role. Provide only the questions, each on a new line."
        response = model.generate_content(prompt)
        
        questions_text = response.text.strip().split('\n')
        questions = [Question(id=i+1, text=q.strip()) for i, q in enumerate(questions_text) if q.strip()]
        
        if not questions:
            raise HTTPException(status_code=404, detail=f"Could not generate questions for role: {request.role}")
        return questions
    except Exception as e:
        print(f"Error fetching questions from Gemini: {e}")
        # Fallback to mock questions if Gemini fails
        if request.role in mock_questions_db:
            return mock_questions_db[request.role][:request.num_questions]
        raise HTTPException(status_code=500, detail=f"Error fetching questions from Gemini API and no mock questions available for role: {request.role}. Error: {str(e)}")


@app.post("/evaluate-answer", response_model=EvaluationResult)
async def evaluate_answer(request: AnswerEvaluationRequest):
    """
    Evaluates an answer using NLP models.
    Currently returns a mock evaluation. Will be replaced with SpaCy/HuggingFace or Gemini API.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    try:
        # Try to use the working model, or try common model names
        model_names = [WORKING_MODEL_NAME] if WORKING_MODEL_NAME else []
        model_names.extend(['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro'])
        
        model = None
        for model_name in model_names:
            if not model_name:
                continue
            try:
                model = genai.GenerativeModel(model_name)
                break
            except:
                continue
        
        if not model:
            raise Exception("No working Gemini model found")
            
        prompt = f"""Evaluate the following answer for the question:
        Question: "{request.question}"
        Answer: "{request.answer}"
        Role (for context, if applicable): "{request.role}"

        Provide a score from 0.0 to 1.0 (e.g., 0.75) and brief feedback.
        Format your response as:
        Score: [score]
        Feedback: [feedback]
        """
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        score_line = next((line for line in response_text.split('\n') if line.startswith("Score:")), None)
        feedback_line = next((line for line in response_text.split('\n') if line.startswith("Feedback:")), None)

        if not score_line or not feedback_line:
            raise HTTPException(status_code=500, detail="Could not parse evaluation from Gemini API.")

        score_str = score_line.replace("Score:", "").strip()
        feedback = feedback_line.replace("Feedback:", "").strip()
        
        try:
            score = float(score_str)
        except ValueError:
            raise HTTPException(status_code=500, detail=f"Could not parse score '{score_str}' from Gemini API response.")

        return EvaluationResult(score=score, feedback=feedback)
    except Exception as e:
        print(f"Error evaluating answer with Gemini: {e}")
        # Fallback to mock evaluation
        return EvaluationResult(score=0.75, feedback="This is a mock evaluation. The answer seems plausible.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
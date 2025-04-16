from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv
from fastapi import HTTPException




class RequestModel(BaseModel):
    message: str
async def getAnswer(request : RequestModel):
    try:
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        ENV_PATH = os.path.join(BASE_DIR, '.env')
        load_dotenv(dotenv_path=ENV_PATH)

        api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        msg = request.message
        print("request from users is " + msg)
        response = client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-01-21",
                contents = msg
        )
        return {"Message": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

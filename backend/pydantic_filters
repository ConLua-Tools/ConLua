from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    name: str

class UserLogin(BaseModel):
    email: EmailStr

class QuestionRequest(BaseModel):
    question: str
    mode: str = "hybrid"

class CustomAIRequest(BaseModel):
    name: str
    description: str

class QuestionResponse(BaseModel):
    answer: str
    mode: str
    status: str

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    message: str

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "Student"
COLLECTION_NAME = "marks"

# MongoDB Connection
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Pydantic Models
class Student(BaseModel):
    name: str
    tenth: float
    twelfth: float
    graduation: float

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    tenth: Optional[float] = None
    twelfth: Optional[float] = None
    graduation: Optional[float] = None

# Helper function to serialize MongoDB document
def serialize_student(student):
    student["_id"] = str(student["_id"])
    return student

# Create - Add new student
@app.post("/students/")
async def add_student(student: Student):
    result = await collection.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

# Read - Get all students
@app.get("/students/", response_model=list[dict])
async def get_all_students():
    students = await collection.find().to_list(100)
    return [serialize_student(student) for student in students]

# Read - Get single student by ID
@app.get("/students/{student_id}")
async def get_student(student_id: str):
    if (student := await collection.find_one({"_id": ObjectId(student_id)})) is not None:
        return serialize_student(student)
    raise HTTPException(status_code=404, detail="Student not found")

# Update - Full update of student data
@app.put("/students/{student_id}")
async def update_student(student_id: str, student: Student):
    result = await collection.replace_one(
        {"_id": ObjectId(student_id)},
        student.dict()
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

# Delete - Remove student by ID
@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
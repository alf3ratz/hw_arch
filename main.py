from fastapi import FastAPI, Request
import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import re
import uvicorn
import random

app = FastAPI(title="Student Service API", description="API для поиска студентов", version="1.0")
api = jsonrpc.Entrypoint('/api/v1/jsonrpc')

students_db = [
    {
        "id": 1,
        "name": "Иван Иванов Иванович",
        "age": 20,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 2,
        "name": "Мария Петрова Сидорова",
        "age": 22,
        "gender": "Женский",
        "attendance": {"Лекция 1": True, "Лекция 2": True},
        "grades": {"Математика": 5, "Физика": 4}
    },
    {
        "id": 3,
        "name": "Иван Иванов Иванович",
        "age": 20,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 4,
        "name": "Иван Иванов Иванович",
        "age": 90,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 5,
        "name": "Иван Иванов Иванович",
        "age": 20,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 6,
        "name": "Иван Иванов Иванович",
        "age": 44,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 7,
        "name": "Иван Иванов Иванович",
        "age": 29,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    },
    {
        "id": 8,
        "name": "Иван Иванов Иванович",
        "age": 25,
        "gender": "Мужской",
        "attendance": {"Лекция 1": True, "Лекция 2": False},
        "grades": {"Математика": 10, "Физика": 10}
    }
]


def full_text_search(query, text):
    return bool(re.search(query, text, re.IGNORECASE))


class SearchStudentsRequest(BaseModel):
    name: Optional[str] = Field(None, description="ФИО студента")
    age: Optional[int] = Field(None, description="Возраст студента")
    gender: Optional[str] = Field(None)
    lecture_presence: Optional[bool] = Field(None)
    lecture_name: Optional[str] = Field(None)
    total_attendance: Optional[int] = Field(None)
    avg_grade: Optional[float] = Field(None)
    sort_by: Optional[List[Tuple[str, str]]] = Field(None)
    page: int = Field(1)
    per_page: int = Field(10)


class AttendanceItem(BaseModel):
    lecture: str = Field(...)
    present: bool = Field(...)


class GradesItem(BaseModel):
    subject: str = Field(...)
    grade: float = Field(...)


class StudentResult(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    age: int = Field(...)
    gender: str = Field(...)
    attendance: List[AttendanceItem] = Field(...)
    grades: List[GradesItem] = Field(...)


class SearchStudentsResponse(BaseModel):
    result: List[StudentResult] = Field(...)


@api.method()
async def search_students(request: Request, params: SearchStudentsRequest) -> SearchStudentsResponse:
    filtered_students = students_db

    if params.name:
        filtered_students = [s for s in filtered_students if full_text_search(params.name, s["name"])]

    if params.age is not None:
        filtered_students = [s for s in filtered_students if s["age"] == params.age]

    if params.gender:
        filtered_students = [s for s in filtered_students if s["gender"] == params.gender]

    if params.lecture_name and params.lecture_presence is not None:
        filtered_students = [s for s in filtered_students if
                             s["attendance"].get(params.lecture_name) == params.lecture_presence]

    if params.total_attendance is not None:
        filtered_students = [s for s in filtered_students if sum(s["attendance"].values()) == params.total_attendance]

    if params.avg_grade is not None:
        filtered_students = [s for s in filtered_students if
                             sum(s["grades"].values()) / len(s["grades"]) == params.avg_grade]


    if params.sort_by:
        for key, order in reversed(params.sort_by):
            filtered_students.sort(key=lambda x: x[key], reverse=(order == "desc"))

    start = (params.page - 1) * params.per_page
    end = start + params.per_page
    paginated_students = filtered_students[start:end]

    result = []
    for student in paginated_students:
        attendance_items = [AttendanceItem(lecture=lec, present=pres) for lec, pres in student["attendance"].items()]
        grades_items = [GradesItem(subject=subj, grade=grade) for subj, grade in student["grades"].items()]
        result.append(StudentResult(
            id=student["id"],
            name=student["name"],
            age=student["age"],
            gender=student["gender"],
            attendance=attendance_items,
            grades=grades_items
        ))

    return SearchStudentsResponse(result=result)

@api.method()
async def get_student_by_id():
    print("get_student_by_id")

app = jsonrpc.API()
app.bind_entrypoint(api)

if __name__ == "__main__":
    print("Сервис запущен на http://localhost:5000")
    for i in range(1, 10):
        random_number = random.randint(1, 100)
        student = {
            "id": i,
            "name": "Иван Иванов Иванович",
            "age": random_number,
            "gender": "Мужской",
            "attendance": {"Лекция 1": True, "Лекция 2": False},
            "grades": {"Математика": 10, "Физика": 10}
        }
        students_db.append(student)
    uvicorn.run(app, host="0.0.0.0", port=5000)

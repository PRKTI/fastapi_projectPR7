import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="FastAPIPractice",
    description="First FastAPI application",
    docs_url="/docs",
    redoc_url="/redoc",
)

DATA_FILE = Path("src/fastapi_project/data.json")

class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    genre: str
    price: float
    in_stock: bool


def load_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(payload: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


data = load_data()


@app.get("/books", response_model=list[Book])
async def get_books():
    return data["books"]


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    for book in data["books"]:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с id={book_id} не найдена",
    )


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    for existing in data["books"]:
        if existing["id"] == book.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Книга с id={book.id} уже существует",
            )
    new_book = book.model_dump()
    data["books"].append(new_book)
    save_data(data)
    return new_book


@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, updated_book: Book):
    for idx, book in enumerate(data["books"]):
        if book["id"] == book_id:
            book_data = updated_book.model_dump()
            book_data["id"] = book_id
            data["books"][idx] = book_data
            save_data(data)
            return book_data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с id={book_id} не найдена",
    )


@app.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(book_id: int):
    for idx, book in enumerate(data["books"]):
        if book["id"] == book_id:
            deleted = data["books"].pop(idx)
            save_data(data)
            return {"message": "Книга удалена", "deleted_book": deleted}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с id={book_id} не найдена",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
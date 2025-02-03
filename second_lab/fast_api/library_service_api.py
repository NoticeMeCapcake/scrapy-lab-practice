from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

client = MongoClient("mongodb://root:password@localhost:27017/")
db = client['books_db']
collection = db['books']

class Book(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    price_amount: Optional[str] = None
    price_currency: Optional[str] = None
    rating_value: Optional[str] = None
    rating_count: Optional[str] = None
    publication_year: str
    isbn: str
    pages_cnt: str
    publisher: Optional[str] = None
    book_cover: Optional[str] = None
    source_url: str

@app.get("/book", response_model=Book)
def get_book(isbn: str = Query(..., description="ISBN книги")):
    book = collection.find_one({"isbn": isbn})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found " + isbn)
    return book

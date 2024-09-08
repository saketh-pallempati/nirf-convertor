from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import pdf_processor

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/convert/")
async def convert_pdf_to_csv(file: UploadFile = File(...)):
    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(await file.read())

    csv_path = pdf_processor.main(pdf_path)

    os.remove(pdf_path)

    return FileResponse(csv_path, media_type='text/csv', filename=csv_path)
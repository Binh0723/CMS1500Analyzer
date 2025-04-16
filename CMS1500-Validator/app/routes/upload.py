from fastapi import APIRouter, File, UploadFile # type: ignore
from app.services.pdf_parser import validate_pdf
from app.services.ocr_service import validate_image
from app.services.getAnswer import getAnswer
from app.services.getAnswer import RequestModel
upload_router = APIRouter(prefix ="/api")

@upload_router.get("/test")
async def getTest():
    return {"Message" : "test router"}


@upload_router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    
    #getting the file extension
    file_extension = file.filename.split(".")[-1].lower()
 
    #get the content of the file
    contents = await file.read()

    #save the file to uploaded_files folder
    name = f"uploaded_files/{file.filename}"
    with open(name,"wb") as f:
        f.write(contents)
    result = None
    if file_extension == 'pdf':
        result = validate_pdf(name) 
    else:
        result = validate_image(name)

    #return the metadata of the uploaded files
    return {"result":result
            }

@upload_router.post("/question/")
async def upload_image(message:RequestModel):
    
    print("getting message " + str(message))
    response = await getAnswer(message)

    #return the metadata of the uploaded files
    return {"result":response
            }
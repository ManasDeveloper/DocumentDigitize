from fastapi import FastAPI, File,UploadFile,HTTPException
from fastapi.responses import JSONResponse 
from PIL import Image 
import pytesseract
import uvicorn
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
load_dotenv()
import os

app = FastAPI() 
es = Elasticsearch(
    "https://my-elasticsearch-project-d846f7.es.us-east-1.aws.elastic.cloud:443",
    api_key=os.getenv("ELASTIC_API_KEY")
)

INDEX_NAME = "documents"

mapping = {
    "mappings": {
        "properties": {
            "filename": {"type": "text"},
            "text": {"type": "text"}
        }
    }
}

# function to check if the index exists
def create_index():
    if not es.indices.exists(index = INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)

create_index()

@app.post("/upload")
async def upload_file(file : UploadFile = File(...)):
    try:
        # open the uploaded file 
        image = Image.open(file.file)
        # extract text using ocr
        text = pytesseract.image_to_string(image)

        # save to elasticsearch
        document = {
            "filename" : file.filename,
            "text" : text
        }
        es.index(index=INDEX_NAME, document=document)
        print(text)
        return {"message":"File uploaded successfully","text":text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search")
async def search_documents(q : str):
    try:
        query = {
    "query": {
        "multi_match": {
            "query": q,
            "fields": ["filename", "text"]
        }
    }
}
    
            
        
        response = es.search(index=INDEX_NAME, body=query)
        results = [
            {
                "filename": hit["_source"]["filename"],
                "text": hit["_source"]["text"],
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
        
        if not results:
            return {"message" : "No results found"}
        
        return {"results" : results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
        
@app.get("/list-documents")
async def list_documents():
    try:
        # Query to fetch all documents
        query = {"query": {"match_all": {}}}
        
        response = es.search(index=INDEX_NAME, body=query, size=1000)  # Fetch up to 1000 documents
        results = [
            {
                "filename": hit["_source"]["filename"],
                "text": hit["_source"]["text"][:200]  # Show a snippet of the text
            }
            for hit in response["hits"]["hits"]
        ]
        
        if not results:
            return {"message": "No documents found"}
        
        return {"documents": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

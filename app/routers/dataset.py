from fastapi import APIRouter, UploadFile
from app.services.dataset_service import process_tsv_dataset, process_faa_dataset

router = APIRouter()

@router.post("/load_tsv_data")
async def process_tsv(file: UploadFile):
    return await process_tsv_dataset(file)

@router.post("/load_faa_data")
async def process_faa(file: UploadFile):
    return await process_faa_dataset(file)

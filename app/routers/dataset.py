from fastapi import APIRouter, UploadFile, File
from app.services.dataset_service import process_tsv_dataset, process_faa_dataset

import logging, time
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/load_tsv_data")
async def process_tsv(file: UploadFile = File(...)):
    t0 = time.time()
    logger.info("load_tsv_data: ENTER")
    logger.info("load_tsv_data: filename=%s content_type=%s", file.filename, file.content_type)
    out = await process_tsv_dataset(file)
    logger.info("load_tsv_data: DONE in %.2fs", time.time() - t0)
    return out

@router.post("/load_faa_data")
async def process_faa(file: UploadFile = File(...)):
    return await process_faa_dataset(file)

from fastapi import APIRouter, Request
from app.services.lookup_service import resolve_id_by_name

router = APIRouter()

@router.post("/fetchID")
async def id_by_name(request: Request):
    data = await request.json()
    taxon_name = data["taxName"]
    return resolve_id_by_name(taxon_name)

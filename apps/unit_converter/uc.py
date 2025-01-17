from fastapi import APIRouter
from .uc_db import len_db

router = APIRouter(prefix='/uc')

@router.get('/length/')
def length(value: float, from_unit: str, to_unit: str):

    ans = value * len_db['conv'][from_unit][to_unit]

    return {
        "from_unit": len_db['units'][from_unit],
        "from_unit_notation": from_unit,
        "to_unit": len_db['units'][to_unit],
        "to_unit_notation": to_unit,
        "given_value": value,
        "converted_value": ans
    }
    

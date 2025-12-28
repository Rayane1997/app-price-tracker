from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..core import crud
from ..schemas.parser_config import (
    ParserConfigCreate,
    ParserConfigUpdate,
    ParserConfigResponse,
    ParserConfigList,
)
import math

router = APIRouter(prefix="/parser-configs", tags=["parser-configs"])


@router.get("/", response_model=ParserConfigList)
def list_parser_configs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """List all parser configurations with pagination and filtering"""
    skip = (page - 1) * page_size

    configs, total = crud.get_parser_configs(
        db=db,
        skip=skip,
        limit=page_size,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ParserConfigList(
        configs=configs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{config_id}", response_model=ParserConfigResponse)
def get_parser_config(
    config_id: int,
    db: Session = Depends(get_db),
):
    """Get single parser configuration by ID"""
    config = crud.get_parser_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Parser configuration not found")
    return config


@router.get("/domain/{domain}", response_model=ParserConfigResponse)
def get_parser_config_by_domain(
    domain: str,
    db: Session = Depends(get_db),
):
    """Get parser configuration by domain"""
    config = crud.get_parser_config_by_domain(db, domain)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Parser configuration not found for domain: {domain}",
        )
    return config


@router.post("/", response_model=ParserConfigResponse, status_code=201)
def create_parser_config(
    config: ParserConfigCreate,
    db: Session = Depends(get_db),
):
    """Create new parser configuration"""
    try:
        # Check if domain already exists
        existing = crud.get_parser_config_by_domain(db, config.domain)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Parser configuration already exists for domain: {config.domain}",
            )
        return crud.create_parser_config(db, config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{config_id}", response_model=ParserConfigResponse)
def update_parser_config(
    config_id: int,
    config_update: ParserConfigUpdate,
    db: Session = Depends(get_db),
):
    """Update existing parser configuration"""
    config = crud.update_parser_config(db, config_id, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="Parser configuration not found")
    return config


@router.delete("/{config_id}", status_code=204)
def delete_parser_config(
    config_id: int,
    db: Session = Depends(get_db),
):
    """Delete parser configuration"""
    success = crud.delete_parser_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parser configuration not found")
    return None


@router.post("/{config_id}/test", response_model=dict)
def test_parser_config(
    config_id: int,
    url: str = Query(..., description="URL to test the parser config against"),
    db: Session = Depends(get_db),
):
    """Test parser configuration with a URL"""
    config = crud.get_parser_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Parser configuration not found")

    # Simple test: check if config has required selectors
    if not config.price_selectors:
        raise HTTPException(
            status_code=400, detail="Parser configuration missing price_selectors"
        )

    return {
        "config_id": config_id,
        "domain": config.domain,
        "test_url": url,
        "selectors_available": {
            "price": bool(config.price_selectors),
            "name": bool(config.name_selectors),
            "image": bool(config.image_selectors),
        },
        "use_playwright": config.use_playwright,
        "status": "ready",
        "message": "Parser configuration is valid and ready for testing",
    }

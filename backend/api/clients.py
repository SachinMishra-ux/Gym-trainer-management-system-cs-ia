from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.schemas.client import ClientCreate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.get("", response_model=List[ClientResponse], summary="List all clients")
def list_clients(active_only: bool = False, db: Session = Depends(get_db)):
    """
    Retrieve all clients from the database.
    Optionally filter to active clients only using ?active_only=true.
    """
    query = db.query(Client)
    if active_only:
        query = query.filter(Client.active == True)
    clients = query.order_by(Client.id.asc()).all()
    return clients

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, summary="Create a new client")
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client record in the database.
    Validates that client name is provided.
    """
    cleaned_name = client_data.name.strip()
    if not cleaned_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client name cannot be empty."
        )

    db_client = Client(
        name=cleaned_name,
        phone=client_data.phone.strip() if client_data.phone else None,
        email=client_data.email.strip() if client_data.email else None,
        active=client_data.active
    )
    
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database commit error: {str(e)}"
        )

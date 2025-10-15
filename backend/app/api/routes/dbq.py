"""DBQ document upload endpoints for vision-based grading"""

import base64
import logging
import time
import uuid
from typing import Dict, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from app.models.requests.grading import DocumentMetadata, DocumentUploadResponse
from app.api.routes.auth import require_auth
from app.middleware.rate_limiting import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/dbq", tags=["dbq"])

# In-memory document storage - similar to auth sessions
document_sets: Dict[str, Dict] = {}
DOCUMENT_SET_DURATION = 2 * 60 * 60  # 2 hours in seconds
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file
REQUIRED_DOCUMENT_COUNT = 7


def cleanup_expired_documents():
    """Remove expired document sets"""
    current_time = time.time()
    expired_ids = [
        doc_id for doc_id, doc_set in document_sets.items()
        if current_time - doc_set["created_at"] > DOCUMENT_SET_DURATION
    ]
    for doc_id in expired_ids:
        logger.info(f"Cleaning up expired document set: {doc_id}")
        del document_sets[doc_id]


def get_document_set(document_set_id: str) -> Dict:
    """
    Retrieve a document set by ID.

    Args:
        document_set_id: UUID of the document set

    Returns:
        Document set dictionary

    Raises:
        HTTPException: If document set not found or expired
    """
    cleanup_expired_documents()

    if document_set_id not in document_sets:
        raise HTTPException(
            status_code=404,
            detail="Document set not found or expired. Please upload documents again."
        )

    return document_sets[document_set_id]


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    responses={
        400: {"description": "Invalid file format or count"},
        413: {"description": "File too large"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    },
    summary="Upload DBQ documents",
    description="""
    Upload 7 DBQ document images for vision-based grading.

    **Requirements:**
    - Exactly 7 PNG files
    - Each file must be < 5MB
    - Files will be labeled as Document 1-7 in order of upload
    - Documents expire after 2 hours

    **Usage:**
    1. Upload documents once per assignment
    2. Receive document_set_id
    3. Use document_set_id when grading multiple student essays
    4. Documents cached for batch grading (cost optimization)

    **Rate Limits:**
    - 10 uploads per hour
    """
)
@limiter.limit("10/hour")
async def upload_documents(
    request: Request,
    documents: List[UploadFile] = File(..., description="7 PNG document images"),
    _: bool = Depends(require_auth)
) -> DocumentUploadResponse:
    """
    Upload 7 DBQ document images.

    Args:
        request: FastAPI request object for rate limiting
        documents: List of 7 PNG files

    Returns:
        Document set metadata including document_set_id

    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        # Validate document count
        if len(documents) != REQUIRED_DOCUMENT_COUNT:
            raise HTTPException(
                status_code=400,
                detail=f"Exactly {REQUIRED_DOCUMENT_COUNT} documents required. Received {len(documents)}."
            )

        # Process and validate each document
        processed_documents: List[DocumentMetadata] = []
        total_size_bytes = 0

        for idx, file in enumerate(documents, start=1):
            # Validate PNG format
            if file.content_type not in ["image/png"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Document {idx} must be PNG format. Received: {file.content_type}"
                )

            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            total_size_bytes += file_size

            # Validate file size
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Document {idx} exceeds 5MB limit. Size: {file_size / 1024 / 1024:.2f}MB"
                )

            # Validate file is not empty
            if file_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Document {idx} is empty"
                )

            # Convert to base64
            base64_encoded = base64.b64encode(file_content).decode('utf-8')

            # Create document metadata
            doc_metadata = DocumentMetadata(
                doc_num=idx,
                base64=base64_encoded,
                size_bytes=file_size
            )
            processed_documents.append(doc_metadata)

            logger.info(f"Processed document {idx}: {file_size / 1024:.2f}KB")

        # Generate unique document set ID
        document_set_id = str(uuid.uuid4())
        current_time = time.time()
        expires_at = datetime.fromtimestamp(current_time + DOCUMENT_SET_DURATION)

        # Store documents in memory
        document_sets[document_set_id] = {
            "documents": [doc.dict() for doc in processed_documents],
            "created_at": current_time,
            "expires_at": expires_at,
            "total_size_bytes": total_size_bytes
        }

        # Clean up old documents
        cleanup_expired_documents()

        logger.info(
            f"Document set {document_set_id} created: "
            f"{len(processed_documents)} documents, "
            f"{total_size_bytes / 1024 / 1024:.2f}MB total"
        )

        return DocumentUploadResponse(
            document_set_id=document_set_id,
            document_count=len(processed_documents),
            total_size_mb=round(total_size_bytes / 1024 / 1024, 2),
            expires_at=expires_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload documents. Please try again."
        )


@router.get(
    "/documents/{document_set_id}",
    summary="Get document set info",
    description="Get metadata about an uploaded document set without retrieving the actual images."
)
async def get_document_info(
    document_set_id: str,
    _: bool = Depends(require_auth)
) -> Dict:
    """
    Get information about a document set.

    Args:
        document_set_id: UUID of the document set

    Returns:
        Document set metadata
    """
    doc_set = get_document_set(document_set_id)

    return {
        "document_set_id": document_set_id,
        "document_count": len(doc_set["documents"]),
        "total_size_mb": round(doc_set["total_size_bytes"] / 1024 / 1024, 2),
        "expires_at": doc_set["expires_at"].isoformat(),
        "created_at": datetime.fromtimestamp(doc_set["created_at"]).isoformat()
    }


@router.delete(
    "/documents/{document_set_id}",
    summary="Delete document set",
    description="Manually delete a document set before it expires."
)
async def delete_document_set(
    document_set_id: str,
    _: bool = Depends(require_auth)
) -> Dict:
    """
    Delete a document set.

    Args:
        document_set_id: UUID of the document set

    Returns:
        Success message
    """
    if document_set_id not in document_sets:
        raise HTTPException(
            status_code=404,
            detail="Document set not found"
        )

    del document_sets[document_set_id]
    logger.info(f"Document set {document_set_id} manually deleted")

    return {"message": "Document set deleted successfully"}

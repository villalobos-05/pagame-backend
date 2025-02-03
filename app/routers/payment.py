from datetime import datetime, timezone
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.dependencies import getAuthenticatedUserId, getObjectId
from app.models.payment import CreatePayment, PaymentStatus
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.payment import paymentSchemas

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
async def createPayment(
    payment: CreatePayment,
    receiverId: ObjectId = Depends(getAuthenticatedUserId),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    payerId = getObjectId(payment.payerId)

    # todo: check that payerId and receiverId are not the same

    await db["payments"].insert_one(
        {
            "issue": payment.issue,
            "money": payment.money,
            "receiverId": receiverId,
            "payerId": payerId,
            "status": PaymentStatus.UNPAYED,
            "createdAt": datetime.now(timezone.utc),
        }
    )

    return {"message": "Payment created successfully"}


@router.patch("/{id}/pay")
async def payPayment(
    id: Annotated[ObjectId, Depends(getObjectId)],
    payerId: Annotated[ObjectId, Depends(getAuthenticatedUserId)],
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = await db["users"].find_one({"_id": payerId})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User not found with id {id}",
        )

    # todo: check if status is only unpayed

    await db["payments"].update_one(
        {"_id": id, "payerId": payerId},
        {"$set": {"status": PaymentStatus.UNCHECKED}},
    )

    return {"message": f"Payment payed. Status changed to {PaymentStatus.UNCHECKED}"}


@router.patch("/{id}/check")
async def checkPayment(
    id: Annotated[ObjectId, Depends(getObjectId)],
    receiverId: Annotated[ObjectId, Depends(getAuthenticatedUserId)],
    reject: bool | None = False,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = await db["users"].find_one({"_id": receiverId})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User not found with id {id}",
        )

    # todo: check if status is only unchecked

    await db["payments"].update_one(
        {"_id": id, "receiverId": receiverId},
        {
            "$set": {
                "status": (PaymentStatus.REJECTED if reject else PaymentStatus.PAYED),
                "checkedAt": datetime.now(timezone.utc),
            }
        },
    )

    return {
        "message": (
            "Payment rejected successfully"
            if reject
            else "Payment checked successfully"
        )
    }


@router.get("/")
async def getUserPayments(
    userId: Annotated[ObjectId, Depends(getAuthenticatedUserId)],
    payerId: str | None = None,
    receiverId: str | None = None,
    paymentStatus: PaymentStatus | None = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # All payments (both payed or received)
    if not payerId and not receiverId:
        query = {
            "$or": [
                {"payerId": userId},
                {"receiverId": userId},
            ]
        }
    # Payments received from payer
    elif payerId:
        query = {"payerId": getObjectId(payerId), "receiverId": userId}
    # Payments payed to receiver
    elif receiverId:
        query = {"payerId": userId, "receiverId": getObjectId(receiverId)}

    if paymentStatus:
        query["status"] = paymentStatus

    payments = await db["payments"].find(query).to_list()

    return paymentSchemas(payments)

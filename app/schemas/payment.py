from app.models.payment import Payment


def paymentSchema(payment) -> Payment:
    return Payment(
        id=str(payment["_id"]),
        issue=payment["issue"],
        money=payment["money"],
        payerId=str(payment["payerId"]),
        receiverId=str(payment["receiverId"]),
        status=payment["status"],
        createdAt=payment["createdAt"],
        checkedAt=payment.get("checkedAt") or None,
    )


def paymentSchemas(payments) -> list[Payment]:
    return [paymentSchema(payment) for payment in payments]

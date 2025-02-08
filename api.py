from datetime import datetime
import string
import json
import re
import math
from hashlib import md5
from uuid import uuid4
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from __types.receipts import ReceiptsPayload, ReceiptItem
from __types.db import DBObject, DB

api = FastAPI()

# Add middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DB()

alpha_num_re = re.compile(f'[^{string.ascii_letters+string.digits}]')  # regex for removing non-alphanumeric characters


def calculate_datetime_points(timestamp: str) -> int:
    try:
        dt_points = 0

        receipt_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
        # Give points for odd days
        if receipt_timestamp.day % 2 != 0:
            dt_points += 6

        if receipt_timestamp.hour >= 14 and receipt_timestamp.hour < 16:
            # Assuming that 14:00 is excluded because the instruction say after 2pm
            if receipt_timestamp.minute > 0:
                dt_points += 10
        return dt_points
    except Exception as ex:
        print(f'calculate_datetime_points exception {ex}')
        raise ex


def calculate_item_points(items: list[ReceiptItem]) -> int:
    try:
        item_total = 0
        for item in items:
            if len(item.shortDescription.strip()) % 3 == 0:
                item_points = math.ceil(float(item.price) * 0.2)

                item_total += item_points

        return item_total
    except Exception as ex:
        print(f'calculate_item_points exception {ex}')
        raise ex


def calculate_total_price_points(total: str) -> int:
    try:
        t_points = 0
        # Might be a more math-y way to do this, but checking the cents value seems fine
        if '.00' in total:
            t_points += 50

        # Check if the total is a multiple of 25 cents
        float_total = float(total)
        if float_total % 0.25 == 0.0:
            t_points += 25

        return t_points
    except Exception as ex:
        print(f'calculate_total_price_points exception {ex}')
        raise ex


def calculate_points(receipt: ReceiptsPayload) -> int:
    '''Calculates points according to assignment guidelines'''
    try:
        clean_retailer = re.sub(alpha_num_re, '', receipt.retailer)

        retailer_points = len(clean_retailer)
        total_price_points = calculate_total_price_points(receipt.total)
        item_count_points = 5 * math.floor(len(receipt.items) / 2)  # round down to the nearest 2 multiple
        item_price_points = calculate_item_points(receipt.items)
        datetime_points = calculate_datetime_points(f'{receipt.purchaseDate} {receipt.purchaseTime}')

        points_total = retailer_points + total_price_points + item_count_points + item_price_points + datetime_points

        return points_total
    except Exception as ex:
        raise ex


def store_receipt(receipt: ReceiptsPayload) -> str:
    try:
        receipt_hash = md5(json.dumps(receipt, default=lambda o: o.__dict__).encode())
        receipt_key = receipt_hash.hexdigest()

        if db.receipts.get(receipt_key, None):
            return db.receipts.get(receipt_key).id
        else:
            db_receipt = DBObject()
            db_receipt.id = str(uuid4())
            db_receipt.points = calculate_points(receipt)

            db.receipts[receipt_key] = db_receipt

            return db_receipt.id
    except Exception as ex:
        raise ex


@api.post("/receipts/process", include_in_schema=True)
async def process_receipt(response: Response, payload: ReceiptsPayload):
    try:
        receipt_id = store_receipt(payload)

        return {'id': receipt_id}
    except Exception:
        response.status_code = 422
        return {'error': 'There was an error processing your receipt'}


@api.get("/receipts/{id}/points")
async def receipt_points(id: str):
    try:
        receipt = [r for r in db.receipts.values() if r.id == id][0]

        return {'points': receipt.points}
    except Exception:
        return {'error': f'No receipt found for id {id}'}

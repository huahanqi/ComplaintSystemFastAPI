import os
import uuid

from services.s3 import S3Service
from services.ses import SESService

from constants import TEMP_FILE_FOLDER
from db import database
from models import complaint, RoleType, State
from utils.helpers import decode_photo

s3 = S3Service()
ses = SESService()

class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaint.select()
        if user["role"] == RoleType.complainer:
            q = q.where(complaint.c.complainer_id == user["id"])
        elif user["role"] == RoleType.approver:
            q = q.where(complaint.c.state == State.pending)
        return await database.fetch_all(q)

    @staticmethod
    async def create_complaint(complaint_data, user):
        data = complaint_data.dict()
        data["complainer_id"] = user["id"]
        encoded_photo = data.pop("encoded_photo")
        ext = data.pop("extension")
        name = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(TEMP_FILE_FOLDER, name)
        decode_photo(path, encoded_photo)
        data["photo_url"] = s3.upload_photo(path, name, ext)
        os.remove(path)
        id_ = await database.execute(complaint.insert().values(**data))
        return await database.fetch_one(complaint.select().where(complaint.c.id == id_))

    @staticmethod
    async def delete(complaint_id):
        await database.execute(complaint.delete().where(complaint.c.id == complaint_id))

    @staticmethod
    async def approve(id_):
        await database.execute(complaint.update().where(complaint.c.id == id_).values(status=State.approved))
        ses.send_mail("Your complaint is approved", ["huahanqi@gmail.com"],
                      "Congrats! You complaint is approved. Please check your bank account after 2 business days. ")

    @staticmethod
    async def reject(id_):
        await database.execute(complaint.update().where(complaint.c.id == id_).values(status=State.rejected))

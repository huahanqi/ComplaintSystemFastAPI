from decouple import config
import boto3


class SESService:
    def __init__(self):
        secret_id = config("AWS_ACCESS_KEY")
        secret_key = config("AWS_SECRET")
        self.ses = boto3.client(
            "ses",
            region_name=config("SES_REGION"),
            aws_access_key_id=secret_id,
            aws_secret_access_key=secret_key,
        )

    def send_mail(self, subject, to_addresses, text_data):
        body = {}
        body.update({"Text": {"Data": text_data, "Charset": "UTF-8"}})

        try: self.ses.send_email(
            Source="huahanqi@live.unc.edu",
            Destination={"ToAddresses": to_addresses, "CcAddresses": [], "BccAddresses": []},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": body,
                },
        )
        except Exception as ex:
            raise ex

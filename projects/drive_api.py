import json
import requests


class DriveUploader():
    def __init__(self, file_name, file_data, access_token="ya29.a0AX07Cmt2fEvLDD-t1wMLGJoJ1OKZfMrekaUSF980UF8eVNSmBgsTJJ43Ex5Um8eWg1ltepeIC-4oeS0BHFPyXoZpvqIAMH-iXWUFnFMeYTX07eELfm8UAQTXkSCkUxQ9XV38rGd2G_NUKzF6QKxuagwZCyjzn-v4RV2iDWGGHfNRA7sDdNFikUNIxvtbX0BNQMJ6pdoaCgYKAeYSARQSFQHGX2MiX4Xk9uGK2wbY0Rlt8k9WhQ0206",  file_mime_type="application/pdf", parent_folder_id="1YBO4ktfLh1229IsEUkG2YAvfbGIn6QoW"):
        self.ACCESS_TOKEN = access_token
        self.FILE_MIME_TYPE = file_mime_type
        self.PARENT_FOLDER_ID = parent_folder_id
        self.UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        self.FILE_NAME = file_name
        self.FILE_DATA = file_data

    def upload_file(self):
        # 2. Endpoint URL
        

        # 3. File metadata
        metadata = {
            "name": self.FILE_NAME,  # Target name in Drive
        }
        if self.PARENT_FOLDER_ID:
            metadata["parents"] = [self.PARENT_FOLDER_ID]

        # 4. Prepare headers and multipart payload
        headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}"
        }

        files = {
                "data": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
                "file": (metadata["name"], self.FILE_DATA, self.FILE_MIME_TYPE),
            }

            # 5. Send POST request
        response = requests.post(self.UPLOAD_URL, headers=headers, files=files)

        # 6. Response handling
        if response.status_code == 200:
            file_info = response.json()
            print("Upload successful!")
            print(f"File ID: {file_info.get('id')}")
            print(f"File Name: {file_info.get('name')}")
            return file_info
        else:
            print(f"Failed to upload. HTTP {response.status_code}: {response.text}")
        return None

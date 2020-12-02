from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from apiclient import errors
import time


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():

    service = get_service()

    original_photo_folder_id = "1tauR2RzAF1GWBVvvNKLQho2TRnEYcJUy"
    new_photo_folder_id = "1mg8hrVY9LsdoE1ks8Ybn02P0ODu4MWgL"

    all_folders = retrieve_all_files(service, original_photo_folder_id)

    moved_photos = retrieve_all_files(service, new_photo_folder_id)
    moved_photos_name = list()

    for photo in moved_photos:
        moved_photos_name.append(photo["name"])

    print(moved_photos_name)

    for folder in all_folders:

        current_folder_id = folder["id"]

        photos_in_folder = retrieve_all_files(service, current_folder_id)

        for photo in photos_in_folder:

            if photo["name"] in moved_photos_name:
                print("moved")
                continue

            print(photo)
            try:
                copy_file(service, photo["id"], photo["name"], new_photo_folder_id)
            except:
                print("sleeping")
                time.sleep(60)
                copy_file(service, photo["id"], photo["name"], new_photo_folder_id)


def retrieve_all_files(service, folder_id):
    """Retrieve a list of File resources.

    Args:
    service: Drive API service instance.
    folder_id: Folder from which to retrieve files
    Returns:
    List of File resources.
    """
    result = []
    page_token = None
    while True:
        try:
            query = "'{}' in parents".format(folder_id)
            param = {"q": query}
            if page_token:
                param["pageToken"] = page_token

            files = service.files().list(**param).execute()

            result.extend(files["files"])
            page_token = files.get("nextPageToken")
            if not page_token:
                break
        except errors.HttpError:
            print("An error occurred")
            break
    return result


def copy_file(service, origin_file_id, original_file_name, new_parent_id):
    """Copy an existing file.

    Args:
        service: Drive API service instance.
        origin_file_id: ID of the origin file to copy.
        copy_title: Title of the copy.

    Returns:
        The copied file if successful, None otherwise.
    """
    copied_file = {"title": original_file_name, "parents": [new_parent_id]}
    try:
        service.files().copy(fileId=origin_file_id, body=copied_file).execute()
    except errors.HttpError:
        print("An error occurred")


def get_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


if __name__ == "__main__":
    main()

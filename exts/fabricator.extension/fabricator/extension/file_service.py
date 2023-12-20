import os, requests, shutil, uuid
from io import BytesIO
from PIL import Image
from pathlib import Path

class FileService:
    image_ext = "png"
    model_ext = "usdz"

    def __init__(self) -> None:
        self.dir_path = (Path.home() / 'temp').as_posix()

    def create_dir(self):
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def remove_dir(self):
        if os.path.exists(self.dir_path):
            shutil.rmtree(self.dir_path)

    def save_file(self, file_name: str, url: str) -> str:
        file_path = os.path.join(self.dir_path, f'{file_name}')
        if os.path.exists(file_path):
            return file_path

        binary_data = requests.get(url).content
        with open(file_path, 'wb') as file_object:
            file_object.write(binary_data)
        
        return file_path
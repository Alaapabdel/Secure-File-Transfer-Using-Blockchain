import os
import time
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # Ensure unique names by appending a timestamp
        base, extension = os.path.splitext(name)
        new_name = f"{base}_{int(time.time())}{extension}"
        return super().get_available_name(new_name, max_length)

    def get_valid_name(self, name):
        return name  # Keep the original name for display purposes

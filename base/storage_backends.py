
from django.core.files.storage import Storage
from supabase import create_client
from django.conf import settings
import io

class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET

    def _save(self, name, content):
        # Convert Django file to bytes
        file_bytes = content.read()

        # Upload to Supabase
        response = self.client.storage.from_(self.bucket).upload(name, io.BytesIO(file_bytes))
        
        if response.get("error"):
            raise Exception(f"Supabase upload failed: {response['error']}")
        return name

    def url(self, name):
        # Return public URL
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{name}"

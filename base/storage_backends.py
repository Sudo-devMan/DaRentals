
from django.core.files.storage import Storage
from supabase import create_client
from django.conf import settings
import io
import tempfile

class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET


    def _save(self, name, content):
        # Convert Django file to bytes
        content.seek(0)

        # Upload to Supabase
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(content.read())
            tmp.flush()
            self.client.storage.from_(self.bucket).upload(name, tmp.name)
        response = self.client.storage.from_(self.bucket).upload(name, io.BytesIO(file_bytes))
        
        return name

    def exists(self, name):
        res = self.client.storage.from_(self.bucket).list(path=name)
        return len(res) > 0

    def url(self, name):
        # Return public URL
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{name}"

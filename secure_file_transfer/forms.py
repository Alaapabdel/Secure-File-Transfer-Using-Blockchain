from django import forms
from .models import FileUpload, User

class FileUploadForm(forms.Form):
    file = forms.FileField()

class FileTransferForm(forms.ModelForm):
    recipient_email = forms.EmailField()

    class Meta:
        model = FileUpload
        fields = ['recipient_email']

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

    def clean_recipient_email(self):
        email = self.cleaned_data['recipient_email']
        if email == self.sender.email:
            raise forms.ValidationError("You can't send files to yourself.")
        
        try:
            recipient = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("User with this email does not exist.")
        
        return recipient

    def save(self, commit=True):
        if 'uploaded_files' not in self.data:
            raise forms.ValidationError("No file uploaded.")
        
        recipient = self.cleaned_data['recipient_email']
        original_file_upload_id = self.data['uploaded_files']
        original_file_upload = FileUpload.objects.get(id=original_file_upload_id)
        
        file_upload = FileUpload(
            sender=self.sender,
            recipient=recipient,
            ipfs_hash=original_file_upload.ipfs_hash,
            encryption_key=original_file_upload.encryption_key
        )
        if commit:
            file_upload.save()
            file_upload.create_blockchain_entry('transfer')

        return file_upload

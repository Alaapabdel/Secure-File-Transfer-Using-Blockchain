from __future__ import print_function
from virus_total_apis import PublicApi as VirusTotalPublicApi
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib import messages
from .models import User, FileUpload, Wallet, Blockchain
from .forms import FileUploadForm, FileTransferForm
from .decorators import custom_login_required
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib
from django.utils import timezone
from .ipfs_service import add_file_to_ipfs, get_file_from_ipfs

API_KEY = 'YOUR-VIRUSTOTAL-API-KEY'

def get_wallet_balance(user):
    wallet, created = Wallet.objects.get_or_create(owner=user)
    return wallet.balance

def is_malicious(file):
    file_md5 = hashlib.md5(file.read()).hexdigest()
    vt = VirusTotalPublicApi(API_KEY)
    response = vt.get_file_report(file_md5)
    if response['results']['response_code'] == 1:
        if 'positives' in response['results'] and response['results']['positives'] > 0:
            return True
    return False

def index(request):
    wallet = None
    if request.session.get('user_id'):
        try:
            user = User.objects.get(id=request.session['user_id'])
            wallet = Wallet.objects.get(owner=user)
        except (User.DoesNotExist, Wallet.DoesNotExist):
            wallet = None
    
    context = {
        'wallet_balance': wallet.balance if wallet else 0
    }
    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            return redirect('/')
        except User.DoesNotExist:
            messages.error(request, 'The email address or password you entered is incorrect.')
            return render(request, 'login.html')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email address is already registered. Please use a different email or login.')
            return render(request, 'register.html')
        user = User(email=email, password=password)
        user.save()
        Wallet.objects.create(owner=user, balance=Decimal('10.00'))  # Initial balance for new users
        messages.success(request, 'Registration successful. You can now log in.')
        return redirect('/login')
    return render(request, 'register.html')

def logout(request):
    request.session.flush()
    messages.success(request, 'You have successfully logged out.')
    return redirect('/login')

@custom_login_required
def files(request):
    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        return redirect('/login')

    wallet, created = Wallet.objects.get_or_create(owner=user)  # Ensure the user has a wallet

    if request.method == 'POST':
        # Check the upload limit (5 times a day)
        upload_limit = 5
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        uploads_today = FileUpload.objects.filter(sender=user, uploaded_at__gte=start_of_day, recipient__isnull=True).count()
        if uploads_today >= upload_limit:
            messages.error(request, 'You have reached the daily upload limit of 5 files.')
            return redirect('files')
        else:
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file']
                uploaded_file.seek(0)
                if is_malicious(uploaded_file):
                    messages.error(request, 'The file you are trying to upload is malicious.')
                    return redirect('files')
                
                # Encrypt the file
                uploaded_file.seek(0)
                encryption_key = Fernet.generate_key().decode()
                encrypted_data = Fernet(encryption_key.encode('utf-8')).encrypt(uploaded_file.read())

                # Upload to IPFS
                ipfs_response = add_file_to_ipfs(encrypted_data)
                if ipfs_response and 'Hash' in ipfs_response:
                    ipfs_hash = ipfs_response['Hash']
                    file_upload = FileUpload(
                        sender=user,
                        ipfs_hash=ipfs_hash,
                        original_filename=uploaded_file.name,  # Save original filename
                        encryption_key=encryption_key
                    )

                    file_upload.save()
                    file_upload.create_blockchain_entry('upload')  # Record upload action
                    messages.success(request, 'File successfully uploaded, recorded in the blockchain, and reward granted.')
                    return redirect('files')
                else:
                    messages.error(request, 'Failed to upload file to IPFS.')
                    return redirect('files')
    else:
        form = FileUploadForm()

    files = FileUpload.objects.filter(sender=user, recipient__isnull=True)
    return render(request, 'files.html', {'form': form, 'files': files, 'wallet_balance': wallet.balance})

@custom_login_required
def serve_file(request, file_id):
    try:
        user_id = request.session['user_id']
        file_upload = get_object_or_404(FileUpload, id=file_id)

        if file_upload.recipient is None or file_upload.recipient.id != user_id:
            if file_upload.sender.id != user_id:
                messages.error(request,"You do not have permission to access this file.")
                return redirect('files')

        ipfs_hash = file_upload.ipfs_hash
        encrypted_data = get_file_from_ipfs(ipfs_hash)
        if encrypted_data:
            decrypted_data = Fernet(file_upload.encryption_key.encode('utf-8')).decrypt(encrypted_data)
            response = HttpResponse(decrypted_data, content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{file_upload.original_filename}"'
            return response
        else:
            raise Http404("Failed to retrieve file from IPFS.")
    except Exception as e:
        raise Http404(e)


@custom_login_required
def dashboard(request):
    user = User.objects.get(id=request.session['user_id'])
    wallet, created = Wallet.objects.get_or_create(owner=user)  # Ensure the user has a wallet
    blocks = Blockchain.objects.all().order_by('-block_number')
    return render(request, 'dashboard.html', {'blocks': blocks, 'wallet_balance': wallet.balance})

@custom_login_required
def file_transfer(request):
    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        return redirect('/login')

    wallet, created = Wallet.objects.get_or_create(owner=user)  # Ensure the user has a wallet

    if request.method == 'POST':
        form = FileTransferForm(request.POST, request.FILES, sender=user)
        if form.is_valid():
            if wallet.balance < Decimal('1.0'):  # Check if the user has enough balance
                messages.error(request, 'Insufficient balance to complete the transfer.')
            else:
                file_upload = form.save(commit=False)
                file_upload.ipfs_hash = FileUpload.objects.get(id=request.POST['uploaded_files']).ipfs_hash
                file_upload.original_filename = FileUpload.objects.get(id=request.POST['uploaded_files']).original_filename
                file_upload.save()  # Save the file upload record
                file_upload.create_blockchain_entry('transfer')  # Record transfer action
                messages.success(request, 'File successfully sent.')
                return redirect('file_transfer')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = FileTransferForm(sender=user)

    uploaded_files = FileUpload.objects.filter(sender=user, recipient__isnull=True)
    sent_files = FileUpload.objects.filter(sender=user).exclude(recipient__isnull=True)
    received_files = FileUpload.objects.filter(recipient=user)

    return render(request, 'filetransfer.html', {
        'form': form,
        'uploaded_files': uploaded_files,
        'sent_files': sent_files,
        'received_files': received_files,
        'wallet_balance': wallet.balance
    })

import hashlib
import json
from decimal import Decimal
from typing import Any
from django.db import models
from cryptography.fernet import Fernet
import os
from django.utils.crypto import get_random_string
from django.utils import timezone


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email

class Wallet(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.owner.email}'s Wallet"

class FileUpload(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_files')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_files', null=True, blank=True)
    ipfs_hash = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    encryption_key = models.CharField(max_length=255)

    def encrypt_file(self, file_data):
        cipher_suite = Fernet(self.encryption_key.encode('utf-8'))
        return cipher_suite.encrypt(file_data)

    def decrypt_file(self, encrypted_data):
        cipher_suite = Fernet(self.encryption_key.encode('utf-8'))
        return cipher_suite.decrypt(encrypted_data)

    def create_blockchain_entry(self, action):
        file_hash = hashlib.sha256(self.ipfs_hash.encode()).hexdigest()
        previous_block = Blockchain.objects.order_by('-block_number').first()
        previous_hash = previous_block.hash if previous_block else '0' * 64
        block_number = previous_block.block_number + 1 if previous_block else 1
        cairo_time = timezone.localtime(self.uploaded_at, timezone.get_current_timezone())

        data = {
            'ipfs_hash': self.ipfs_hash,
            'action': action,
            'sender': self.sender.email,
            'recipient': self.recipient.email if self.recipient else None,
            'timestamp': cairo_time.strftime('%Y-%m-%d %H:%M:%S')
        }
  
        new_block = Blockchain(
            block_number=block_number,
            previous_hash=previous_hash,
            hash=file_hash,
            data=json.dumps(data)
        )
        new_block.mine_block(4)
        wallet = Wallet.objects.filter(owner=self.sender)[0]
        wallet.balance += Decimal('0.01')  # Reward for Mining
        if action == 'transfer':
            wallet.balance -= Decimal('1.00')  # Deduct Cost
        wallet.save()
        new_block.save()

    def __str__(self):
        return f"{self.sender.email} - {self.ipfs_hash}"

class Blockchain(models.Model):
    block_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)
    data = models.TextField()
    nonce = models.IntegerField(default=0)

    def calculate_hash(self):
        block_string = f"{self.block_number}{self.previous_hash}{self.timestamp}{self.data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        self.hash = self.calculate_hash()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __str__(self):
        return f"Block {self.block_number}"

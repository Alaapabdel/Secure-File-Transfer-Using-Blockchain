# Secure File Transfer Using Blockchain

This project is a secure file transfer application that allows users to upload, download, and transfer files securely. It integrates with the Interplanetary File System (IPFS) for decentralized file storage and uses blockchain technology to record transactions, ensuring data integrity and transparency. The project also includes features for user authentication and wallet management.

## Key Features

- **User Authentication:**
  - Register, login, and logout functionalities.
  - Wallet assignment with an initial balance upon registration.

- **File Upload and Download:**
  - Secure file uploads with encryption and IPFS storage.
  - Malware scanning using the VirusTotal API before uploading.
  - Blockchain records for uploaded files to ensure transaction integrity.

- **File Transfer:**
  - Secure file transfers between registered users.
  - Deduction of a small amount from the sender's wallet for each transfer.
  - Blockchain records for all transfer transactions.

- **Wallet Management:**
  - Track user balances and manage wallet transactions.
  - Reward mechanism for file uploads.

- **Blockchain Integration:**
  - Immutable record-keeping of all transactions.
  - User access to blockchain records for transaction verification.

- **Dashboard:**
  - Access to recent blockchain entries for transaction transparency.

## Technical Components

- **Django Framework:** Core framework for handling HTTP requests, user sessions, and database interactions.
- **IPFS (InterPlanetary File System):** Decentralized storage system for secure file handling.
- **Blockchain:** Ensures data integrity and transparency by recording all transactions.
- **VirusTotal API:** Integrated for malware scanning of files before upload.
- **Cryptography:** Secure file encryption and decryption mechanisms.

## User Flow

1. **Registration and Login:** Users can register with an email and password, and log in to initiate a session.
2. **File Upload:** Users can upload files, which are encrypted and stored securely on IPFS after malware scanning.
3. **File Transfer:** Users can transfer files to others, with the transaction recorded on the blockchain.
4. **File Download:** Secure file download with decryption.
5. **Dashboard Access:** Users can view recent blockchain transactions and verify the integrity of their file activities.

## Summary

This project combines the robust features of Django, IPFS, and blockchain technology to create a secure, transparent, and user-friendly file transfer application. The integration of malware scanning and decentralized storage ensures maximum security and data integrity.

---

### Note
This project was part of my practical work for my Cyber Security Pre-Masters course at Ain Shams University, under the guidance of Professor Tamer Mostafa. I decided to share it publicly after achieving a perfect score of 100/100.

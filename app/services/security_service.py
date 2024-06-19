from base64 import urlsafe_b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from app.config import settings


class EncryptionService:

    @staticmethod
    def generate_password_hash(password):
        password_bytes = password.encode('utf-8')
        algorithm = hashes.SHA256()
        digest = hashes.Hash(algorithm, backend=default_backend())
        digest.update(password_bytes)
        hashed_password = digest.finalize()
        hashed_password_b64 = urlsafe_b64encode(hashed_password).rstrip(b'=').decode('utf-8')
        return hashed_password_b64

    @staticmethod
    def _encrypt_data(key, iv, data):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext

    @staticmethod
    def encrypt_card_data(card_data):
        """
        Шифрует данные карты с использованием указанного ключа и вектора инициализации
        """
        card_name = card_data['card_name']
        card_number = card_data['card_number']
        month = str(card_data['month'])
        year = str(card_data['year'])
        cvv = str(card_data['cvv'])

        encrypted_card_number = EncryptionService._encrypt_field(card_number)
        encrypted_month = EncryptionService._encrypt_field(month)
        encrypted_year = EncryptionService._encrypt_field(year)
        encrypted_cvv = EncryptionService._encrypt_field(cvv)

        encrypted_data = {
            "card_name": card_name,
            "card_number": encrypted_card_number,
            "month": encrypted_month,
            "year": encrypted_year,
            "cvv": encrypted_cvv
        }

        return encrypted_data

    @staticmethod
    def _encrypt_field(field):
        encrypted_field = EncryptionService._encrypt_data(
            settings.aes_key, settings.aes_iv, field.encode()
        ).hex()
        return encrypted_field

    @staticmethod
    def _decrypt_data(key, iv, data):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data

    @staticmethod
    def decrypt_data(encrypted_card_data):
        decrypted_card_number = EncryptionService._decrypt_data(
            settings.aes_key, settings.aes_iv, bytes.fromhex(encrypted_card_data)
        ).decode()
        return decrypted_card_number

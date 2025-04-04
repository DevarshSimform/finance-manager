from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_mask = Fernet(key)

def encrypt_password(password: str) -> str:
    # encode() convert password to byte and decode() will convert it to string
    encrypted_password = cipher_mask.encrypt(password.encode())
    return encrypted_password.decode()

def decrypt_password(e_password: str) -> str:
    decrypted_password = cipher_mask.decrypt(e_password.encode())
    return decrypted_password.decode()


# p = 'Admin@123'

# enc = encrypt_password(p)
# print(enc)
# dec = decrypt_password(enc)
# print(dec)
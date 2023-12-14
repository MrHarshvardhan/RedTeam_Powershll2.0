//python small_master_2_max_file.py -input a -output b

import argparse
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def encrypt_code(code):
    # Generate a random encryption key
    key = os.urandom(32)

    # Generate a random initialization vector (IV)
    iv = os.urandom(16)

    # Create an AES-256 cipher in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    # Create an encryptor object
    encryptor = cipher.encryptor()

    # Create a padder
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    # Pad the code
    padded_code = padder.update(code.encode()) + padder.finalize()

    # Encrypt the padded code
    encrypted_code = encryptor.update(padded_code) + encryptor.finalize()

    # Base64 encode the encrypted code and other parameters
    encoded_key = base64.b64encode(key).decode()
    encoded_iv = base64.b64encode(iv).decode()
    encoded_encrypted_code = base64.b64encode(encrypted_code).decode()

    # Construct the final output code
    output_code = f"""
$key = [System.Convert]::FromBase64String("{encoded_key}")
$iv = [System.Convert]::FromBase64String("{encoded_iv}")
$encryptedCode = [System.Convert]::FromBase64String("{encoded_encrypted_code}")

$decryptor = (New-Object System.Security.Cryptography.AesCryptoServiceProvider).CreateDecryptor($key, $iv)
$decryptedCode = $decryptor.TransformFinalBlock($encryptedCode, 0, $encryptedCode.Length)
$unpadder = (New-Object System.Security.Cryptography.PKCS7Padding).GetType().GetProperty("Mode").SetValue($unpadder, [System.Security.Cryptography.PaddingMode]::None, $null)
$decryptedCode = $unpadder.Unpad($decryptedCode)
$decryptedScript = [System.Text.Encoding]::UTF8.GetString($decryptedCode)
Invoke-Expression $decryptedScript
"""

    return output_code

def save_code(obfuscated_code, output_path):
    # Write the obfuscated code to the selected file path
    with open(output_path, "w") as file:
        file.write(obfuscated_code)

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".ps1"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            with open(input_path, "rb") as input_file:
                code = input_file.read()

            obfuscated_code = encrypt_code(code.decode('utf-8', 'ignore'))
            save_code(obfuscated_code, output_path)

def main():
    parser = argparse.ArgumentParser(description="PowerShell Code Obfuscator")
    parser.add_argument("-input", required=True, help="Input directory containing PowerShell scripts")
    parser.add_argument("-output", required=True, help="Output directory to save obfuscated scripts")
    args = parser.parse_args()

    process_folder(args.input, args.output)

if __name__ == "__main__":
    main()

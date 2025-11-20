# app.py
import os
import subprocess
import tempfile


def decrypt_vault_file(path: str, vault_pass: str) -> str:
    """
    Decrypt een ansible-vault file via de 'ansible-vault' CLI.
    We maken een tijdelijke password-file aan met de inhoud van VAULTPASS.
    """
    # Tijdelijke file met het wachtwoord
    tmp = tempfile.NamedTemporaryFile("w", delete=False)
    try:
        tmp.write(vault_pass)
        tmp.flush()
        pw_path = tmp.name
    finally:
        tmp.close()

    try:
        # ansible-vault decrypt <file> --output=- --vault-password-file=<pwfile>
        result = subprocess.run(
            [
                "ansible-vault",
                "decrypt",
                path,
                "--output=-",
                f"--vault-password-file={pw_path}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout
    finally:
        # passwordfile weer opruimen
        try:
            os.remove(pw_path)
        except FileNotFoundError:
            pass


def main():
    vaultpass = os.getenv("VAULTPASS")
    if not vaultpass:
        raise SystemExit("Environment variabele VAULTPASS is niet gezet")

    plaintext = decrypt_vault_file("secrets.env", vaultpass)

    print("=== Inhoud van secrets.env (decrypted) ===")
    print(plaintext)


if __name__ == "__main__":
    main()



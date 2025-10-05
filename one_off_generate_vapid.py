from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

priv = ec.generate_private_key(ec.SECP256R1())
priv_pem = priv.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()
).decode()

pub = priv.public_key().public_numbers()
x = pub.x.to_bytes(32, "big")
y = pub.y.to_bytes(32, "big")
uncompressed = b"\x04" + x + y
pub_b64url = base64.urlsafe_b64encode(uncompressed).rstrip(b"=").decode()

print("-----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----\n")
print(priv_pem)
print("VAPID_PUBLIC_KEY_B64URL:\n")
print(pub_b64url)

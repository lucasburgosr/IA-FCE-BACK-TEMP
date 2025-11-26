import os
import jwt

key = os.getenv("JWT_SECRET_KEY")
encoded = jwt.encode({"some": "payload"}, key, algorithm="HS256")
# jwt.decode(encoded, key, algorithms="HS256")

print(encoded)
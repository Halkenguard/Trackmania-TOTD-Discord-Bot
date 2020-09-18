import base64

message = "Python is fun"
print(message)
message_bytes = message.encode('ascii')
print(message_bytes)
print(type(message_bytes))
base64_bytes = base64.b64encode(message_bytes)
print(base64_bytes)
base64_message = base64_bytes.decode('ascii')
print(base64_message)
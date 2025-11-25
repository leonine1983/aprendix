from decouple import config

print("--- TESTANDO VALORES ---")
for key in ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]:
    value = config(key)
    print(f"{key}: {value} | type={type(value)}")

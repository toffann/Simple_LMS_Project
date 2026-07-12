import time
from weather_api import get_weather

print("=== Memulai Pengujian Redis Caching ===")

start_time = time.time()
result1 = get_weather("Jakarta")
duration1 = time.time() - start_time
print(f"Panggilan Pertama : {duration1:.2f} detik (Cache Miss)")

start_time = time.time()
result2 = get_weather("Jakarta")
duration2 = time.time() - start_time
print(f"Panggilan Kedua   : {duration2:.2f} detik (Cache Hit)")
print("=======================================")
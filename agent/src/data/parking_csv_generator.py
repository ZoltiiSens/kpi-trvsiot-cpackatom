import random
import csv

data = [["empty_spots"]]

for _ in range(1000):
  free_spots = random.randint(0, 200)
  data.extend([[free_spots] for _ in range(random.randint(2, 20))])

print(data)

with open('parking.csv', 'w', newline='') as csvfile:
   writer = csv.writer(csvfile)
   writer.writerows(data)
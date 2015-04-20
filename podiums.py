import csv

output = csv.writer(open('charts/podium-averages.csv', 'w'))

output.writerow(['race','podium_sum','podium_sum_after','grid_average','average_change','podium_to_average','podium_to_average_per_driver','average_change_to_grid_average'])

for line in csv.reader(open('charts/rate.csv')):
    name = '-'.join(line[:-4])
    values = map(float, line[-4:])
    values.append(values[0] / values[2])
    values.append(values[4] / 3)
    values.append(values[3] / values[2] * 100)
    values[:0] = [name]
    output.writerow(values)

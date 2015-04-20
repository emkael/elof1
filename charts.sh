python charts.py
grep -v '^#' rate.log | grep -v '^$' | paste -s -d ',,,\n'  | grep -f charts/championship-races.csv | sed 's/\(Average\|Podium\) rating\( change\)\?: *//g' | sed 's/\([0-9]\) \([0-9]\)/\1,\2/g' > charts/rate.csv
python podiums.py
rm charts/rate.csv
cat charts/podium-averages.csv | sort --field-separator=',' --key=7 -r | head -n 21 > charts/strongest_podiums.csv
cat charts/podium-averages.csv | head -n 1 > charts/weakest_podiums.csv
cat charts/podium-averages.csv | sort --field-separator=',' --key=7  | tail -n+2 | head -n 20 >> charts/weakest_podiums.csv
cat charts/podium-averages.csv | sort --field-separator=',' --key=8 -r | head -n 21 > charts/biggest_shuffles.csv
cat charts/podium-averages.csv | head -n 1 > charts/smallest_shuffles.csv
cat charts/podium-averages.csv | sort --field-separator=',' --key=8  | head -n 20 >> charts/smallest_shuffles.csv

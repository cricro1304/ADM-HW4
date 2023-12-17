awk -F, '{print $4}' dataset.csv | sort | uniq -c | sort -nr | head -n 1

awk -F, '{duration[$NF] += $3} END {for (id in duration) print duration[id], id}' dataset.csv | sort -nr | head -n 1

awk -F, 'NR>1 {print $2}' dataset.csv | 
while read -r line; do 
    date -j -f "%Y-%m-%d %T" "$line" +%s
done | 
awk 'NR>1 {print $1-prev} {prev=$1}' | 
awk '{sum+=$1; count+=1} END {if (count > 0) print sum/count}'

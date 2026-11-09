import argparse,csv,collections
p=argparse.ArgumentParser();p.add_argument('--input',default='results.csv');a=p.parse_args()
with open(a.input,encoding='utf-8') as f: rows=list(csv.DictReader(f))
for condition in sorted(set(r['condition'] for r in rows)):
    group=[r for r in rows if r['condition']==condition and not r['error']]
    print(condition,':',len(group),'responses; errors:',sum(bool(r['error']) for r in rows if r['condition']==condition))
print('Manually evaluate pacing and humor in the CSV. Demo outputs are synthetic.')

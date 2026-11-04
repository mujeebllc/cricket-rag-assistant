with open('/home/inara/aiproject/backend/unseen_results.txt') as f:
    text = f.read()

blocks = text.split('----------------------------------------------------------------------')
for b in blocks:
    if 'TEST' in b:
        lines = [l.strip() for l in b.strip().split('\n') if l.strip()]
        tname = lines[0]
        res_line = [l for l in lines if 'Result:' in l]
        db_line = [l for l in lines if 'DB Rows:' in l]
        ans_line = [l for l in lines if 'Answer:' in l]
        print(f"{tname:<35} | {res_line[0] if res_line else 'NO RES'}")
        if 'FAIL' in (res_line[0] if res_line else ''):
            print(f"   DB:  {db_line[0] if db_line else ''}")
            print(f"   ANS: {ans_line[0] if ans_line else ''}")

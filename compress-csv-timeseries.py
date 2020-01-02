import fire
from smart_open import open

'''
# Usage

To restore into complete timeseries data.
    
    df = pd.read_csv('test.csv')
    df.index = pd.DatetimeIndex(pd.to_datetime(df.t.values, unit='s'))
    df.drop(columns=['t'], inplace=True)
    df = df.q.resample('15s').ohlc().ffill

'''

def main(input, output):
    with open(output, 'w') as out:
        print('t,q', end='\n', file=out)
        t_prev, q_prev = None, None
        for line in open(input, 'r'):
            line = line.strip()
            if line.startswith('t,q'):
                continue
            t, q = line.split(',')
            t = int(float(t))
            if t == t_prev or q == q_prev:
                continue
            else:
                print(f'{t},{q}', end='\n', file=out)
            t_prev = t
            q_prev = q
        # print last line to get timestamp
        print(f'{t},{q}', end='\n', file=out)


if __name__ == '__main__':
    fire.Fire(main)


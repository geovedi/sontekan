import fire
from smart_open import open

'''
# Usage

To restore into complete timeseries data.
    
    df = pd.read_csv('test.csv')
    df.index = pd.DatetimeIndex(pd.to_datetime(df.t.values, unit='s'))
    df.drop(columns=['t'], inplace=True)
    df.resample('1s').ffill()

'''

def main(input, output):
    with open(output, 'w') as out:
        print('t,q', end='\n', file=out)
        prev = None
        for line in open(input, 'r'):
            line = line.strip()
            if line.startswith('t,q'):
                continue
            t, q = line.split(',')
            if q == prev:
                continue
            else:
                print(f'{line}', end='\n', file=out)
            prev = q
        # print last line to get timestamp
        print(f'{line}', end='\n', file=out)


if __name__ == '__main__':
    fire.Fire(main)


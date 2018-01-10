import sys


def print_reddit_table(df, columns):
    for ix, col in enumerate(columns):
        try:
            df[col] = df[col].round(2)
        except TypeError:
            print(TypeError)
        sys.stdout.write(str(col) + (' | ' if ix is not len(columns) - 1 else ''))
    print('')
    for ix, col in enumerate(columns):
        sys.stdout.write(':--' + (' | ' if ix is not len(columns) - 1 else ''))
    print('')
    for ix, row in df.iterrows():
        for jx, col in enumerate(columns):
            try:
                sys.stdout.write(str(row[col]) + (' | ' if jx is not len(columns) - 1 else ''))
            except UnicodeEncodeError:
                sys.stdout.write(' ' + (' | ' if jx is not len(columns) - 1 else ''))
        print('')

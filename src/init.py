import pathlib
import sys

from .tools import download_db, initialize_db

"""
Initialize a MiniPDB database by downloading minipdb.sqlite or setting up an
empty database with the appropriate tables
"""
def init(args):
    database = args['database']
    if args['download']:
        print('Downloading database...')
        # TODO add sanity checks
        d = pathlib.Path(args['directory'])
        d.mkdir(exist_ok=True)
        p = d / database
        if p.is_file():
            if not args['yes']:
                ans = input(f'File {str(p)} already exists.\n\nDo you want to delete it and proceed?\n\nType Yes to continue: ')
                if ans != 'Yes':
                    sys.exit('Canceled download.')
        p.unlink()
        download_db(p)
    else:
        print('Initializing database...')
        initialize_db(database)
    print('Done.')

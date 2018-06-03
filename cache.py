import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


class SqliteCache:

    connection = None

    def __init__(self, path):

        """ Inits a new SqliteCache instance """

        self.path = os.path.abspath(path)
        logger.debug('Instantiated with cache_db path as {path}'.format(path=self.path))

        # prepare the directory for the cache sqlite db
        os.mkdir(self.path)
        logger.debug('Successfully created the storage path for {path}'.format(path=self.path))

    def _get_conn(self, bookstore):

        if self.connection:
            return self.connection

        cache_db_path = os.path.join(self.path, 'cache.sqlite')

        conn = sqlite3.Connection(cache_db_path, timeout=60)
        logger.debug('Connected to {path}'.format(path=cache_db_path))

        with conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS {} (isbn INTEGER PRIMARY KEY, book_id INTEGER NOT NULL)".format(bookstore))
            logger.debug('Ran the create table')

        self.connection = conn
        return self.connection

    def get(self, bookstore, isbn):
        with self._get_conn(bookstore) as conn:
            cur = conn.cursor()
            cur.execute('SELECT book_id FROM {} WHERE isbn = ?'.format(bookstore), (isbn,))
            return cur.fetchone()

    def set(self, bookstore, isbn, book_id):
        with self._get_conn(bookstore) as conn:
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO {} (isbn, book_id) VALUES (?, ?)'.format(bookstore), (isbn, book_id))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE {} SET book_id=? WHERE isbn = ?'.format(bookstore), (book_id, isbn))

    def remove(self, bookstore, isbn):
        with self._get_conn(bookstore) as conn:
            conn.cursor().execute('DELETE FROM {} WHERE isbn = ?'.format(bookstore), (isbn,))

    def update(self, bookstore, isbn, book_id):
        with self._get_conn() as conn:
            cur = conn.cursor(bookstore)
            cur.execute('UPDATE {} SET book_id=? WHERE isbn = ?'.format(bookstore), (book_id, isbn))

    def clear(self, bookstore):
        with self._get_conn(bookstore) as conn:
            conn.cursor().execute('DELETE FROM {}'.format(bookstore))

    def __del__(self):
        logger.debug('Cleans up the object by destroying the sqlite connection')
        if self.connection:
            self.connection.close()


def cache_book_id(path, cache_table):
    def decorator(fn):
        def wrapped(*args, **kwargs):
            sqlite_cache = SqliteCache(path)
            isbn = args[1]
            book_id = sqlite_cache.get(cache_table, isbn)
            if book_id:
                return book_id
            book_id = fn(*args, **kwargs)
            sqlite_cache.set(cache_table, isbn, book_id)
            return book_id
        return wrapped
    return decorator




import os
import sqlite3
import logging
import re
from functools import wraps
from datetime import datetime, timedelta
from book_review_scraper.exceptions import BookIdCacheMissError, BookIdCacheExpiredError, ISBNError


class SqliteCache:

    connection = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(root_dir, '.cache')
        self.logger.debug('Instantiated with cache_db path as {path}'.format(path=self.path))
        self.expire_time = timedelta(days=7)
        # prepare the directory for the cache sqlite db
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.logger.debug('Successfully created the storage path for {path}'.format(path=self.path))

    def _get_conn(self, cache_table):

        if self.connection:
            return self.connection

        cache_db_path = os.path.join(self.path, 'cache.sqlite')

        conn = sqlite3.connect(cache_db_path, timeout=60,
                               detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.logger.debug('Connected to {path}'.format(path=cache_db_path))

        with conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS {} "
                        "(isbn INTEGER PRIMARY KEY, "
                        "book_id INTEGER NOT NULL, "
                        "updated TIMESTAMP )".format(cache_table))
            self.logger.debug('Ran the create table')

        self.connection = conn
        return self.connection

    def get(self, cache_table, isbn):
        with self._get_conn(cache_table) as conn:
            cur = conn.cursor()
            cur.execute('SELECT book_id, updated '
                        'FROM {} '
                        'WHERE isbn = ?'.format(cache_table), (isbn,))
            rows = cur.fetchone()
            if not rows:
                self.logger.debug(f'{cache_table}, {isbn} cache miss ')
                raise BookIdCacheMissError(table=cache_table, isbn=isbn)
            updated = rows[1]
            now = datetime.now()
            if updated + self.expire_time < now:
                raise BookIdCacheExpiredError(table=cache_table, isbn=isbn)
            return rows[0]

    def set(self, cache_table, isbn, book_id):
        with self._get_conn(cache_table) as conn:
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO {} '
                            '(isbn, book_id, updated) '
                            'VALUES (?, ?, ?)'.format(cache_table), (isbn, book_id, datetime.now()))
                self.logger.debug(f'{cache_table}, insert {isbn} : {book_id}')
            except sqlite3.IntegrityError:
                self.update(cache_table, isbn, book_id)

    def remove(self, cache_table, isbn):
        with self._get_conn(cache_table) as conn:
            conn.cursor().execute('DELETE FROM {}'
                                  ' WHERE isbn = ?'.format(cache_table), (isbn,))
            self.logger.debug(f'{cache_table}, delete {isbn}')

    def update(self, cache_table, isbn, book_id):
        with self._get_conn(cache_table) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE {} '
                        'SET book_id=?, updated=? '
                        'WHERE isbn = ?'.format(cache_table), (book_id, datetime.now(), isbn))
            self.logger.debug(f'{cache_table}, update {isbn} : {book_id}')

    def clear(self, cache_table):
        with self._get_conn(cache_table) as conn:
            conn.cursor().execute('DELETE FROM {}'.format(cache_table))
            self.logger.debug(f'{cache_table}, clear')

    def __del__(self):
        self.logger.debug('Cleans up the object by destroying the sqlite connection')
        if self.connection:
            self.connection.close()


cache = SqliteCache()


def cache_book_id(cache_table):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            isbn13 = args[1]
            if re.match('[\d+]{13}', str(isbn13)) is None:
                raise ISBNError(bookstore=cache_table, isbn=isbn13)
            try:
                book_id = cache.get(cache_table, isbn13)
                return book_id
            except (BookIdCacheMissError, BookIdCacheExpiredError):
                book_id = fn(*args, **kwargs)
                cache.set(cache_table, isbn13, book_id)
                return book_id
        return wrapped
    return decorator

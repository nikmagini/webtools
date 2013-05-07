#/usr/bin/env python
from openid.store  import sqlstore
import logging
from WMCore.Database.DBFactory import DBFactory

class DBOidStore(sqlstore.SQLStore):
    """
    This is a Oracle specialization of SQLStore.

    It uses WMCore.Database, so database config comes from WMCore
    config files.

    To create the tables, call DBOidStore.createTables().
    """

    try:
        import cx_Oracle as exceptions
    except ImportError:
        exceptions = None

    def __init__(self, store_source):
        logging.basicConfig(level = logging.DEBUG,
                format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt = '%m-%d %H:%M')
        self.logger = logging.getLogger('OIDDBOidStore')
        dbi = DBFactory(self.logger, store_source).connect()
        sqlstore.SQLStore.__init__(self, dbi.connection().connection)

    # Oracle queries
    create_nonce_sql = """
    CREATE TABLE %(nonces)s (
        server_url VARCHAR2(2047),
        timestamp INTEGER,
        salt CHAR(40),
        CONSTRAINT nonce_pk PRIMARY KEY (server_url, timestamp, salt)
    )
    """

    create_assoc_sql = """
    CREATE TABLE %(associations)s (
        server_url VARCHAR2(2047) not null,
        handle VARCHAR2(255) not null,
        secret BLOB not null,
        issued INTEGER not null,
        lifetime INTEGER not null,
        assoc_type VARCHAR2(64) not null,
        CONSTRAINT assoc_pk PRIMARY KEY (server_url, handle)
    )
    """

    # set_assoc_sql = (); Replaced by the method db_set_assoc()
    new_assoc_sql = ('INSERT INTO %(associations)s '
                     'VALUES (:1, :2, :3, :4, :5, :6)')
    update_assoc_sql = ('UPDATE %(associations)s SET '
                        'secret = :1, issued = :2, '
                        'lifetime = :3, assoc_type = :4 '
                        'WHERE server_url = :5 AND handle = :6')
    
    get_assoc_sql = ('SELECT handle, secret, issued, lifetime, assoc_type FROM '
                     '%(associations)s WHERE server_url = :1 AND handle = :2')

    get_assocs_sql = ('SELECT handle, secret, issued, lifetime, assoc_type FROM '
                      '%(associations)s WHERE server_url = :1')

    get_expired_sql = ('SELECT server_url FROM '
                       '%(associations)s WHERE issued + lifetime < :1')

    remove_assoc_sql = ('DELETE FROM %(associations)s WHERE '
                        'server_url = :1 AND handle = :2')

    clean_assoc_sql = 'DELETE FROM %(associations)s WHERE issued + lifetime < :1'

    add_nonce_sql = 'INSERT INTO %(nonces)s VALUES (:1, :2, :3)'
    clean_nonce_sql = 'DELETE FROM %(nonces)s WHERE timestamp < :1'

    # replaces set_assoc_sql
    def db_set_assoc(self, server_url, handle, secret, issued, lifetime, assoc_type):
        """
        Set an association.  This is implemented as a method because
        REPLACE INTO is not supported by Oracle (and is not
        standard SQL).
        """
        result = self.db_get_assoc(server_url, handle)
        rows = self.cur.fetchall()
        if len(rows):
            # Update the table since this associations already exists.
            return self.db_update_assoc(secret, issued, lifetime, assoc_type,
                                        server_url, handle)
        else:
            # Insert a new record because this association wasn't
            # found.
            return self.db_new_assoc(server_url, handle, secret, issued,
                                     lifetime, assoc_type)

    def blobDecode(self, buf):
        return str(buf)

    def blobEncode(self, s):
        return buffer(s)


"""Isolated delivery histories: fake receiver and in-memory SQLite, no external effects."""
import sqlite3
import unittest

class Receiver:
    def __init__(self):
        self.receipts = {}
        self.effects = 0

    def charge(self, key, payload):
        if key in self.receipts:
            old, result = self.receipts[key]
            if old != payload:
                raise ValueError('key payload mismatch')
            return result
        self.effects += 1
        result = f'receipt-{self.effects}'
        self.receipts[key] = (payload, result)
        return result

class DeliveryHistories(unittest.TestCase):
    def test_payment_crash_before_local_completion_and_competing_retry(self):
        gateway = Receiver()
        original = gateway.charge('merchant/order/payment-v1', (100, 'USD'))
        # Crash loses local receipt. Both a retry and competing worker replay same key.
        self.assertEqual(original, gateway.charge('merchant/order/payment-v1', (100, 'USD')))
        self.assertEqual(original, gateway.charge('merchant/order/payment-v1', (100, 'USD')))
        self.assertEqual(1, gateway.effects)
        with self.assertRaises(ValueError):
            gateway.charge('merchant/order/payment-v1', (200, 'USD'))

    def test_atomic_inbox_rollback_and_outbox_duplicate_publication(self):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript('CREATE TABLE inbox(scope TEXT, id TEXT, PRIMARY KEY(scope,id)); '
                         'CREATE TABLE orders(id TEXT PRIMARY KEY, fulfilled INTEGER); '
                         'CREATE TABLE outbox(id TEXT PRIMARY KEY); '
                         "INSERT INTO orders VALUES('order',0);")
        def consume(scope, event, crash=False):
            with db:
                cursor = db.execute('INSERT OR IGNORE INTO inbox VALUES(?,?)', (scope,event))
                if not cursor.rowcount:
                    return
                db.execute("UPDATE orders SET fulfilled=fulfilled+1 WHERE id='order'")
                db.execute('INSERT INTO outbox VALUES(?)', (scope + '/' + event,))
                if crash:
                    raise RuntimeError('crash before commit')
        with self.assertRaises(RuntimeError):
            consume('fulfillment', 'event-1', crash=True)
        self.assertEqual(0, db.execute('SELECT count(*) FROM inbox').fetchone()[0])
        self.assertEqual(0, db.execute('SELECT fulfilled FROM orders').fetchone()[0])
        # Dispatcher crashes after publish: same stable event is delivered twice.
        consume('fulfillment', 'event-1')
        consume('fulfillment', 'event-1')
        self.assertEqual(1, db.execute('SELECT fulfilled FROM orders').fetchone()[0])
        self.assertEqual(1, db.execute('SELECT count(*) FROM outbox').fetchone()[0])
        db.execute("INSERT INTO inbox VALUES('analytics','event-1')")
        self.assertEqual(2, db.execute('SELECT count(*) FROM inbox').fetchone()[0])

if __name__ == '__main__':
    unittest.main()

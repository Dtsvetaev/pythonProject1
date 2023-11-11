
import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER,
            phone_number TEXT UNIQUE NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )''')
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute('INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id',
                    (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        conn.commit()

        if phones:
            for phone in phones:
                cur.execute('INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)',
                            (client_id, phone))
                conn.commit()

        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)',
                    (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute('UPDATE clients SET first_name = %s WHERE id = %s', (first_name, client_id))
        if last_name:
            cur.execute('UPDATE clients SET last_name = %s WHERE id = %s', (last_name, client_id))
        if email:
            cur.execute('UPDATE clients SET email = %s WHERE id = %s', (email, client_id))

        if phones is not None:
            cur.execute('DELETE FROM phones WHERE client_id = %s', (client_id,))
            for phone in phones:
                cur.execute('INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)',
                            (client_id, phone))

        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM phones WHERE client_id = %s AND phone_number = %s',
                    (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM clients WHERE id = %s', (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = 'SELECT c.*, p.phone_number FROM clients c LEFT JOIN phones p ON c.id = p.client_id WHERE'
        params = []

        if first_name:
            query += ' c.first_name = %s AND'
            params.append(first_name)
        if last_name:
            query += ' c.last_name = %s AND'
            params.append(last_name)
        if email:
            query += ' c.email = %s AND'
            params.append(email)
        if phone:
            query += ' p.phone_number = %s AND'
            params.append(phone)

        query = query.rstrip(' AND')

        cur.execute(query, tuple(params))
        return cur.fetchall()


with psycopg2.connect(database="SQL_DZ", user="postgres", password="%Rollex77%", host="localhost", port="5432") as conn:

    create_db(conn)


    client_id = add_client(conn, 'Дмитрий', 'Цветаев', 'd@mail.ru', ['+79991234567'])
    print(f"Добавлен клиент с ID: {client_id}")


    change_client(conn, client_id, first_name='Дмитрий', last_name='Цветаев', email='dmitriy@mail.ru', phones=['+79991234568'])


    found_clients = find_client(conn, first_name='Дмитрий')
    for client in found_clients:
        print('Найденный клиент:', client)

    delete_phone(conn, client_id, '+79991234568')


    delete_client(conn, client_id)

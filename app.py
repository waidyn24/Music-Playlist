from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'playlist.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration TEXT NOT NULL
            )
        ''')
        db.commit()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'title')  # По умолчанию сортируем по названию
    conn = get_db_connection()
    songs = conn.execute(f'SELECT * FROM songs ORDER BY {sort_by}').fetchall()
    conn.close()
    return render_template('index.html', songs=songs)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre = request.form['genre']
        duration = request.form['duration']

        conn = get_db_connection()
        conn.execute('INSERT INTO songs (title, artist, genre, duration) VALUES (?, ?, ?, ?)',
                     (title, artist, genre, duration))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    song = conn.execute('SELECT * FROM songs WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre = request.form['genre']
        duration = request.form['duration']

        conn.execute('UPDATE songs SET title = ?, artist = ?, genre = ?, duration = ? WHERE id = ?',
                     (title, artist, genre, duration, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit.html', song=song)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM songs WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']  # Получаем поисковый запрос из формы
        conn = get_db_connection()
        songs = conn.execute('''
            SELECT * FROM songs 
            WHERE title LIKE ? OR artist LIKE ? OR genre LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
        return render_template('search.html', songs=songs)
    return render_template('search.html')


@app.route('/statistics')
def statistics():
    conn = get_db_connection()

    # Общее количество песен
    total_songs = conn.execute('SELECT COUNT(*) FROM songs').fetchone()[0]

    # Количество песен по жанрам
    genre_stats = conn.execute('''
        SELECT genre, COUNT(*) as count 
        FROM songs 
        GROUP BY genre
    ''').fetchall()

    # Самые популярные исполнители (топ 5)
    popular_artists = conn.execute('''
        SELECT artist, COUNT(*) as count 
        FROM songs 
        GROUP BY artist 
        ORDER BY count DESC 
        LIMIT 5
    ''').fetchall()

    conn.close()

    return render_template(
        'statistics.html',
        total_songs=total_songs,
        genre_stats=genre_stats,
        popular_artists=popular_artists
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
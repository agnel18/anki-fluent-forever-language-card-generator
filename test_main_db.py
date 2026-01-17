import sqlite3

def test_main_database():
    try:
        conn = sqlite3.connect('streamlit_app/language_learning.db')
        cursor = conn.cursor()

        # Test basic queries
        cursor.execute('SELECT COUNT(*) FROM words WHERE lang_code = "hi"')
        hindi_count = cursor.fetchone()[0]
        print(f'Hindi words: {hindi_count}')

        cursor.execute('SELECT word, frequency FROM words WHERE lang_code = "hi" ORDER BY frequency DESC LIMIT 5')
        hindi_words = cursor.fetchall()
        print('Top 5 Hindi words by frequency:')
        for word, freq in hindi_words:
            print(f'  {word}: {freq}')

        # Test other languages
        cursor.execute('SELECT lang_code, COUNT(*) FROM words GROUP BY lang_code ORDER BY COUNT(*) DESC LIMIT 5')
        lang_counts = cursor.fetchall()
        print('\nLanguage counts:')
        for lang, count in lang_counts:
            print(f'  {lang}: {count}')

        conn.close()
        print('\nDatabase appears to be working correctly!')

    except Exception as e:
        print(f'Database error: {e}')

if __name__ == "__main__":
    test_main_database()
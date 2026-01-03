import pandas as pd
import sys
import os
sys.path.append('d:\\Language Learning\\LanguagLearning')

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def test_top_words():
    """Test top 1000 Hindi words for color consistency and grammatical role accuracy"""

    # Load frequency list
    df = pd.read_excel('77 Languages Frequency Word Lists/Hindi (HI).xlsx')
    top_words = df['Hindi Word'].head(1000).tolist()

    analyzer = HiAnalyzer()
    results = []

    print(f"Testing top {len(top_words)} Hindi words for anomalies...")

    for i, word in enumerate(top_words):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(top_words)} words tested")

        try:
            # Create a simple sentence with the word
            test_sentence = f"यह {word} है।"  # "This is [word]."

            # Analyze grammar
            result = analyzer.analyze_grammar(test_sentence, word, "intermediate", "dummy_key")

            # Check for anomalies
            anomalies = []

            # Check if word appears in word_explanations
            word_in_explanations = any(exp[0] == word for exp in result.word_explanations)
            if not word_in_explanations:
                anomalies.append("word_not_in_explanations")

            # Check for grey colors (indicates 'other' category)
            grey_words = [exp[0] for exp in result.word_explanations if exp[2] == '#888888']
            if grey_words:
                anomalies.append(f"grey_words: {grey_words}")

            # Check for postpositions that should be blue
            postpositions = ['में', 'से', 'को', 'का', 'पर', 'तक', 'के', 'ने']
            for exp in result.word_explanations:
                if exp[0] in postpositions and exp[2] != '#4444FF':
                    anomalies.append(f"postposition_wrong_color: {exp[0]}={exp[2]}")

            if anomalies:
                results.append({
                    'word': word,
                    'rank': i+1,
                    'anomalies': anomalies,
                    'word_explanations': result.word_explanations,
                    'sentence': test_sentence
                })

        except Exception as e:
            results.append({
                'word': word,
                'rank': i+1,
                'anomalies': [f"error: {str(e)}"],
                'word_explanations': [],
                'sentence': test_sentence
            })

    # Report findings
    print(f"\n=== ANOMALY REPORT ===")
    print(f"Total words tested: {len(top_words)}")
    print(f"Words with anomalies: {len(results)}")

    if results:
        print("\nTop anomalies:")
        for result in results[:20]:  # Show first 20
            print(f"#{result['rank']}: {result['word']} - {result['anomalies']}")

        # Save detailed results
        with open('hindi_top1000_anomalies.txt', 'w', encoding='utf-8') as f:
            f.write("Hindi Top 1000 Words - Anomaly Report\n")
            f.write("=" * 50 + "\n\n")
            for result in results:
                f.write(f"Rank #{result['rank']}: {result['word']}\n")
                f.write(f"Sentence: {result['sentence']}\n")
                f.write(f"Anomalies: {result['anomalies']}\n")
                f.write("Word explanations:\n")
                for exp in result['word_explanations']:
                    f.write(f"  {exp}\n")
                f.write("\n" + "-"*50 + "\n")

        print(f"\nDetailed results saved to hindi_top1000_anomalies.txt")
    else:
        print("✅ No anomalies found in top 1000 words!")

if __name__ == "__main__":
    test_top_words()
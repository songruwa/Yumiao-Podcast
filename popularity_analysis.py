import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_word_counts(text_file):
    with open(text_file, 'r') as f:
        text = f.read()
    intervals = re.findall(r'\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\]', text)
    words = re.findall(r'\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\] (.*)', text)
    return [len(word.split()) for word, interval in zip(words, intervals) if get_seconds(interval) <= 5]

def get_seconds(interval):
    start, end = re.findall(r'\d+:\d+\.\d+', interval)
    start_min, start_sec = map(float, start.split(':'))
    end_min, end_sec = map(float, end.split(':'))
    return (end_min * 60 + end_sec) - (start_min * 60 + start_sec)

def get_audio_duration(text_file):
    with open(text_file, 'r') as f:
        last_line = f.readlines()[-1]
    interval_match = re.search(r'\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\]', last_line)
    if interval_match is None:
        print(f"Warning: Could not find interval in file {text_file}")
        return 0
    else:
        return get_seconds(interval_match.group(0))

def analyze_category(category):
    sequence_file = os.path.join(category, 'sequence.txt')  
    with open(sequence_file, 'r') as f:
        sequence_titles = [line.strip() for line in f.read().splitlines()]
    durations = []
    word_counts = []
    for rank, title in enumerate(sequence_titles):
        clean_title = re.sub(r'^\d+\.\s', '', title)
        text_file_path = os.path.join(category, 'text', clean_title + '.txt')  
        durations.append(get_audio_duration(text_file_path))
        word_counts.append(sum(get_word_counts(text_file_path)))
    return pd.DataFrame({'rank': range(1, len(sequence_titles) + 1), 'duration': durations, 'word_count': word_counts})

def main():
    categories = ['人文', '健康', '国学', '头条', '影视', '科技', '评书', '商业管理', '投资理财']
    for category in categories:
        df = analyze_category(category)
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(df['rank'], df['duration'])
        plt.xlabel('Rank')
        plt.ylabel('Duration (seconds)')
        plt.title('Duration vs Rank in {}'.format(category))
        plt.subplot(1, 2, 2)
        plt.plot(df['rank'], df['word_count'])
        plt.xlabel('Rank')
        plt.ylabel('Word Count')
        plt.title('Word Count vs Rank in {}'.format(category))
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    main()

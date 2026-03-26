# IR Explorer

An educational desktop application for learning Information Retrieval through interactive exploration and guided lessons.

## Download

| Platform | Download |
|----------|----------|
| **Windows** | [IR_Explorer_Setup.exe](https://github.com/Theodor908/IR-Explorer/releases/latest/download/IR_Explorer_Setup.exe) |
| **macOS** | [IR_Explorer.app.zip](https://github.com/Theodor908/IR-Explorer/releases/latest/download/IR_Explorer.app.zip) |
| **Linux** | [IR_Explorer_Linux.tar.gz](https://github.com/Theodor908/IR-Explorer/releases/latest/download/IR_Explorer_Linux.tar.gz) |

## What is IR Explorer?

IR Explorer teaches Information Retrieval concepts through hands-on interaction. Instead of reading about how search engines work, you build indexes, run queries, and watch algorithms step through their execution, all in a visual desktop app.

It covers the full IR pipeline:
- Text preprocessing (tokenization, stopwords, stemming)
- Inverted index construction
- Boolean and ranked retrieval (TF-IDF, cosine similarity)
- Evaluation metrics (precision, recall, MAP)
- Web crawling (BFS/DFS)
- Link analysis (PageRank, HITS)

## Features

### Learn Mode
Nine structured lessons guide you from basic tokenization through PageRank. Each lesson has:
- **Theory** - clear explanations of each concept
- **Animated demos** - step-by-step visualizations with playback controls
- **Experiments** - prompts to try things in Explore mode
- **Checkpoints** - self-test questions with revealable answers

Lessons auto-advance and track your progress across sessions.

### Explore Mode
Ten interactive tabs for free-form experimentation:

| Tab | What you can do |
|-----|----------------|
| **Corpus** | Import PDFs, load example corpora, generate synthetic corpora, edit documents |
| **Index** | Build and browse the inverted index, inspect postings lists |
| **Search** | Run Boolean (AND/OR/NOT) or TF-IDF ranked queries |
| **Vocabulary** | View term frequencies, Zipf's law plots, toggle stopwords |
| **Postings** | Examine document frequency distributions |
| **Pipeline** | See preprocessing stages side by side (raw -> stopwords -> stemmed) |
| **Compare** | Jaccard similarity between documents with heatmap |
| **Evaluation** | Mark relevant docs, compute precision/recall, plot PR curves |
| **Crawler** | Simulate BFS/DFS crawling on a link graph |
| **Link Analysis** | Run PageRank or HITS and watch scores converge |

### Other Features
- **Configurable stemmer** - add, remove, or reorder suffix rules via Settings
- **PDF import** - split by titles, subtitles, or import as a single document
- **Corpus generator** - create synthetic corpora with controllable vocabulary overlap and reproducible seeds
- **Live document editing** - modify document text directly in the Corpus tab
- **Contextual hints** - collapsible explanation panels in each tab

## Screenshots

<img width="1198" height="841" alt="Captură de ecran 2026-03-26 030030" src="https://github.com/user-attachments/assets/1995a51a-eff8-476f-bbfd-48a91f16f09a" />

<img width="1201" height="849" alt="Captură de ecran 2026-03-26 030306" src="https://github.com/user-attachments/assets/6fab5ddf-3d61-41d6-ba36-b9507abadfd6" />

<img width="1192" height="847" alt="Captură de ecran 2026-03-26 030056" src="https://github.com/user-attachments/assets/292288fb-b4f1-4d35-b4c2-62fb2e5de889" />

<img width="1198" height="857" alt="Captură de ecran 2026-03-26 030241" src="https://github.com/user-attachments/assets/00dadf97-5b9c-40d8-a8ce-1e0dee7d416e" />

## Default Corpus

The app ships with 13 documents extracted from three research papers:

- **Tegmark (2005)** - *"The Multiverse Hierarchy"* (documents d1-d5)
- **Guth (2007)** - *"Eternal Inflation and its Implications"* (documents d6-d9)
- **Blackshaw & Franklin (2026)** - *"Everettian Interpretations of Quantum Mechanics"* (documents d10-d13)

Two curated example corpora are also included:
- **Synonyms corpus** - demonstrates vocabulary normalization challenges
- **Link Structure corpus** - hand-crafted citation graph for crawler and PageRank demos

## Documentation

Full documentation is available in [`IR_Explorer_Documentation.docx`](IR_Explorer_Documentation.docx) in this repository.

## Running from Source

Requirements: Python 3.10+

```bash
pip install numpy PyMuPDF pyyaml
python -m ir_explorer.main
```

## Building the Installer

```bash
pip install pyinstaller
python build_installer.py
```

This runs PyInstaller to bundle the app, then generates an Inno Setup script. If Inno Setup 6 is installed, it compiles the installer automatically.

## Project Structure

```text
ir_explorer/
|-- main.py                 # entry point
|-- app.py                  # main window, mode switching
|-- settings.py             # persistent settings
|-- core/                   # IR algorithms (no UI dependencies)
|   |-- preprocessing.py    # tokenize, stopwords, stemming
|   |-- index.py            # inverted index
|   |-- retrieval.py        # boolean + TF-IDF search
|   |-- evaluation.py       # precision, recall, MAP
|   |-- crawler.py          # BFS/DFS + link graph
|   |-- link_analysis.py    # PageRank, HITS
|   |-- corpus_generator.py # synthetic corpus generation
|   `-- pdf_reader.py       # PDF text extraction
|-- lessons/                # learn mode
|   |-- engine.py           # lesson state machine
|   |-- registry.py         # YAML loader
|   |-- animations.py       # demo step generators
|   `-- definitions/        # 9 lesson YAML files
|-- ui/
|   |-- explore/            # 10 explore mode tabs
|   |-- learn/              # lesson navigator + viewer
|   |-- widgets/            # hint box, animated canvas, parameter controls
|   |-- mode_switcher.py
|   |-- suffix_dialog.py
|   `-- theme.py
`-- assets/
    |-- default_corpus.json
    |-- icon.ico
    |-- icon.png
    `-- corpora/            # curated example corpora
```

## License

Released under the MIT License. See `LICENSE`.

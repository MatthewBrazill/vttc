# VTTC (WebVTT Converter)

A tiny command-line tool that converts **Zoom** and **Google Meet** transcript exports into **WebVTT** subtitle tracks.

The output is a valid `.vtt` file that can be used with video players and transcription tools that accept WebVTT.

---

## Install (macOS / Linux)

You can install the tool in one step and make it available as `vttc` on your PATH.

```bash
curl -Lo /usr/local/bin/vttc https://raw.githubusercontent.com/MatthewBrazill/vttc/main/convert.py && chmod +x /usr/local/bin/vttc
```

If you don’t have permission to write to `/usr/local/bin`, install it into `~/bin` and ensure that directory is on your `PATH`:

```bash
mkdir -p ~/bin && curl -Lo ~/bin/vttc https://raw.githubusercontent.com/MatthewBrazill/vttc/main/convert.py && chmod +x ~/bin/vttc
```

---

## How it works (quick overview)

`vttc` reads a transcript export and produces a clean WebVTT file that timestamps each line.

### Supported input formats

- **Zoom transcript** (default format exported from Zoom meetings)
- **Google Meet transcript** (exported from Google Meet)

### What you get

- A `WEBVTT` file with cue timing derived from the transcript timestamps.
- Each line is treated as a subtitle cue and includes the speaker label (where available).
- A small default “end” buffer is applied to the final cue so the file is always valid.

---

## Basic usage

```bash
vttc -i path/to/transcript.txt -o out.vtt
```

### Options

- `-i`, `--file` &nbsp;&nbsp;&nbsp;Input transcript file (required)
- `-o`, `--output` &nbsp;&nbsp;&nbsp;Output file (defaults to `output.vtt`)
- `-f`, `--force` &nbsp;&nbsp;&nbsp;Continue even if some timestamps can’t be parsed (skips invalid blocks)

---

## Examples

Sample transcripts are included in `examples/`:

- `examples/google-example.txt` → `examples/google-out.vtt`
- `examples/zoom-example.txt` → `examples/zoom-out.vtt`

Run the converter against an example to see the output:

```bash
vttc -i examples/google-example.txt -o examples/google-out.vtt
```

---

## Contributing / How it works (developer notes)

### Key behavior

- The script detects Zoom transcripts by checking if the first character of the file is `[`.
- Google Meet transcripts are detected by falling back on splitting on blank-line blocks.
- Each parsed block becomes one or more WebVTT cues.
- The end timestamp for each cue is derived from the start time of the next cue (or set to +3 seconds for the last cue).

### Extending the tool

If you want to improve or extend the converter:

1. Add new transcript format parsing in `convert.py`.
2. Add more robust timestamp parsing (the current code expects `HH:MM:SS` or `HH:MM:SS.sss`).

### Running tests

This repo includes a small suite of unit tests that validate the converter against the example inputs.

Run them with:

```bash
python3 -m unittest
```

or (to run a single test file):

```bash
python3 -m unittest tests.test_convert
```

The tests compare the generated `.vtt` output against the `examples/*.vtt` reference files.

### Style and conventions

- The repository is intentionally minimal and depends only on Python’s standard library.
- Keep changes small and focused—this tool is meant to stay lightweight.

---

## 🧾 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

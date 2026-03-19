#!/usr/bin/python3

import argparse
import re
from datetime import datetime
from datetime import timedelta

def main(i, o=None, f=False):
    try:
        vtt_content = []
        content = []
        with open(i, 'r') as infile:
            input = infile.read().strip()

        try:
            if input[0] == "[": # Zoom transcript
                content = input.split("\n\n")
                for line in content:
                    title = line.split("\n")[0].split(" ")
                    timestamp = title.pop()
                    try:
                        timestamp = datetime.strptime(timestamp, "%H:%M:%S.%f")
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp, "%H:%M:%S")
                        except ValueError as err:
                                if f == True:
                                    print(f"WARN: Error parsing timestamp '{timestamp}'; skipping block.")
                                    continue
                                else:
                                    raise err

                    vtt_content.append({
                        "timestamp": timestamp,
                        "speaker": " ".join(title).strip("]["),
                        "text": line.split("\n")[1]
                    })

            else: # Google Meet transcript
                content = input.split("\n", 2)[-1].split("\n \n \n")
                if re.compile(r"^\d{2}:\d{2}:\d{2}(?:\.\d+)?$").match(content[-1]) is None:
                #if content[-1].startswith("Transcription"):
                    content.pop()
                for i, block in enumerate(content):
                    allText = block.split("\n \n")[1].split("\n")
                    initialTs = None
                    nextTs = None

                    try:
                        initialTs = datetime.strptime(block.split("\n \n")[0], "%H:%M:%S.%f")
                    except ValueError:
                        try:
                            initialTs = datetime.strptime(block.split("\n \n")[0], "%H:%M:%S")
                        except ValueError as err:
                                if f == True:
                                    errorTs = block.split('\n \n')[0]
                                    print(f"WARN: Error parsing timestamp '{errorTs}'; skipping block.")
                                    continue
                                else:
                                    raise err

                    if i < len(content)-1:
                        try:
                            nextTs = datetime.strptime(content[i+1].split("\n \n")[0], "%H:%M:%S.%f")
                        except ValueError:
                            try:
                                nextTs = datetime.strptime(content[i+1].split("\n \n")[0], "%H:%M:%S")
                            except ValueError as err:
                                if f == True:
                                    errorTs = content[i+1].split('\n \n')[0]
                                    print(f"WARN: Error parsing timestamp '{errorTs}'; skipping block.")
                                    continue
                                else:
                                    raise err
                    else:
                        nextTs = initialTs + timedelta(0,len(allText))

                    secondsPerLine = timedelta(0,(nextTs - initialTs).total_seconds() / len(allText))
                    for i, line in enumerate(allText, 1):
                        vtt_content.append({
                            "timestamp": initialTs + secondsPerLine * i,
                            "speaker": line.split(":")[0],
                            "text": " ".join(line.split(":")[1:]).strip()
                        })

            output = "WEBVTT\n\n"
            for i, item in enumerate(vtt_content):
                if i < len(vtt_content)-1:
                    output += f"{item['timestamp'].strftime('%H:%M:%S.%f')[:-3]} --> {vtt_content[i+1]['timestamp'].strftime('%H:%M:%S.%f')[:-3]}\n{item['speaker']}: {item['text']}\n\n"
                else: 
                    output += f"{item['timestamp'].strftime('%H:%M:%S.%f')[:-3]} --> {(item['timestamp'] + timedelta(0,3)).strftime('%H:%M:%S.%f')[:-3]}\n{item['speaker']}: {item['text']}\n\n"

            try:
                if o:
                    with open(o, 'w') as outfile:
                        outfile.write(output)
                    print(f"Output written to '{o}'")
                else:
                    with open("output.vtt", 'w') as outfile:
                        outfile.write(output)
                    print(f"Output written to 'output.vtt'")
            except Exception as e:
                print(f"Error writing output file: {e}")
                exit(1)

        except Exception as e:
            print(f"Error processing file: {e}")
            print(f"\nAre you sure this is a Zoom or Google Meet transcript?")
            exit(1)

    except Exception as e:
        print(f"Error reading file {i}: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to convert Zoom and Google Meet transcripts into functional VTT scripts for Homerun.")
    parser.add_argument("-i", "--file", help="Input file")
    parser.add_argument("-o", "--output", default=None, help="Output file (optional)")
    parser.add_argument("-f", "--force", default=False, help="Force conversion even if there are timestamp errors (optional)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.4")
    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        exit(1)
    main(args.file, args.output, args.force)
#!/usr/bin/python3

import argparse
import os
import re
from datetime import datetime
from datetime import timedelta

def main(input_file, output_file=None, force=False, replace=False):
    try:
        vtt_content = []
        content = []
        with open(input_file, 'r') as infile:
            input_data = infile.read().strip()

        try:
            if input_data and input_data[0] == "[": # Zoom transcript
                content = input_data.split("\n\n")
                for line in content:
                    title = line.split("\n")[0].split(" ")
                    timestamp = title.pop()
                    try:
                        timestamp = datetime.strptime(timestamp, "%H:%M:%S.%f")
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp, "%H:%M:%S")
                        except ValueError as err:
                                if force == True:
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
                content = input_data.split("\n", 2)[-1].split("\n \n \n")
                if re.compile(r"^\d{2}:\d{2}:\d{2}(?:\.\d+)?$").match(content[-1]) is None:
                #if content[-1].startswith("Transcription"):
                    content.pop()
                for idx, block in enumerate(content):
                    allText = block.split("\n \n")[1].split("\n")
                    initialTs = None
                    nextTs = None

                    try:
                        initialTs = datetime.strptime(block.split("\n \n")[0], "%H:%M:%S.%f")
                    except ValueError:
                        try:
                            initialTs = datetime.strptime(block.split("\n \n")[0], "%H:%M:%S")
                        except ValueError as err:
                                if force == True:
                                    errorTs = block.split('\n \n')[0]
                                    print(f"WARN: Error parsing timestamp '{errorTs}'; skipping block.")
                                    continue
                                else:
                                    raise err

                    if idx < len(content)-1:
                        try:
                            nextTs = datetime.strptime(content[idx+1].split("\n \n")[0], "%H:%M:%S.%f")
                        except ValueError:
                            try:
                                nextTs = datetime.strptime(content[idx+1].split("\n \n")[0], "%H:%M:%S")
                            except ValueError as err:
                                if force == True:
                                    errorTs = content[idx+1].split('\n \n')[0]
                                    print(f"WARN: Error parsing timestamp '{errorTs}'; skipping block.")
                                    continue
                                else:
                                    raise err
                    else:
                        nextTs = initialTs + timedelta(0,len(allText))

                    secondsPerLine = timedelta(0,(nextTs - initialTs).total_seconds() / len(allText))
                    for line_idx, line in enumerate(allText, 1):
                        vtt_content.append({
                            "timestamp": initialTs + secondsPerLine * line_idx,
                            "speaker": line.split(":")[0],
                            "text": " ".join(line.split(":")[1:]).strip()
                        })

            output = "WEBVTT\n\n"
            for item_idx, item in enumerate(vtt_content):
                if item_idx < len(vtt_content)-1:
                    output += f"{item['timestamp'].strftime('%H:%M:%S.%f')[:-3]} --> {vtt_content[item_idx+1]['timestamp'].strftime('%H:%M:%S.%f')[:-3]}\n{item['speaker']}: {item['text']}\n\n"
                else: 
                    output += f"{item['timestamp'].strftime('%H:%M:%S.%f')[:-3]} --> {(item['timestamp'] + timedelta(0,3)).strftime('%H:%M:%S.%f')[:-3]}\n{item['speaker']}: {item['text']}\n\n"

            try:
                if replace:
                    target_file = input_file
                elif output_file:
                    target_file = output_file
                else:
                    target_file = "output.vtt"

                with open(target_file, 'w') as outfile:
                    outfile.write(output)

                if replace:
                    final_file = os.path.splitext(input_file)[0] + ".vtt"
                    if os.path.abspath(final_file) != os.path.abspath(input_file):
                        os.replace(input_file, final_file)
                    else:
                        final_file = input_file
                    print(f"Output written to '{final_file}'")
                else:
                    print(f"Output written to '{target_file}'")
            except Exception as e:
                print(f"Error writing output file: {e}")
                exit(1)

        except Exception as e:
            print(f"Error processing file: {e}")
            print(f"\nAre you sure this is a Zoom or Google Meet transcript?")
            exit(1)

    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to convert Zoom and Google Meet transcripts into functional VTT scripts for Homerun.")
    parser.add_argument("-i", "--file", help="Input file")
    parser.add_argument("-o", "--output", default=None, help="Output file (optional)")
    parser.add_argument("-r", "--replace", action="store_true", default=False, help="Replace input file and rename to .vtt")
    parser.add_argument("-f", "--force", action="store_true", default=False, help="Force conversion even if there are timestamp errors (optional)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.4")
    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        exit(1)
    main(args.file, args.output, args.force, args.replace)
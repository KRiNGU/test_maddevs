import sys
from msg_split import split_message

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("UsageError: python msg_split.py [--max_len <max_len>] <input_file>")
        sys.exit(1)
    print(sys.argv)

    input_file = sys.argv[1]

    try:
        if len(sys.argv) == 3 and sys.argv[1].startswith("--max_len="):
            input_file = sys.argv[2]
            max_len = int(sys.argv[1].split("=", 1)[1])
    except ValueError:
        print("ValueError: <max_length> must be an integer.")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as source:
        gen = split_message(source=source, max_len=max_len)
        i = 1
        try:
            for res in gen:
                print(f"fragment #{i}: {len(res)} chars")
                print(res)
                i += 1
        except Exception as e:
            print(e)

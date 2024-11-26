import sys
from msg_split import split_message, MAX_LEN
import click


@click.command()
@click.option("--max_len", default=MAX_LEN, type=int, is_eager=True)
@click.argument("input_file", type=click.Path(exists=True))
def process_file(max_len, input_file):
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


if __name__ == "__main__":
    process_file()

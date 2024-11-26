from typing import Generator
from bs4 import BeautifulSoup

MAX_LEN = 4096


class NotEnoughtFragmentLen(Exception):
    def __init__(self, fragment: str, current_node: str, close_tags: str, max_len: int):
        super().__init__(
            f"Fragment exceeds maximum length: {len(fragment) + len(current_node) + len(close_tags)} > {max_len}"
        )


class NotEnoughtFragmentLenForInitialization(Exception):
    def __init__(self, max_len: int):
        super().__init__(
            f"Not enough fragment len for initialization, max len: {max_len}"
        )


class EmptySourceString(Exception):
    def __init__(self):
        super().__init__(f"Empty source string, nothing to parse")


def get_attr(k: str, v: str) -> str:
    return f'{k}="{v}"'


def get_open_tags(tags: list[BeautifulSoup]) -> str:
    return "".join(
        f"<{tag.name}{' ' + ' '.join(get_attr(k,v) for k, v in tag.attrs.items()) if tag.attrs else ''}>"
        for tag in tags
    )


def get_close_tag(name: str) -> str:
    return f"</{name}>"


def get_close_tags(tags: list[BeautifulSoup]) -> str:
    return "".join(get_close_tag(tag.name) for tag in reversed(tags))


def count_fragment_len_with_close_tags(
    fragment: str, current_node_len: int, close_tags: str
) -> str:
    return len(fragment) + current_node_len + len(close_tags)


def split_message(source: str, max_len=MAX_LEN) -> Generator[str, None, None]:
    """Splits the original message (`source`) into fragments of the specified length
    (`max_len`)."""

    if not isinstance(max_len, int):
        raise TypeError("The max_len can only be int")

    block_tags: set = {"p", "b", "strong", "i", "ul", "ol", "div", "span"}
    close_block_tags: set = {
        "</p>",
        "</b>",
        "</strong>",
        "</i>",
        "</ul>",
        "</ol>",
        "</div>",
        "</span>",
    }
    soup = BeautifulSoup(source, "html.parser")
    fragment = ""
    tag_stack: list[BeautifulSoup] = []
    node_stack: list[BeautifulSoup] = []

    if not soup.contents:
        raise EmptySourceString()

    # Добавляем всех прямых children soup объекта
    for content in soup.contents:
        node_stack.append(content)

    while node_stack:
        current_node: BeautifulSoup = node_stack[0]
        close_tags_string: str = get_close_tags(tag_stack)

        # Если мы встречаем заранее положенный закрывающий тег, то просто дописываем его в строку
        if current_node in close_block_tags:
            node = tag_stack.pop()
            tag_close = current_node
            fragment += tag_close
            node_stack.pop(0)
            continue
        # Так как все элементы не из block_tags разбивать мы не можем, то рассматриваем их как атомарную единицу
        elif isinstance(current_node, str) or current_node.name not in block_tags:
            if (
                count_fragment_len_with_close_tags(
                    fragment, len(str(current_node)), close_tags_string
                )
                > max_len
            ):
                res = fragment + close_tags_string
                fragment = get_open_tags(tag_stack)
                # Фактически если мы не смогли положить в результат ничего,
                # то размер фрагмента недостаточен для помещения туда символа строки/неблочного тега даже в единичном виде
                if not res:
                    raise NotEnoughtFragmentLenForInitialization(max_len=max_len)
                yield res
                # Если после выставления открывающих тегов мы обнаруживаем, суммарная длина открытия и закрытия тегов с контентом
                # больше допустимой длины фрагмента, то эти фрагменты могут обслуживать только открытие и закрытие тегов -> длины фрагмента недостаточно
                if (
                    count_fragment_len_with_close_tags(
                        fragment, len(str(current_node)), close_tags_string
                    )
                    > max_len
                ):
                    raise NotEnoughtFragmentLen(
                        fragment=fragment,
                        current_node=str(current_node),
                        close_tags=close_tags_string,
                        max_len=max_len,
                    )
                    continue
            fragment += str(current_node)
            node_stack.pop(0)
            continue
        # Аналогично для блочных, мы пытаемся положить хотя бы один валидный блок с полной информацией и своим закрывающим тегом
        if (
            count_fragment_len_with_close_tags(
                fragment,
                len(get_open_tags([current_node]))
                + len(get_close_tag(current_node.name)),
                close_tags_string,
            )
            > max_len
        ):
            res = fragment + close_tags_string
            fragment = get_open_tags(tag_stack)
            # Размер фрагмента не достаточен для помещения туда блока
            if not res:
                raise NotEnoughtFragmentLenForInitialization(max_len=max_len)
            yield res
            # Аналогично мы не можем позволить фрагментам обслуживать только открытие и закрытие тегов
            if (
                count_fragment_len_with_close_tags(
                    fragment,
                    len(get_open_tags([current_node]))
                    + len(get_close_tag(current_node.name)),
                    close_tags_string,
                )
                > max_len
            ):
                raise NotEnoughtFragmentLen(
                    fragment=fragment,
                    current_node=str(current_node),
                    close_tags=close_tags_string,
                    max_len=max_len,
                )
            continue
        else:
            # Если это блочная нода и мы можем её добавить, то добавляем её к стеку тегов для дальнейшего закрытия при переполнении размер фрагмента
            tag_stack.append(current_node)

        tag_open = get_open_tags([current_node])
        fragment += tag_open
        node_stack.pop(0)
        node_stack = (
            current_node.contents + [get_close_tag(current_node.name)] + node_stack
        )
    yield fragment

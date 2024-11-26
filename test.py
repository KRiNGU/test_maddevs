import msg_split
import unittest
from bs4 import BeautifulSoup


class TestGetAttrFunction(unittest.TestCase):
    def test_tag(self):
        k, v = "style", "display: block"
        self.assertEqual(msg_split.get_attr(k, v), 'style="display: block"')

    def test_tag_nums(self):
        k, v = 1, 2
        self.assertEqual(msg_split.get_attr(k, v), '1="2"')


class TestGetOpenCloseTags(unittest.TestCase):

    def setUp(self):
        self.tags = [
            BeautifulSoup('<div style="diplay: block"></div>', "html.parser").contents[
                0
            ],
            BeautifulSoup('<p fontsize="10"></p>', "html.parser").contents[0],
        ]

    def test_get_open_tags(self):
        self.assertEqual(
            msg_split.get_open_tags(self.tags),
            '<div style="diplay: block"><p fontsize="10">',
        )

    def test_get_single_open_tag(self):
        self.assertEqual(
            msg_split.get_open_tags(self.tags[0:1]), '<div style="diplay: block">'
        )

    def test_get_close_tags(self):
        self.assertEqual(
            msg_split.get_close_tags(self.tags),
            "</p></div>",
        )

    def test_get_single_close_tags(self):
        self.assertEqual(
            msg_split.get_close_tags(self.tags[0:1]),
            "</div>",
        )

    def test_get_close_tag_string(self):
        self.assertEqual(msg_split.get_close_tag("div"), "</div>")

    def test_get_close_tags_attribute_error(self):
        with self.assertRaises(AttributeError):
            msg_split.get_close_tags(["<div></div>"])
        with self.assertRaises(AttributeError):
            msg_split.get_close_tags("<div></div>")


class TestCountFragmentLenWithCloseTags(unittest.TestCase):
    def setUp(self):
        self.tags = [
            BeautifulSoup('<div style="diplay: block"></div>', "html.parser").contents[
                0
            ],
            BeautifulSoup('<p fontsize="10"></p>', "html.parser").contents[0],
        ]
        self.fragment = "<div>First part of fragment</div>"
        self.current_node_len = 13

    def test_count(self):
        res = msg_split.count_fragment_len_with_close_tags(
            self.fragment, self.current_node_len, self.tags
        )
        self.assertEqual(res, 48)

    def test_type_error(self):
        with self.assertRaises(TypeError):
            msg_split.count_fragment_len_with_close_tags(48, 13, self.tags)
        with self.assertRaises(TypeError):
            msg_split.count_fragment_len_with_close_tags(self.fragment, 13, 45)


class TestSplitMessage(unittest.TestCase):
    def setUp(self):
        self.html_path = "test_source.html"
        self.html_string = '<strong>Done</strong> <i>\
                            <a href="https://mockdata.atlassian.net/browse/ABC-12508"><code>ABC-12508</code></a> \
                            Vestibulum pellentesque ullamcorper sapien sed venenatis.\
                            <a href="https://mockdata.atlassian.net/browse/ABC-12587"><code>ABC-12587</code></a> \
                            Integer et erat mollis, tempor sem a, fringilla est. \
                            </i>'

    def test_small_max_len_for_init(self):
        with self.assertRaises(msg_split.NotEnoughtFragmentLenForInitialization):
            gen = msg_split.split_message(self.html_string, 10)
            next(gen)

    def test_small_max_len_while_processing(self):
        results = []
        with self.assertRaises(msg_split.NotEnoughtFragmentLen):
            gen = msg_split.split_message(self.html_string, 100)
            for res in gen:
                results.append(res)

    def test_wrong_len_type(self):
        with self.assertRaises(TypeError):
            gen = msg_split.split_message(self.html_string, "100")
            next(gen)

    def test_empty_source_string(self):
        with self.assertRaises(msg_split.EmptySourceString):
            gen = msg_split.split_message("", 120)
            next(gen)

    # Проверка вручную почитанного html фрагмента
    def test_split_message_html_string(self):
        len_results = []
        len_results_test = [114, 121, 91, 117]
        gen = msg_split.split_message(self.html_string, 150)
        for res in gen:
            len_results.append(len(res))
        self.assertEqual(len_results, len_results_test)

    # Проверяем случай с 4396
    def test_split_message_html_test_source_4396_len(self):
        results: list[str] = []
        len_results = []
        len_results_test = [4377, 1370]
        first_fragment_end_test = "\n</div></span>"
        second_fragment_start_test = '<span><div><a href="https://mockdata.atlassian.net/browse/ABC-12398"><code>ABC-12398</code></a>'
        with open(self.html_path, "r") as source:
            gen = msg_split.split_message(source, 4396)
            for res in gen:
                results.append(res)
                len_results.append(len(res))
            self.assertEqual(len_results, len_results_test)
            self.assertTrue(results[0].endswith(first_fragment_end_test))
            self.assertTrue(results[1].startswith(second_fragment_start_test))

    # Проверяем случай при длине 4296 с переносот \n
    def test_split_message_html_test_source_4296_len(self):
        results: list[str] = []
        len_results = []
        len_results_test = [4255, 1492]
        first_fragment_end_test = "\n<div>\n</div></span>"
        second_fragment_start_test = '<span><div><a href="https://mockdata.atlassian.net/browse/ABC-12354"><code>ABC-12354</code></a>'
        with open(self.html_path, "r") as source:
            gen = msg_split.split_message(source, 4296)
            for res in gen:
                results.append(res)
                len_results.append(len(res))
            self.assertEqual(len_results, len_results_test)
            self.assertTrue(results[0].endswith(first_fragment_end_test))
            self.assertTrue(results[1].startswith(second_fragment_start_test))

    # Проверяем, что фрагмент, прочитанный от начала до конца, эквивалентен изначальному файлу
    def test_split_message_len_more_string(self):
        results: list[str] = []
        len_results = []
        len_results_test = []
        with open(self.html_path, "r", encoding="utf-8") as source:
            fragment_start_test = source.readline()
            ln = len(fragment_start_test)
            for line in source:
                fragment_end_test = line
                ln += len(line)
            len_results_test.append(ln)
        with open(self.html_path, "r", encoding="utf-8") as source:
            gen = msg_split.split_message(source, 8000)
            for res in gen:
                results.append(res)
                len_results.append(len(res))
            self.assertEqual(len_results, len_results_test)
            self.assertTrue(results[0].endswith(fragment_end_test))
            self.assertTrue(results[0].startswith(fragment_start_test))


if __name__ == "__main__":
    unittest.main()

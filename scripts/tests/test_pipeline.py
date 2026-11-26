import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_pipeline import infer_topic, normalize_question, parse_messages, stable_id


class PipelineTests(unittest.TestCase):
    def test_question_normalization_is_stable(self):
        self.assertEqual(normalize_question('  Explain  SQL?  '), 'Explain SQL?')
        self.assertEqual(stable_id('A', 'B'), stable_id('a', 'b'))

    def test_nested_messages_are_parsed(self):
        messages = parse_messages([{'role': 'assistant', 'content': 'Explain polymorphism'}])
        self.assertEqual(messages[0]['role'], 'assistant')

    def test_topic_mapping_is_explicitly_inferred(self):
        topic, metadata = infer_topic('Explain how database normalization works')
        self.assertEqual(topic, 'databases')
        self.assertTrue(metadata['inference'])


if __name__ == '__main__':
    unittest.main()

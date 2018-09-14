from unittest import TestCase


from checkQC.run_type_summarizer import RunTypeSummarizer


class TestRunTypeSummarizer(TestCase):

    def test_summarize(self):

        instrument_and_reagent_type = "my_fav_illumina_instrument"
        read_lengths = "42-42"
        handler_config = [{"name": "CoolestHandler", "error": 1, "warning": 2}]

        with self.assertLogs() as cm:
            result = RunTypeSummarizer.summarize(instrument_and_reagent_version=instrument_and_reagent_type,
                                                 read_lengths=read_lengths,
                                                 handler_config=handler_config)

            expected_log = ['INFO:checkQC.run_type_summarizer:Run summary',
                            'INFO:checkQC.run_type_summarizer:-----------',
                            'INFO:checkQC.run_type_summarizer:Instrument and reagent version: '
                            'my_fav_illumina_instrument',
                            'INFO:checkQC.run_type_summarizer:Read length: 42-42',
                            'INFO:checkQC.run_type_summarizer:Enabled handlers and their config values were: ',
                            'INFO:checkQC.run_type_summarizer:'
                            '\t{\'name\': \'CoolestHandler\', \'error\': 1, \'warning\': 2}']

            self.assertEqual(cm.output, expected_log)

            expected = {'instrument_and_reagent_type': instrument_and_reagent_type,
                        'read_length': read_lengths,
                        'handlers': [{'name': 'CoolestHandler', 'error': 1, 'warning': 2}]}
            self.assertEqual(result, expected)

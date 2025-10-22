import numpy as np
from checkQC.parsers.illumina import _read_interop_summary


def bclconvert_test_runfolder(qc_data, runfolder_path):
    _, _, run_info = _read_interop_summary(runfolder_path)
    flowcell_id = run_info.flowcell_id()
    if "HMTFYDRXX" in flowcell_id:
        return {
            "qc_data": qc_data,
            "expected_instrument": "novaseq_SP",
            "expected_read_length": 36,
            "expected_samplesheet": {
                "len": 4,
                "head": [
                    {
                        "lane": 1,
                        "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane1",
                        "index": "GAACTGAGCG",
                        "index2": "TCGTGGAGCG",
                        "sample_project": "AB-1234",
                        "overridecycles": "Y36;I10;I10",
                        "custom_description": "LIBRARY_NAME:test",
                    },
                    {
                        "lane": 1,
                        "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane1",
                        "index": "AGGTCAGATA",
                        "index2": "CTACAAGATA",
                        "sample_project": "CD-5678",
                        "overridecycles": "Y36;I10;I10",
                        "custom_description": "LIBRARY_NAME:test",
                    },
                    {
                        "lane": 2,
                        "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane2",
                        "index": "GAACTGAGCG",
                        "index2": "TCGTGGAGCG",
                        "sample_project": "AB-1234",
                        "overridecycles": "Y36;I10;I10",
                        "custom_description": "LIBRARY_NAME:test",
                    },
                    {
                        "lane": 2,
                        "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane2",
                        "index": "AGGTCAGATA",
                        "index2": "CTACAAGATA",
                        "sample_project": "CD-5678",
                        "overridecycles": "Y36;I10;I10",
                        "custom_description": "LIBRARY_NAME:test",
                    },
                ],
            },
            "expected_sequencing_metrics": {
                1: {
                    "total_reads_pf": 532_464_327,
                    "total_reads": 638_337_024,
                    "raw_density": 2_961_270.5,
                    "pf_density": 2_470_118.25,
                    "yield": 122_605_416,
                    "yield_undetermined": 121_940_136,
                    "top_unknown_barcodes": {
                        "len": 1029,
                        "head": [
                            {
                                'index': 'ATATCTGCTT', 'index2': 'TAGACAATCT',
                                'count': 12857,
                            },
                            {
                                'index': 'CACCTCTCTT', 'index2': 'CTCGACTCCT',
                                'count': 12406,
                            },
                            {
                                'index': 'ATGTAACGTT', 'index2': 'ACGATTGCTG',
                                'count': 12177,
                            },
                            {
                                'index': 'TTCGGTGTGA', 'index2': 'GAACAAGTAT',
                                'count': 11590,
                            },
                            {
                                'index': 'GGTCCGCTTC', 'index2': 'CTCACACAAG',
                                'count': 11509,
                            },
                        ],
                    },
                    "reads": {
                        1: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 95.70932006835938,
                            "is_index": False,
                            "mean_percent_phix_aligned": 0.,
                        },
                        2: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 92.57965850830078,
                            "is_index": True,
                            "mean_percent_phix_aligned": np.nan,
                        },
                        3: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 90.3790283203125,
                            "is_index": True,
                            "mean_percent_phix_aligned": np.nan,
                        },
                    },
                    "reads_per_sample": [
                        {
                            "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane1",
                            "cluster_count": 9920,
                            "percent_of_lane": 0.29,
                            "percent_perfect_index_reads": 97.96,
                            "mean_q30": 36.37,
                            "percent_q30": 96,
                        },
                        {
                            "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane1",
                            "cluster_count": 8560,
                            "percent_of_lane": 0.25,
                            "percent_perfect_index_reads": 98.15,
                            "mean_q30": 36.43,
                            "percent_q30": 96,
                        },
                    ],
                },
                2: {
                    "total_reads_pf": 530_917_565,
                    "total_reads": 638_337_024,
                    "raw_density": 2_961_270.5,
                    "pf_density": 2_462_942.5,
                    "yield": 124_497_108,
                    "yield_undetermined": 123_817_428,
                    "top_unknown_barcodes": {
                        "len": 1055,
                        "head": [
                            {
                                'index': 'ATATCTGCTT', 'index2': 'TAGACAATCT',
                                'count': 13176,
                            },
                            {
                                'index': 'ATGTAACGTT', 'index2': 'ACGATTGCTG',
                                'count': 12395,
                            },
                            {
                                'index': 'CACCTCTCTT', 'index2': 'CTCGACTCCT',
                                'count': 12247,
                            },
                            {
                                'index': 'TTCGGTGTGA', 'index2': 'GAACAAGTAT',
                                'count': 11909,
                            },
                            {
                                'index': 'TAATTAGCGT', 'index2': 'TGGTTAAGAA',
                                'count': 11330,
                            },
                        ],
                    },
                    "reads": {
                        1: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 95.75276184082031,
                            "is_index": False,
                            "mean_percent_phix_aligned": 0.,
                        },
                        2: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 92.60448455810547,
                            "is_index": True,
                            "mean_percent_phix_aligned": np.nan,
                        },
                        3: {
                            "mean_error_rate": np.nan,
                            "percent_q30": 90.2811050415039,
                            "is_index": True,
                            "mean_percent_phix_aligned": np.nan,
                        },
                    },
                    "reads_per_sample": [
                        {
                            "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane2",
                            "cluster_count": 10208,
                            "percent_of_lane": 0.3,
                            "percent_perfect_index_reads": 98.2,
                            "mean_q30": 36.4,
                            "percent_q30": 96,
                        },
                        {
                            "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane2",
                            "cluster_count": 8672,
                            "percent_of_lane": 0.25,
                            "percent_perfect_index_reads": 98.29,
                            "mean_q30": 36.48,
                            "percent_q30": 97,
                        },
                    ],
                },
            },
        }
    else:
        raise Exception("Excpected flowcell_id value as 'HMTFYDRXX' only for "
                        f"this fuction but got {flowcell_id}"
        )


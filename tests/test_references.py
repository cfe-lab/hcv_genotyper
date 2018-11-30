import pathlib
import unittest

import Bio.SeqIO

import hcv_genotyper.genotyper as gtr

REFSEQS_PATH = (
    pathlib.Path(__file__).parent.parent / "hcv_genotyper/hcv-refs.fasta"
)
with REFSEQS_PATH.open() as inf:
    REFERENCE_SEQS = list(Bio.SeqIO.parse(inf, "fasta"))


class TestGenotypingRefernences(unittest.TestCase):
    "Verify that the references can be correctly genotyped"

    def test_reference_seqs_are_correctly_genotyped(self):
        for seq in REFERENCE_SEQS:
            gt_src = seq.description.split()[1]
            gt = gtr.Genotype.parse(gt_src)
            self.assertIsNotNone(
                gt, "Invalid genotype '{}' in {}".format(gt_src, seq)
            )
            seq_str = str(seq.seq)
            genotype = gtr.classify(seq_str)
            self.assertIsNotNone(genotype, "Failed to genotype {}".format(seq))
            self.assertEqual(
                genotype, gt, "Mismatched genotypes for {}".format(seq)
            )

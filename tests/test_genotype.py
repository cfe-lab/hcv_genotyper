import itertools
import string
import typing as ty
import unittest

from hcv_genotyper.genotyper import Genotype


class TestGenotype(unittest.TestCase):
    @staticmethod
    def all_valid_cases() -> ty.Iterable[ty.Tuple[str, Genotype]]:
        genotypes = [1, 2, 3, 4, 5, 6]
        subgenotypes: ty.List[ty.Optional[str]] = [None]
        subgenotypes.extend(string.ascii_lowercase)
        for gt, subgt in itertools.product(genotypes, subgenotypes):
            as_str = "{}{}".format(gt, subgt if subgt else "")
            as_gt = Genotype(gt, subgt)
            yield (as_str, as_gt)

    def test_parsing_valid(self):
        for src, expected in self.all_valid_cases():
            msg = "Expected '{}' to parse to '{}'".format(src, expected)
            self.assertEqual(Genotype.parse(src), expected, msg)

    def test_parsing_invalid(self):
        invalid_cases = ("a", " 1a", "Samson", "7b")
        for src in invalid_cases:
            with self.assertRaises(ValueError):
                Genotype.parse(src)

    def test_formatting(self):
        cases = [((1, "a"), "1a"), ((1, None), "1"), ((2, "b"), "2b")]
        for inpt, expected in cases:
            gt = Genotype(*inpt)
            msg = "Expected str(Genotype{}) to be '{}'".format(inpt, expected)
            self.assertEqual(str(gt), expected, msg)

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

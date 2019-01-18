import functools
import logging
import pathlib
import re
import sys
import tempfile
import typing as ty

from . import cache

from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from Bio.Blast import Record

log = logging.getLogger(__file__)


# ---------------------------------------------------------------------
# Load references

REFERENCE_SEQUENCE_PATH = pathlib.Path(__file__).parent / "hcv-refs.fasta"
if not REFERENCE_SEQUENCE_PATH.exists() and REFERENCE_SEQUENCE_PATH.is_file():

    sys.exit(1)

BLAST_PARAMS = {
    "outfmt": 5,
    "evalue": 0.0001,
    "gapopen": 5,
    "gapextend": 2,
    "penalty": -3,
    "reward": 1,
    "max_target_seqs": 1,
    "subject": str(REFERENCE_SEQUENCE_PATH),
}


# ---------------------------------------------------------------------


class Genotype(ty.NamedTuple):
    "An HCV genotype, with an optional subgenotype"
    gt: int
    sub_gt: ty.Optional[str]

    @classmethod
    def parse(cls, src: str) -> "Genotype":
        gt_re = re.compile(r"^([123456])([a-z]?)")
        match = gt_re.match(src)
        if match is None:
            msg = f"Error parsing genotype '{src}'"
            raise ValueError(msg)
        gt_src, subgt_src = match.groups()
        return Genotype(gt=int(gt_src), sub_gt=subgt_src or None)

    def __str__(self) -> str:
        sub_gt = self.sub_gt if self.sub_gt else ""
        return "{}{}".format(self.gt, sub_gt)


class MatchScore(ty.NamedTuple):
    gt: Genotype
    score: int


# ---------------------------------------------------------------------


def do_blast_search(seqfilename: str, resultfilename: str):
    """Perform a BLAST search

    The sequences in the input file (called `seqfilename`) will BLAST searched
    against this library's HCV reference sequences. The output is stored in a
    file called `resultfilename`.
    """
    cmd = NcbiblastnCommandline(
        query=seqfilename, out=resultfilename, **BLAST_PARAMS
    )
    cmd()


def blast_search_descriptions(seq: str) -> ty.List[Record.Description]:
    """Perform a blast search on nucleotide sequence `seq`.

    Uses temporary files to send the input sequence to `blast` and get the
    results.
    """
    with tempfile.NamedTemporaryFile(buffering=0) as seqfile:
        seqfile.write("> Sequence\n{}".format(seq).encode("utf8"))
        seqfile.seek(0)  # reset file handle
        with tempfile.NamedTemporaryFile(buffering=0) as xmloutput:
            do_blast_search(seqfile.name, xmloutput.name)
            xmloutput.seek(0)
            blast_record = NCBIXML.read(xmloutput)
            descriptions = blast_record.descriptions
            return descriptions


def best_match(
    blast_descs: ty.List[Record.Description]
) -> ty.Optional[Genotype]:
    def parse_desc(desc: Record.Description) -> MatchScore:
        score = desc.score
        title = desc.title
        gt_str = title.split(" ")[-1]
        gt = Genotype.parse(gt_str)
        return MatchScore(gt, score)

    desc_scores = sorted(
        [parse_desc(desc) for desc in blast_descs],
        key=lambda ms: ms.score,
        reverse=True,  # We want the highest score first.
    )
    best_score = next(iter(desc_scores), None)
    if best_score is None:
        return None
    else:
        return best_score.gt


T = ty.TypeVar("T")


def tidy_seq_input(fn: ty.Callable[[str], T]) -> ty.Callable[[str], T]:
    @functools.wraps(fn)
    def wrapped(seq: str):
        tidied_seq = seq.replace(" ", "").replace("-", "").replace("~", "")
        return fn(tidied_seq)

    return wrapped


@tidy_seq_input
@cache.persistent_cache(".genotypes.shelve")
def classify(seq: str) -> ty.Optional[Genotype]:
    blast_descriptions = blast_search_descriptions(seq)
    return best_match(blast_descriptions)


def classify_seqs(seqs: ty.Iterable[str]) -> ty.Optional[Genotype]:
    gts = set(classify(seq) for seq in seqs)
    if len(gts) == 1:
        return gts.pop()
    else:
        return None

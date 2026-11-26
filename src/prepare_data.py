"""
Builds the matched-pair dataset from the raw replication package.
"""

# --- IMPORTS ---
from pathlib import Path

import json
import pandas as pd


# --- GLOBALS ---
# input and output files, resolved from the repository root
REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_FILE = REPO_ROOT / 'data' / 'raw' / 'activity_profiles.json'
PAIRS_FILE = REPO_ROOT / 'data' / 'processed' / 'pairs.csv'

# position of the activity duration (months) inside raw_dims
DURATION_INDEX = 4

# an organic contributor's id is its event pair's id plus this suffix
ORGANIC_SUFFIX = '__organic'

# whether each event comes with a mentor
MENTORSHIP_BY_EVENT = {
    'gsoc': True,
    'lfx': True,
    'hacktoberfest': False,
    '24pr': False,
}

# sizes the dataset must have, as reported by the replication package
EXPECTED_PAIRS = 2001
EXPECTED_REPOS = 330
EXPECTED_PAIRS_BY_EVENT = {
    'gsoc': 739,
    '24pr': 576,
    'hacktoberfest': 516,
    'lfx': 170,
}

# columns of pairs.csv, in order
PAIR_COLUMNS = [
    'pair_id',
    'repo',
    'event_type',
    'mentorship',
    'duration_event',
    'duration_organic',
    'D',
    'self_matched',
]


# --- CODE ---
def load_profiles(path: Path) -> pd.DataFrame:
    """
    Load one row per contributor with the fields the pairing needs.

    :param path: Path to activity_profiles.json.

    :return: The contributor profiles.
    """
    # read the raw profiles
    with path.open(encoding='utf-8') as file:
        records = json.load(file)

    # keep only the fields used, pulling the duration out of raw_dims
    return pd.DataFrame(
        [
            {
                'contributor_id': record['contributor_id'],
                'contributor_type': record['contributor_type'],
                'event_type': record['event_type'],
                'repo': record['repo'],
                'username': record['username'],
                'duration': record['raw_dims'][DURATION_INDEX],
            }
            for record in records
        ]
    )


def build_pairs(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Join each event contributor to its organic match, one row per pair.

    :param profiles: The contributor profiles.

    :return: The pairs, sorted by pair_id.
    """
    # the pair id is the event contributor's id
    profiles = profiles.assign(
        pair_id=profiles['contributor_id'].str.removesuffix(ORGANIC_SUFFIX)
    )
    events = profiles[profiles['contributor_type'] == 'event']
    organics = profiles[profiles['contributor_type'] == 'organic']

    # join both members; an unmatched member is kept, with a missing duration
    columns = ['pair_id', 'repo', 'username', 'duration']
    pairs = events[[*columns, 'event_type']].merge(
        organics[columns],
        on='pair_id',
        how='outer',
        suffixes=('_event', '_organic'),
    )

    # derive the mentorship flag and the paired difference
    pairs['mentorship'] = pairs['event_type'].map(MENTORSHIP_BY_EVENT)
    pairs['D'] = pairs['duration_event'] - pairs['duration_organic']

    # both members are the same github account (protocol amendment 1)
    usernames = pairs[['username_event', 'username_organic']]
    usernames = usernames.apply(lambda column: column.str.lower())
    pairs['self_matched'] = (
        usernames['username_event'] == usernames['username_organic']
    )
    pairs = pairs.rename(columns={'repo_event': 'repo'})

    return pairs.sort_values('pair_id').reset_index(drop=True)


def validate_pairs(pairs: pd.DataFrame, profiles: pd.DataFrame) -> None:
    """
    Check the pairs against the design and print the result of each check.

    :param pairs: The pairs built by build_pairs.
    :param profiles: The contributor profiles the pairs came from.

    :raises AssertionError: Listing every check that failed.

    :return: None.
    """
    durations = pairs[['duration_event', 'duration_organic']]
    integer = all(pd.api.types.is_integer_dtype(d) for d in durations.dtypes)
    counts = pairs['event_type'].value_counts().to_dict()
    repos = pairs['repo'].nunique()

    # each check, mapped to whether it passed
    checks = {
        f'{EXPECTED_PAIRS} pairs (found {len(pairs)})': (
            len(pairs) == EXPECTED_PAIRS
        ),
        'every contributor is in a pair': len(profiles) == 2 * len(pairs),
        'no duplicated pair ids': not pairs['pair_id'].duplicated().any(),
        'no missing durations': not durations.isna().any(axis=None),
        'durations are whole months >= 1': (
            integer and (durations >= 1).all(axis=None)
        ),
        f'{EXPECTED_REPOS} repos (found {repos})': repos == EXPECTED_REPOS,
        'both members of each pair in the same repo': (
            pairs['repo'] == pairs['repo_organic']
        ).all(),
        'mentorship known for every event': pairs['mentorship'].notna().all(),
        f'pairs per event: {counts}': counts == EXPECTED_PAIRS_BY_EVENT,
    }

    # print every check, then fail listing the ones that did not pass
    status = {True: 'ok', False: 'FAIL'}
    for check, passed in checks.items():
        print(f'  [{status[bool(passed)]}] {check}')

    failed = [check for check, passed in checks.items() if not passed]
    assert not failed, f'Failed checks: {failed}'


def main() -> None:
    """
    Build, validate and save the pairs.

    :return: None.
    """
    # load the raw profiles
    profiles = load_profiles(PROFILES_FILE)
    print(
        f'Loaded {len(profiles)} contributor profiles from '
        f'{PROFILES_FILE.relative_to(REPO_ROOT)}'
    )

    # pair and validate
    pairs = build_pairs(profiles)
    validate_pairs(pairs, profiles)
    print('All validations passed.')

    # self-matched pairs are left out of the primary analysis
    self_matched = int(pairs['self_matched'].sum())
    print(
        f'Self-matched pairs: {self_matched} '
        f'(primary analysis keeps {len(pairs) - self_matched})'
    )

    # save with fixed line endings, so the output is byte-identical everywhere
    PAIRS_FILE.parent.mkdir(parents=True, exist_ok=True)
    pairs[PAIR_COLUMNS].to_csv(PAIRS_FILE, index=False, lineterminator='\n')
    print(f'Wrote {PAIRS_FILE.relative_to(REPO_ROOT)}')


if __name__ == '__main__':
    main()

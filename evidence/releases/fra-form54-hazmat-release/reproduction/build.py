'''Build the FRA Form 54 hazmat-release dataset with explicit grade-crossing exclusion.'''

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

import pandas as pd

from source_io import fetch

DATASET_ID = 'byy5-w977'
METADATA_URL = 'https://data.transportation.gov/api/views/' + DATASET_ID + '.json'
RESOURCE_CSV_URL = 'https://data.transportation.gov/resource/' + DATASET_ID + '.csv'
EXPORT_CSV_URL = 'https://data.transportation.gov/api/views/' + DATASET_ID + '/rows.csv?accessType=DOWNLOAD'

FEATURES = [
    'trainspeed',
    'equipmenttype',
    'hazmatcars',
    'loadedfreightcars',
    'emptyfreightcars',
    'grosstonnage',
    'tracktype',
    'trackclass',
    'weathercondition',
    'visibility',
    'temperature',
    'accidenttype',
    'reporting_railroad_class',
    'stateabbr',
]

NUMERIC_FEATURES = {
    'trainspeed',
    'hazmatcars',
    'loadedfreightcars',
    'emptyfreightcars',
    'grosstonnage',
    'temperature',
}

TARGET = 'hazmat_release'
ID_COLUMN = 'accident_id'
TIME_COLUMN = 'accident_date'

TRAIN_END = pd.Timestamp('2000-01-01')
EVAL_END = pd.Timestamp('2013-01-01')
MIN_YEAR = 1975
MAX_YEAR = 2026
ROW_LIMIT = 50000
MIN_SHIPPED = 15000
MAX_SHIPPED = 45000

CROSSING_TYPES = {
    'hwyrailcrossing',
    'highwayrailcrossing',
    'rrgradecrossing',
    'railroadgradecrossing',
}

ALIASES = {
    'trainspeed': ['trainspeed', 'speed'],
    'equipmenttype': ['equipmenttype', 'equipment'],
    'hazmatcars': ['hazmatcars', 'hazmatcarsincident'],
    'loadedfreightcars': ['loadedfreightcars', 'loadedcars'],
    'emptyfreightcars': ['emptyfreightcars', 'emptycars'],
    'grosstonnage': ['grosstonnage', 'grosstons', 'totalgrosstonnage'],
    'tracktype': ['tracktype', 'track'],
    'trackclass': ['trackclass', 'fratrackclass'],
    'weathercondition': ['weathercondition', 'weather'],
    'visibility': ['visibility', 'visibilitycondition'],
    'temperature': ['temperature', 'temperaturef'],
    'accidenttype': ['accidenttype', 'typeofaccident'],
    'reporting_railroad_class': [
        'reportingrailroadclass',
        'railroadclass',
        'carrierclass',
        'classofrailroad',
    ],
    'stateabbr': ['stateabbr', 'statecode', 'state'],
    'hazmatreleasedcars': ['hazmatreleasedcars', 'releasedhazmatcars'],
    'gxid': ['gxid', 'gradecrossingid', 'crossingid'],
    'year': ['year', 'accidentyear'],
    'month': ['accidentmonth', 'month'],
    'day': ['accidentday', 'day'],
    'reportingrailroadcode': ['reportingrailroadcode', 'reportingrailroad', 'railroadcode'],
}

ID_CANDIDATES = [
    'reportid',
    'reportnumber',
    'incidentnumber',
    'accidentnumber',
    'recordid',
    'objectid',
    'uniqueid',
    'accidentid',
]

DATE_CANDIDATES = ['accidentdate', 'incidentdate', 'date', 'reportdate']

COMPOSITE_FIELDS = [
    'reportingrailroadcode',
    'year',
    'month',
    'day',
    'stateabbr',
    'station',
    'milepost',
    'accidenttype',
]

POST_OUTCOME_COLUMNS = [
    'hazmatcarsdamaged',
    'hazmatreleasedcars',
    'personsevacuated',
    'totaldamagecost',
]


def _norm(value):
    return re.sub('[^a-z0-9]', '', str(value).lower())


def _text(series):
    return series.astype('string').fillna('').astype(str).str.strip()


def _code(series):
    return _text(series).str.lower().str.replace('[^a-z0-9]', '', regex=True)


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _fetch_retry(url, cache, name, attempts=3):
    errors = []
    for attempt in range(attempts):
        attempt_name = name if attempt == 0 else name + '.attempt' + str(attempt + 1)
        try:
            path = Path(fetch(url, cache, attempt_name))
            if path.is_file() and path.stat().st_size > 0:
                return path
            errors.append('attempt ' + str(attempt + 1) + ' returned an empty or missing file')
        except Exception as exc:
            errors.append(
                'attempt '
                + str(attempt + 1)
                + ' raised '
                + type(exc).__name__
                + ': '
                + str(exc)[:300]
            )
    raise AssertionError(
        ('fetch failed for ' + url + ' after ' + str(attempts) + ' attempts: ' + '; '.join(errors))[:4000]
    )


def _read_metadata_fields(path):
    try:
        text = Path(path).read_text(encoding='utf-8', errors='replace')
        doc = json.loads(text)
    except Exception:
        return []
    names = []
    columns = doc.get('columns')
    if isinstance(columns, list):
        for column in columns:
            if isinstance(column, dict):
                name = column.get('fieldName') or column.get('name')
                if name:
                    names.append(str(name))
    return names


def _resolve(lookup, name):
    for candidate in [name] + ALIASES.get(name, []):
        column = lookup.get(_norm(candidate))
        if column is not None:
            return column
    return None


def _resolve_features(lookup):
    resolved = {}
    missing = []
    for name in FEATURES:
        column = _resolve(lookup, name)
        if column is None:
            missing.append(name)
        else:
            resolved[name] = column
    return resolved, missing


def _soql_url(fields, hazmat_field):
    select = ','.join(fields)
    quote_char = chr(39)
    where = hazmat_field + ' != ' + quote_char + '0' + quote_char
    return (
        RESOURCE_CSV_URL
        + '?$select='
        + quote(select, safe='')
        + '&$where='
        + quote(where, safe='')
        + '&$limit='
        + str(ROW_LIMIT)
    )


def _window_text(frame):
    if frame.empty:
        return 'no rows'
    values = pd.to_datetime(frame[TIME_COLUMN])
    return values.min().strftime('%Y-%m-%d') + ' through ' + values.max().strftime('%Y-%m-%d')


def build(output: Path, cache: Path):
    output = Path(output)
    cache = Path(cache)
    for sub in ('public', 'private'):
        (output / sub).mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    checks = []

    meta_path = _fetch_retry(METADATA_URL, cache, 'fra_form54_subset_metadata.json', attempts=3)
    meta_fields = _read_metadata_fields(meta_path)
    meta_lookup = {_norm(column): column for column in meta_fields}
    meta_resolved, meta_missing = _resolve_features(meta_lookup)
    hazmat_field = meta_resolved.get('hazmatcars')
    release_field = _resolve(meta_lookup, 'hazmatreleasedcars')
    gxid_field = _resolve(meta_lookup, 'gxid')
    year_field = _resolve(meta_lookup, 'year')
    month_field = _resolve(meta_lookup, 'month')
    day_field = _resolve(meta_lookup, 'day')

    csv_path = None
    filter_note = 'full published extract; grade-crossing records are excluded locally after the hazmat and year filters'
    if (
        hazmat_field is not None
        and release_field is not None
        and gxid_field is not None
        and year_field is not None
        and not meta_missing
    ):
        wanted = set(meta_resolved.values())
        wanted.add(hazmat_field)
        wanted.add(release_field)
        wanted.add(gxid_field)
        wanted.add(year_field)
        if month_field is not None:
            wanted.add(month_field)
        if day_field is not None:
            wanted.add(day_field)
        for candidate in DATE_CANDIDATES + ID_CANDIDATES + COMPOSITE_FIELDS:
            column = _resolve(meta_lookup, candidate)
            if column is not None:
                wanted.add(column)
        query_url = _soql_url(sorted(wanted), hazmat_field)
        try:
            csv_path = _fetch_retry(query_url, cache, 'fra_form54_hazmat_filtered.csv', attempts=3)
            filter_note = (
                'projected subset export served by the publisher query engine with a hazmat car count filter; '
                'grade-crossing records are excluded locally'
            )
        except Exception:
            csv_path = None
    if csv_path is None:
        csv_path = _fetch_retry(EXPORT_CSV_URL, cache, 'fra_form54_hazmat_full.csv', attempts=2)

    header = pd.read_csv(csv_path, nrows=0)
    source_headers = [str(column) for column in header.columns]
    lookup = {_norm(column): column for column in source_headers}
    resolved, missing = _resolve_features(lookup)
    label_column = _resolve(lookup, 'hazmatreleasedcars')
    year_column = _resolve(lookup, 'year')
    month_column = _resolve(lookup, 'month')
    day_column = _resolve(lookup, 'day')
    gxid_column = _resolve(lookup, 'gxid')
    accidenttype_column = resolved.get('accidenttype')
    if label_column is None:
        missing.append('hazmatreleasedcars')
    if year_column is None:
        missing.append('year')
    if gxid_column is None:
        missing.append('gxid used to exclude grade-crossing records')
    if accidenttype_column is None:
        missing.append('accidenttype used to exclude grade-crossing records')
    if missing:
        message = (
            'Form 54 field resolution failed for the declared task fields. selected source member: '
            + csv_path.name
            + ' ('
            + filter_note
            + '). missing declared fields: '
            + repr(sorted(set(missing)))
            + '. observed headers ('
            + str(len(source_headers))
            + '): '
            + repr(source_headers)
        )
        raise AssertionError(message[:4000])

    read_columns = set(resolved.values())
    read_columns.add(label_column)
    read_columns.add(year_column)
    read_columns.add(gxid_column)
    if month_column is not None:
        read_columns.add(month_column)
    if day_column is not None:
        read_columns.add(day_column)

    date_column = next(
        (lookup[_norm(candidate)] for candidate in DATE_CANDIDATES if _norm(candidate) in lookup),
        None,
    )
    if date_column is not None:
        read_columns.add(date_column)
    id_column = next(
        (lookup[_norm(candidate)] for candidate in ID_CANDIDATES if _norm(candidate) in lookup),
        None,
    )
    if id_column is not None:
        read_columns.add(id_column)

    composite_columns = []
    for candidate in COMPOSITE_FIELDS:
        column = _resolve(lookup, candidate)
        if column is not None and column not in composite_columns:
            composite_columns.append(column)
    read_columns.update(composite_columns)

    header_set = set(source_headers)
    available = [column for column in sorted(read_columns) if column in header_set]

    frames = []
    rows_scanned = 0
    rows_zero_hazmat = 0
    rows_missing_hazmat = 0
    rows_outside_years = 0
    crossing_rows = 0
    crossing_gxid_rows = 0
    crossing_type_rows = 0
    crossing_positive = 0
    crossing_gxid_positive = 0
    crossing_type_positive = 0
    hazmat_column = resolved['hazmatcars']

    for chunk in pd.read_csv(csv_path, usecols=available, dtype=str, chunksize=200000):
        rows_scanned += int(len(chunk))
        counts = pd.to_numeric(chunk[hazmat_column], errors='coerce')
        rows_missing_hazmat += int(counts.isna().sum())
        rows_zero_hazmat += int((counts == 0).sum())
        kept = chunk.loc[counts >= 1].copy()
        if kept.empty:
            continue
        years = pd.to_numeric(kept[year_column], errors='coerce')
        inside = years.between(MIN_YEAR, MAX_YEAR)
        rows_outside_years += int((~inside).sum())
        kept = kept.loc[inside]
        if kept.empty:
            continue

        gxid_values = _text(kept[gxid_column])
        gxid_crossing = gxid_values.ne('') & gxid_values.str.lower().ne('nan')
        type_codes = _code(kept[accidenttype_column])
        type_crossing = type_codes.isin(CROSSING_TYPES)
        crossing_mask = gxid_crossing | type_crossing
        released = pd.to_numeric(kept[label_column], errors='coerce')

        crossing_rows += int(crossing_mask.sum())
        crossing_gxid_rows += int(gxid_crossing.sum())
        crossing_type_rows += int(type_crossing.sum())
        crossing_positive += int((crossing_mask & (released >= 1)).sum())
        crossing_gxid_positive += int((gxid_crossing & (released >= 1)).sum())
        crossing_type_positive += int((type_crossing & (released >= 1)).sum())

        kept = kept.loc[~crossing_mask]
        if not kept.empty:
            frames.append(kept)

    if not frames:
        raise AssertionError(
            'Form 54 population is empty after the hazmat, year and grade-crossing filters'
        )

    df = pd.concat(frames, ignore_index=True)
    df['_released_cars'] = pd.to_numeric(df[label_column], errors='coerce')
    dropped_unknown = int(df['_released_cars'].isna().sum())
    df = df.loc[df['_released_cars'].notna()].reset_index(drop=True)
    if df.empty:
        raise AssertionError(
            'Form 54 population is empty after dropping accidents with an unknown release count'
        )
    df[TARGET] = (df['_released_cars'] >= 1).astype('int64')

    years = pd.to_numeric(df[year_column], errors='coerce')
    if month_column is not None and day_column is not None:
        months = pd.to_numeric(df[month_column], errors='coerce')
        days = pd.to_numeric(df[day_column], errors='coerce')
    else:
        months = pd.Series([float('nan')] * len(df), index=df.index)
        days = pd.Series([float('nan')] * len(df), index=df.index)

    valid_ymd = years.notna() & months.between(1, 12) & days.between(1, 31)
    composed = pd.to_datetime(
        years.fillna(0).astype(int).astype(str).str.zfill(4)
        + '-'
        + months.fillna(0).astype(int).astype(str).str.zfill(2)
        + '-'
        + days.fillna(0).astype(int).astype(str).str.zfill(2),
        format='%Y-%m-%d',
        errors='coerce',
    ).where(valid_ymd)

    event_dt = composed
    if date_column is not None:
        parsed = pd.to_datetime(df[date_column], errors='coerce')
        event_dt = event_dt.fillna(parsed)

    jan_first = pd.to_datetime(
        years.fillna(0).astype(int).astype(str).str.zfill(4) + '-01-01',
        format='%Y-%m-%d',
        errors='coerce',
    )
    usable = (event_dt.notna() | jan_first.notna()).to_numpy()
    dropped_no_date = int((~usable).sum())
    df = df.loc[usable].reset_index(drop=True)
    event_dt = event_dt.loc[usable].reset_index(drop=True)
    jan_first = jan_first.loc[usable].reset_index(drop=True)
    day_precision = int(event_dt.notna().sum())
    event_dt = event_dt.fillna(jan_first)
    unresolved_dates = int(event_dt.isna().sum())
    if df.empty:
        raise AssertionError(
            'Form 54 population is empty after removing rows without any usable accident date'
        )

    gxid_shipped = int(_text(df[gxid_column]).ne('').sum())
    type_shipped = int(_code(df[accidenttype_column]).isin(CROSSING_TYPES).sum())

    ids = None
    id_origin = 'composite key'
    if id_column is not None:
        candidate = _text(df[id_column])
        if candidate.ne('').all() and candidate.is_unique:
            ids = candidate.astype(str)
            id_origin = id_column
    if ids is None:
        parts = []
        for column in composite_columns:
            parts.append(_text(df[column]))
        if not parts:
            parts = [_text(df[year_column])]
        key = parts[0]
        for part in parts[1:]:
            key = key + '|' + part
        ids = key.map(lambda value: 'F54' + hashlib.sha1(value.encode('utf-8')).hexdigest()[:16])
        if ids.duplicated().any():
            duplicated = ids.duplicated(keep=False)
            sequence = ids.groupby(ids).cumcount().astype(str)
            ids = ids.where(~duplicated, ids + '-' + sequence)
        id_origin = 'composite key over ' + ', '.join(composite_columns)

    frame = pd.DataFrame(index=df.index)
    frame[ID_COLUMN] = [str(value) for value in ids]
    frame['_event_dt'] = event_dt.to_numpy()
    for name in FEATURES:
        column = resolved[name]
        if name in NUMERIC_FEATURES:
            frame[name] = pd.to_numeric(df[column], errors='coerce').to_numpy()
        else:
            values = _text(df[column]).replace('', pd.NA)
            frame[name] = values.to_numpy()
    frame[TARGET] = df[TARGET].to_numpy()

    frame = frame.sort_values(['_event_dt', ID_COLUMN], kind='mergesort').reset_index(drop=True)
    dt = frame['_event_dt']
    frame[TIME_COLUMN] = dt.dt.strftime('%Y-%m-%dT00:00:00.000')

    train_mask = (dt < TRAIN_END).to_numpy()
    eval_mask = ((dt >= TRAIN_END) & (dt < EVAL_END)).to_numpy()
    holdout_mask = (dt >= EVAL_END).to_numpy()

    columns = [ID_COLUMN, TIME_COLUMN] + FEATURES + [TARGET]
    frame = frame[columns]

    train = frame.loc[train_mask]
    eval_frame = frame.loc[eval_mask]
    holdout = frame.loc[holdout_mask]

    train.to_csv(output / 'public' / 'train.csv', index=False)
    eval_frame.to_csv(output / 'public' / 'eval.csv', index=False)
    holdout.to_csv(output / 'private' / 'holdout.csv', index=False)

    n_total = int(len(frame))
    positives = int(frame[TARGET].sum())
    base_rate = (positives / n_total) if n_total else 0.0

    digest = _sha256_file(csv_path)
    checks.append(
        {
            'check': 'publisher Form 54 extract obtained through fetch and hashed',
            'observed': 'source member '
            + csv_path.name
            + ' with '
            + str(csv_path.stat().st_size)
            + ' bytes and sha256 '
            + digest[:16]
            + '; '
            + filter_note,
            'expected': 'the published Form 54 unique-train-accident extract from data.transportation.gov, downloaded through the platform fetch helper',
            'passed': bool(csv_path.is_file() and csv_path.stat().st_size > 0),
        }
    )

    checks.append(
        {
            'check': 'declared task fields resolve to publisher columns in the selected extract',
            'observed': 'resolved '
            + str(len(resolved))
            + ' of '
            + str(len(FEATURES))
            + ' declared features; release count label source column '
            + label_column
            + '; accident year column '
            + year_column
            + '; grade-crossing identifier column '
            + gxid_column,
            'expected': 'every declared feature, the release count label source, the accident year and the grade-crossing identifier present in the published columns',
            'passed': bool(
                len(resolved) == len(FEATURES)
                and label_column is not None
                and year_column is not None
                and gxid_column is not None
                and accidenttype_column is not None
            ),
        }
    )

    checks.append(
        {
            'check': 'published title claim of no grade crossings does not hold in the source block and crossing records are excluded',
            'observed': str(crossing_rows)
            + ' hazmat accidents with a non-empty gxid or a crossing accident type were excluded; '
            + str(crossing_gxid_rows)
            + ' carried a non-empty gxid and '
            + str(crossing_positive)
            + ' of those excluded rows were positive before exclusion; '
            + str(crossing_gxid_positive)
            + ' gxid positives and '
            + str(crossing_type_positive)
            + ' crossing-type positives overlap; shipped rows still carrying gxid '
            + str(gxid_shipped)
            + ' and shipped rows still typed crossing '
            + str(type_shipped),
            'expected': 'the source snapshot contains a crossing block even though the view title says not at grade crossings; no shipped row may carry a non-empty gxid or the accident types Hwy-rail crossing or RR grade crossing',
            'passed': bool(gxid_shipped == 0 and type_shipped == 0),
        }
    )

    hazmat_shipped = frame['hazmatcars'].dropna()
    population_ok = bool(
        n_total > 0
        and len(hazmat_shipped) == n_total
        and (hazmat_shipped >= 1).all()
        and MIN_SHIPPED <= n_total <= MAX_SHIPPED
        and n_total < ROW_LIMIT
        and gxid_shipped == 0
        and type_shipped == 0
    )
    checks.append(
        {
            'check': 'population holds only non-crossing accidents with at least one hazmat car inside the agreed accident years',
            'observed': str(rows_scanned)
            + ' source rows scanned; '
            + str(rows_zero_hazmat)
            + ' with a zero hazmat car count; '
            + str(rows_missing_hazmat)
            + ' without a parseable hazmat car count; '
            + str(rows_outside_years)
            + ' hazmat accidents outside the year range; '
            + str(crossing_rows)
            + ' crossing records excluded; '
            + str(dropped_unknown)
            + ' dropped for an unknown release count; '
            + str(dropped_no_date)
            + ' dropped without a usable date; '
            + str(n_total)
            + ' shipped',
            'expected': 'publisher SoQL reports 27,244 hazmat-car accidents before crossing exclusion, and the live source block carries 1,797 gxid rows and 1,756 Hwy-rail crossing rows; this build removes both kinds before labeling, so every shipped row has at least one hazmat car, an accident year from 1975 through 2026, an empty gxid and a non-crossing accident type',
            'passed': population_ok,
        }
    )

    checks.append(
        {
            'check': 'release target derived only from the recorded hazmat release count after crossing exclusion',
            'observed': str(positives)
            + ' positives and '
            + str(n_total - positives)
            + ' negatives across '
            + str(n_total)
            + ' rows; base rate '
            + format(base_rate, '.4f'),
            'expected': 'publisher SoQL reports 1,935 releases among 27,244 hazmat-car accidents before crossing exclusion; after removing the measured crossing block fewer positives remain, so the rate stays near 0.07 and is not treated as the pre-exclusion count',
            'passed': bool(0 < positives < n_total and 0.02 <= base_rate <= 0.25),
        }
    )

    checks.append(
        {
            'check': 'shipped accident identifiers are unique and stable within the snapshot',
            'observed': 'identifier source '
            + id_origin
            + '; '
            + str(n_total)
            + ' shipped rows and '
            + str(int(frame[ID_COLUMN].nunique()))
            + ' distinct identifiers',
            'expected': 'exactly one shipped row per accident identifier',
            'passed': bool(frame[ID_COLUMN].is_unique),
        }
    )

    observed_labels = sorted(int(value) for value in pd.unique(frame[TARGET]))
    checks.append(
        {
            'check': 'target column is binary with both classes present',
            'observed': 'distinct target values ' + repr(observed_labels),
            'expected': 'only 0 and 1, with at least one of each',
            'passed': bool(observed_labels == [0, 1]),
        }
    )

    checks.append(
        {
            'check': 'shipped columns are exactly the declared identifier, time, feature and target names',
            'observed': 'shipped columns ' + repr(list(frame.columns)),
            'expected': repr(columns),
            'passed': bool(list(frame.columns) == columns),
        }
    )

    checks.append(
        {
            'check': 'no post-outcome or label-source field is shipped as an input',
            'observed': 'overlap between shipped columns and excluded outcome fields is '
            + repr(sorted(set(columns).intersection(POST_OUTCOME_COLUMNS))),
            'expected': 'the excluded outcome fields stay out of the modelling frame',
            'passed': bool(set(columns).isdisjoint(POST_OUTCOME_COLUMNS)),
        }
    )

    class_values = frame['reporting_railroad_class'].dropna()
    class_nonnull = int(len(class_values))
    class_nunique = int(class_values.nunique())
    checks.append(
        {
            'check': 'published Reporting Railroad Class field is present and covered',
            'observed': str(class_nonnull)
            + ' non-null of '
            + str(n_total)
            + ' shipped rows with '
            + str(class_nunique)
            + ' distinct class values',
            'expected': 'the documented Reporting Railroad Class field is non-null for every shipped population row in the current snapshot and has at least one class value',
            'passed': bool(class_nonnull == n_total and class_nunique > 0),
        }
    )

    temp_values = frame['temperature'].dropna()
    temp_nonnull = int(len(temp_values))
    temp_zero = int((temp_values == 0).sum())
    checks.append(
        {
            'check': 'temperature coverage is recorded rather than assumed sparse',
            'observed': str(temp_nonnull)
            + ' non-null temperature values of '
            + str(n_total)
            + ' shipped rows; '
            + str(temp_zero)
            + ' equal zero',
            'expected': 'recorded Fahrenheit temperatures are present; missing values stay missing and zero is not used as a fill',
            'passed': bool(temp_nonnull > 0),
        }
    )

    for name in FEATURES:
        non_null = int(frame[name].notna().sum())
        checks.append(
            {
                'check': 'declared feature coverage for ' + name,
                'observed': str(non_null)
                + ' non-null of '
                + str(n_total)
                + ' shipped rows from source column '
                + resolved[name],
                'expected': 'at least one non-null value parsed from the resolved publisher column',
                'passed': bool(non_null > 0),
            }
        )

    eval_dt = (
        pd.to_datetime(eval_frame[TIME_COLUMN])
        if not eval_frame.empty
        else pd.Series(dtype='datetime64[ns]')
    )
    train_dt = (
        pd.to_datetime(train[TIME_COLUMN])
        if not train.empty
        else pd.Series(dtype='datetime64[ns]')
    )
    holdout_dt = (
        pd.to_datetime(holdout[TIME_COLUMN])
        if not holdout.empty
        else pd.Series(dtype='datetime64[ns]')
    )

    train_ok = bool(not train.empty and train_dt.max() < TRAIN_END)
    eval_ok = bool(
        not eval_frame.empty and eval_dt.min() >= TRAIN_END and eval_dt.max() < EVAL_END
    )
    holdout_ok = bool(not holdout.empty and holdout_dt.min() >= EVAL_END)

    checks.append(
        {
            'check': 'frozen chronological windows hold disjoint accident dates',
            'observed': 'train '
            + str(len(train))
            + ' rows ('
            + _window_text(train)
            + '); eval '
            + str(len(eval_frame))
            + ' rows ('
            + _window_text(eval_frame)
            + '); holdout '
            + str(len(holdout))
            + ' rows ('
            + _window_text(holdout)
            + ')',
            'expected': 'train before 2000-01-01, eval in the half-open window from 2000-01-01 to 2013-01-01, holdout from 2013-01-01 onward, every window non-empty',
            'passed': bool(train_ok and eval_ok and holdout_ok),
        }
    )

    checks.append(
        {
            'check': 'accident dates carry day precision for the split windows',
            'observed': str(day_precision)
            + ' rows with a composed or parsed day-level date; '
            + str(dropped_no_date)
            + ' dropped without any usable date; '
            + str(unresolved_dates)
            + ' unresolved after the January 1 fallback; '
            + str(n_total)
            + ' shipped',
            'expected': 'every shipped row dated from the accident year, month and day (or a publisher date field), with January 1 of the accident year as the last resort',
            'passed': bool(n_total > 0 and day_precision > 0 and unresolved_dates == 0),
        }
    )

    whole_cars = frame['hazmatcars'].dropna()
    fractional = float(((whole_cars % 1) != 0).mean()) if len(whole_cars) else 1.0
    checks.append(
        {
            'check': 'hazmat car counts are whole cars rather than a rate or a tonnage',
            'observed': 'share of shipped rows with a non-integer hazmat car count '
            + format(fractional, '.6f'),
            'expected': 'whole-car counts from the Form 54 consist block',
            'passed': bool(len(whole_cars) > 0 and fractional == 0.0),
            'kind': 'unit',
        }
    )

    tonnage = frame['grosstonnage'].dropna()
    negatives = int((tonnage < 0).sum())
    checks.append(
        {
            'check': 'gross tonnage is a non-negative tonnage of the whole train',
            'observed': str(negatives)
            + ' shipped rows with a negative gross tonnage and '
            + str(int(len(tonnage)))
            + ' rows with a parsed tonnage',
            'expected': 'Form 54 gross tonnage in tons, non-negative',
            'passed': bool(negatives == 0 and len(tonnage) > 0),
            'kind': 'unit',
        }
    )

    failed = [check for check in checks if not check['passed']]
    if failed:
        raise AssertionError(
            ('Form 54 build checks failed: ' + json.dumps(failed, default=str))[:3500]
        )

    return checks

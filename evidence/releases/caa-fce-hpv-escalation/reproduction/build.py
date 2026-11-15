import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from source_io import fetch

SOURCE_URL = 'https://echo.epa.gov/files/echodownloads/ICIS-AIR_downloads.zip'
ARCHIVE_NAME = 'ICIS-AIR_downloads.zip'
EXTRACT_DATE = pd.Timestamp('2026-11-07')
TARGET = 'hpv_escalation_12m'
FEATURES = [
    'state',
    'epa_region',
    'sic_2digit',
    'naics_2digit',
    'facility_type_code',
    'air_pollutant_class_code',
    'program_count',
    'pollutant_count',
    'comp_monitor_type_code',
    'state_epa_flag',
    'prior_evaluations_3y',
    'days_since_last_evaluation',
    'prior_stack_test_failures_3y',
    'prior_hpv_count',
    'days_since_hpv_resolution',
    'prior_formal_actions_3y',
    'prior_penalties_3y',
    'prior_tv_deviations_3y',
]
TEXT_FEATURES = [
    'state',
    'epa_region',
    'sic_2digit',
    'naics_2digit',
    'facility_type_code',
    'air_pollutant_class_code',
    'comp_monitor_type_code',
    'state_epa_flag',
]
OUTPUT_COLUMNS = ['evaluation_id', 'evaluation_end_date', TARGET] + FEATURES
SPLIT_WINDOWS = {
    'train': (pd.Timestamp('2015-01-01'), pd.Timestamp('2019-01-01')),
    'eval': (pd.Timestamp('2020-01-01'), pd.Timestamp('2023-01-01')),
    'holdout': (pd.Timestamp('2024-01-01'), pd.Timestamp('2025-07-01')),
}
TABLE_FILES = {
    'facilities': 'ICIS-AIR_FACILITIES.CSV',
    'programs': 'ICIS-AIR_PROGRAMS.CSV',
    'pollutants': 'ICIS-AIR_POLLUTANTS.CSV',
    'fces': 'ICIS-AIR_FCES_PCES.CSV',
    'stack_tests': 'ICIS-AIR_STACK_TESTS.CSV',
    'titlev': 'ICIS-AIR_TITLEV_CERTS.CSV',
    'violations': 'ICIS-AIR_VIOLATION_HISTORY.CSV',
    'formal': 'ICIS-AIR_FORMAL_ACTIONS.CSV',
}


def _clean_text(series):
    out = series.astype('string').str.strip()
    out = out.mask(out.eq(''))
    return out.mask(out.str.upper().isin(['NULL', 'NONE', 'NAN', 'N/A']))


def _parse_date(series):
    s = _clean_text(series)
    out = pd.to_datetime(s, format='%m/%d/%Y', errors='coerce')
    mask = out.isna() & s.notna()
    if bool(mask.any()):
        try:
            alt = pd.to_datetime(s[mask], errors='coerce', format='mixed')
        except TypeError:
            alt = pd.to_datetime(s[mask], errors='coerce')
        if getattr(alt.dt, 'tz', None) is not None:
            alt = alt.dt.tz_convert(None)
        out.loc[mask] = alt
    return out.dt.normalize()


def _num(series):
    text = series.astype('string').str.replace(',', '', regex=False)
    text = text.str.replace('[^0-9.-]', '', regex=True)
    return pd.to_numeric(text, errors='coerce')


def _code_prefix(series, n=2):
    text = _clean_text(series).fillna('').str.upper()
    text = text.str.replace('[^0-9A-Za-z]+', ' ', regex=True).str.strip()
    first = text.str.split(' ').str[0]
    digits = first.str.extract('([0-9]+)', expand=False)
    return digits.str[:n].astype('string').replace('', pd.NA)


def _explode_codes(df, id_col, code_col):
    work = df[[id_col, code_col]].copy()
    work[id_col] = _clean_text(work[id_col])
    work[code_col] = _clean_text(work[code_col])
    work = work.dropna(subset=[id_col, code_col])
    work['code'] = (
        work[code_col]
        .str.upper()
        .str.replace('[^0-9A-Za-z]+', ' ', regex=True)
        .str.strip()
        .str.split(' ')
    )
    work = work.explode('code')
    work['code'] = work['code'].astype('string').str.strip()
    work = work[work['code'].notna() & work['code'].ne('')]
    return work[[id_col, 'code']].drop_duplicates()


def _norm(df):
    out = df.copy()
    out.columns = [str(col).strip().upper() for col in out.columns]
    return out


def _read_table(zf, member):
    last_error = None
    for encoding in ('utf-8-sig', 'latin-1'):
        try:
            with zf.open(member) as handle:
                frame = pd.read_csv(
                    handle,
                    dtype=str,
                    low_memory=False,
                    keep_default_na=False,
                    encoding=encoding,
                )
            return _norm(frame)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    message = (
        f'Could not decode archive member {member} as utf-8-sig or latin-1. '
        f'Last decoding error: {last_error}'
    )
    raise AssertionError(message[:4000])


def _member_map(zf):
    out = {}
    for name in zf.namelist():
        if name.endswith('/'):
            continue
        out[Path(name).name.upper()] = name
    return out


def _require(df, table, member, required):
    missing = [name for name in required if name not in df.columns]
    if missing:
        message = (
            f'Required fields missing from {table} in archive member {member}: {missing}. '
            f'Observed headers: {list(df.columns)}'
        )
        raise AssertionError(message[:4000])


def _pick(df, candidates, table, member, label='field'):
    for name in candidates:
        if name in df.columns:
            return name
    message = (
        f'None of the expected {label} names {candidates} are present in {table} '
        f'in archive member {member}. Observed headers: {list(df.columns)}'
    )
    raise AssertionError(message[:4000])


def _check(checks, name, observed, expected, passed):
    checks.append(
        {
            'check': name,
            'observed': str(observed),
            'expected': str(expected),
            'passed': bool(passed),
        }
    )


def _date_check(checks, label, raw, parsed):
    nonblank = int(_clean_text(raw).notna().sum())
    good = int(parsed.notna().sum())
    ratio = good / nonblank if nonblank else 0.0
    _check(
        checks,
        label + ' parse coverage',
        f'{good} parsed of {nonblank} nonblank values (ratio {ratio:.3f})',
        'at least 90 percent of nonblank values parse as calendar dates',
        nonblank > 0 and ratio >= 0.9,
    )


def _assign_split(dates):
    out = pd.Series(pd.NA, index=dates.index, dtype='string')
    for name, (start, end) in SPLIT_WINDOWS.items():
        out.loc[(dates >= start) & (dates < end)] = name
    return out


def _safe_int(value):
    try:
        if pd.isna(value):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def build(output: Path, cache: Path):
    output = Path(output)
    cache = Path(cache)
    (output / 'public').mkdir(parents=True, exist_ok=True)
    (output / 'private').mkdir(parents=True, exist_ok=True)
    checks = []

    archive = Path(fetch(SOURCE_URL, cache, ARCHIVE_NAME))
    with zipfile.ZipFile(archive, 'r') as zf:
        members = _member_map(zf)
        required = list(TABLE_FILES.values())
        missing = [name for name in required if name not in members]
        _check(
            checks,
            'archive member availability',
            f'observed {len(members)} archive members; missing {missing}',
            f'required archive members all present: {required}',
            not missing,
        )
        if missing:
            message = (
                f'ZIP {ARCHIVE_NAME} is missing required archive members {missing}. '
                f'Observed archive members: {sorted(members)}'
            )
            raise AssertionError(message[:4000])
        tables = {
            key: _read_table(zf, members[name]) for key, name in TABLE_FILES.items()
        }

    counts = {key: len(value) for key, value in tables.items()}
    _check(
        checks,
        'table row counts',
        counts,
        'every required table has at least one row',
        all(value > 0 for value in counts.values()),
    )

    fac = tables['facilities'].copy()
    fmem = members['ICIS-AIR_FACILITIES.CSV']
    fac_id = _pick(fac, ['PGM_SYS_ID'], 'ICIS-AIR_FACILITIES.csv', fmem, 'facility identifier field')
    fac_state = _pick(fac, ['STATE', 'STATE_CODE'], 'ICIS-AIR_FACILITIES.csv', fmem, 'state field')
    fac_region = _pick(fac, ['EPA_REGION', 'REGION_CODE'], 'ICIS-AIR_FACILITIES.csv', fmem, 'EPA region field')
    fac_type = _pick(fac, ['FACILITY_TYPE_CODE'], 'ICIS-AIR_FACILITIES.csv', fmem, 'facility type field')
    fac_sic = _pick(fac, ['SIC_CODES', 'SIC_CODE'], 'ICIS-AIR_FACILITIES.csv', fmem, 'SIC list field')
    fac_naics = _pick(fac, ['NAICS_CODES', 'NAICS_CODE'], 'ICIS-AIR_FACILITIES.csv', fmem, 'NAICS list field')
    fac_class = _pick(fac, ['AIR_POLLUTANT_CLASS_CODE', 'AIR_POLLUTANT_CLASS'], 'ICIS-AIR_FACILITIES.csv', fmem, 'emission class field')
    resolved = {
        'identifier': fac_id,
        'state': fac_state,
        'region': fac_region,
        'type': fac_type,
        'sic': fac_sic,
        'naics': fac_naics,
        'emission_class': fac_class,
    }
    _check(
        checks,
        'facility field names resolved from header',
        str(resolved),
        'each facility attribute resolves to a published column name in the facilities table',
        all(isinstance(value, str) and value for value in resolved.values()),
    )
    fac = fac[[fac_id, fac_state, fac_region, fac_type, fac_sic, fac_naics, fac_class]].rename(
        columns={
            fac_id: 'PGM_SYS_ID',
            fac_state: 'state',
            fac_region: 'epa_region',
            fac_type: 'facility_type_code',
            fac_sic: 'sic_codes',
            fac_naics: 'naics_codes',
            fac_class: 'air_class',
        }
    )
    _require(
        fac,
        'facility extract',
        fmem,
        ['PGM_SYS_ID', 'state', 'epa_region', 'facility_type_code', 'sic_codes', 'naics_codes', 'air_class'],
    )
    fac['PGM_SYS_ID'] = _clean_text(fac['PGM_SYS_ID'])
    fac = fac.dropna(subset=['PGM_SYS_ID']).drop_duplicates('PGM_SYS_ID', keep='first')
    fac['state'] = _clean_text(fac['state']).str.upper()
    fac['epa_region'] = _clean_text(fac['epa_region'])
    fac['facility_type_code'] = _clean_text(fac['facility_type_code']).str.upper()
    fac['sic_2digit'] = _code_prefix(fac['sic_codes'])
    fac['naics_2digit'] = _code_prefix(fac['naics_codes'])
    fac['air_pollutant_class_code'] = _clean_text(fac['air_class']).str.upper()
    fac_use = fac[
        [
            'PGM_SYS_ID',
            'state',
            'epa_region',
            'sic_2digit',
            'naics_2digit',
            'facility_type_code',
            'air_pollutant_class_code',
        ]
    ]

    prog = tables['programs'].copy()
    pmem = members['ICIS-AIR_PROGRAMS.CSV']
    prog_id = _pick(prog, ['PGM_SYS_ID'], 'ICIS-AIR_PROGRAMS.csv', pmem, 'facility identifier field')
    prog_code = _pick(prog, ['PROGRAM_CODE', 'PROGRAM_CODES'], 'ICIS-AIR_PROGRAMS.csv', pmem, 'program code field')
    prog = prog[[prog_id, prog_code]].rename(columns={prog_id: 'PGM_SYS_ID', prog_code: 'PROGRAM_CODE'})
    _require(prog, 'program extract', pmem, ['PGM_SYS_ID', 'PROGRAM_CODE'])
    prog['PGM_SYS_ID'] = _clean_text(prog['PGM_SYS_ID'])
    prog['PROGRAM_CODE'] = _clean_text(prog['PROGRAM_CODE']).str.upper()
    prog = prog.dropna(subset=['PGM_SYS_ID'])
    has_program = prog.groupby('PGM_SYS_ID').size().rename('has_program')
    prog_count = (
        prog.dropna(subset=['PROGRAM_CODE'])
        .drop_duplicates(['PGM_SYS_ID', 'PROGRAM_CODE'])
        .groupby('PGM_SYS_ID')
        .size()
        .rename('program_count')
    )

    pol = tables['pollutants'].copy()
    omem = members['ICIS-AIR_POLLUTANTS.CSV']
    pol_id = _pick(pol, ['PGM_SYS_ID'], 'ICIS-AIR_POLLUTANTS.csv', omem, 'facility identifier field')
    pol_code = _pick(pol, ['POLLUTANT_CODES', 'POLLUTANT_CODE'], 'ICIS-AIR_POLLUTANTS.csv', omem, 'pollutant code field')
    pol = pol[[pol_id, pol_code]].rename(columns={pol_id: 'PGM_SYS_ID', pol_code: 'POLLUTANT_CODES'})
    pol_codes = _explode_codes(pol, 'PGM_SYS_ID', 'POLLUTANT_CODES')
    pol_count = pol_codes.groupby('PGM_SYS_ID').size().rename('pollutant_count')
    _check(
        checks,
        'pollutant code pairs',
        f'{len(pol_codes)} distinct facility and pollutant code pairs',
        'at least one distinct facility and pollutant code pair is parsed from the current pollutants table',
        len(pol_codes) > 0,
    )

    fce = tables['fces'].copy()
    xmem = members['ICIS-AIR_FCES_PCES.CSV']
    fce_id = _pick(fce, ['PGM_SYS_ID'], 'ICIS-AIR_FCES_PCES.csv', xmem, 'facility identifier field')
    fce_act = _pick(fce, ['ACTIVITY_ID'], 'ICIS-AIR_FCES_PCES.csv', xmem, 'activity identifier field')
    fce_end = _pick(fce, ['ACTUAL_END_DATE'], 'ICIS-AIR_FCES_PCES.csv', xmem, 'evaluation end date field')
    fce_mon = _pick(fce, ['COMP_MONITOR_TYPE_CODE'], 'ICIS-AIR_FCES_PCES.csv', xmem, 'monitor type field')
    fce_flag = _pick(fce, ['STATE_EPA_FLAG'], 'ICIS-AIR_FCES_PCES.csv', xmem, 'lead agency flag field')
    fce = fce[[fce_id, fce_act, fce_end, fce_mon, fce_flag]].rename(
        columns={
            fce_id: 'PGM_SYS_ID',
            fce_act: 'ACTIVITY_ID',
            fce_end: 'ACTUAL_END_DATE',
            fce_mon: 'COMP_MONITOR_TYPE_CODE',
            fce_flag: 'STATE_EPA_FLAG',
        }
    )
    _require(
        fce,
        'evaluation extract',
        xmem,
        ['PGM_SYS_ID', 'ACTIVITY_ID', 'ACTUAL_END_DATE', 'COMP_MONITOR_TYPE_CODE', 'STATE_EPA_FLAG'],
    )
    fce['PGM_SYS_ID'] = _clean_text(fce['PGM_SYS_ID'])
    fce['ACTIVITY_ID'] = _clean_text(fce['ACTIVITY_ID'])
    fce['evaluation_end_date'] = _parse_date(fce['ACTUAL_END_DATE'])
    fce['comp_monitor_type_code'] = _clean_text(fce['COMP_MONITOR_TYPE_CODE']).str.upper()
    fce['state_epa_flag'] = _clean_text(fce['STATE_EPA_FLAG']).str.upper()
    _date_check(checks, 'FCE ACTUAL_END_DATE', fce['ACTUAL_END_DATE'], fce['evaluation_end_date'])
    fce = fce.dropna(subset=['PGM_SYS_ID', 'ACTIVITY_ID', 'evaluation_end_date'])
    fce = (
        fce.sort_values(
            ['PGM_SYS_ID', 'ACTIVITY_ID', 'evaluation_end_date', 'comp_monitor_type_code', 'state_epa_flag'],
            kind='mergesort',
        )
        .drop_duplicates(['PGM_SYS_ID', 'ACTIVITY_ID'], keep='first')
        .reset_index(drop=True)
    )

    vh = tables['violations'].copy()
    vmem = members['ICIS-AIR_VIOLATION_HISTORY.CSV']
    vh_id = _pick(vh, ['PGM_SYS_ID'], 'ICIS-AIR_VIOLATION_HISTORY.csv', vmem, 'facility identifier field')
    vh_start = _pick(vh, ['HPV_DAYZERO_DATE'], 'ICIS-AIR_VIOLATION_HISTORY.csv', vmem, 'HPV day-zero field')
    vh_end = _pick(vh, ['HPV_RESOLVED_DATE'], 'ICIS-AIR_VIOLATION_HISTORY.csv', vmem, 'HPV resolution field')
    vh = vh[[vh_id, vh_start, vh_end]].rename(
        columns={vh_id: 'PGM_SYS_ID', vh_start: 'HPV_DAYZERO_DATE', vh_end: 'HPV_RESOLVED_DATE'}
    )
    _require(vh, 'violation history extract', vmem, ['PGM_SYS_ID', 'HPV_DAYZERO_DATE', 'HPV_RESOLVED_DATE'])
    vh['PGM_SYS_ID'] = _clean_text(vh['PGM_SYS_ID'])
    vh['hpv_dayzero_date'] = _parse_date(vh['HPV_DAYZERO_DATE'])
    vh['hpv_resolved_date'] = _parse_date(vh['HPV_RESOLVED_DATE'])
    _date_check(checks, 'HPV day-zero', vh['HPV_DAYZERO_DATE'], vh['hpv_dayzero_date'])
    _date_check(checks, 'HPV resolution', vh['HPV_RESOLVED_DATE'], vh['hpv_resolved_date'])
    vh = vh.dropna(subset=['PGM_SYS_ID', 'hpv_dayzero_date'])
    vh['_one'] = 1
    vh = vh.groupby(['PGM_SYS_ID', 'hpv_dayzero_date'], as_index=False).agg(
        res_min=('hpv_resolved_date', 'min'),
        res_cnt=('hpv_resolved_date', 'count'),
        row_cnt=('_one', 'sum'),
    )
    vh['hpv_resolved_date'] = vh['res_min'].where(vh['res_cnt'].eq(vh['row_cnt']))
    vh = vh[['PGM_SYS_ID', 'hpv_dayzero_date', 'hpv_resolved_date']]
    _check(
        checks,
        'HPV episode rows',
        f'{len(vh)} distinct facility and day-zero episodes',
        'at least one HPV day-zero episode is present',
        len(vh) > 0,
    )

    st = tables['stack_tests'].copy()
    smem = members['ICIS-AIR_STACK_TESTS.CSV']
    st_id = _pick(st, ['PGM_SYS_ID'], 'ICIS-AIR_STACK_TESTS.csv', smem, 'facility identifier field')
    st_act = _pick(st, ['ACTIVITY_ID'], 'ICIS-AIR_STACK_TESTS.csv', smem, 'activity identifier field')
    st_date = _pick(
        st,
        [
            'STACK_TEST_DATE',
            'AIR_STACK_TEST_DATE',
            'TEST_DATE',
            'STACK_TEST_BEGIN_DATE',
            'STACK_TEST_END_DATE',
            'ACTIVITY_DATE',
            'ACTUAL_END_DATE',
        ],
        'ICIS-AIR_STACK_TESTS.csv',
        smem,
        'stack test date field',
    )
    st_status = _pick(
        st,
        ['AIR_STACK_TEST_STATUS_CODE', 'STACK_TEST_STATUS_CODE'],
        'ICIS-AIR_STACK_TESTS.csv',
        smem,
        'stack test status field',
    )
    st = st[[st_id, st_act, st_date, st_status]].rename(
        columns={
            st_id: 'PGM_SYS_ID',
            st_act: 'ACTIVITY_ID',
            st_date: 'STACK_TEST_DATE',
            st_status: 'AIR_STACK_TEST_STATUS_CODE',
        }
    )
    _require(
        st,
        'stack test extract',
        smem,
        ['PGM_SYS_ID', 'ACTIVITY_ID', 'STACK_TEST_DATE', 'AIR_STACK_TEST_STATUS_CODE'],
    )
    st['PGM_SYS_ID'] = _clean_text(st['PGM_SYS_ID'])
    st['ACTIVITY_ID'] = _clean_text(st['ACTIVITY_ID'])
    st['stack_date'] = _parse_date(st['STACK_TEST_DATE'])
    st['AIR_STACK_TEST_STATUS_CODE'] = _clean_text(st['AIR_STACK_TEST_STATUS_CODE']).str.upper()
    _date_check(checks, 'stack test date column ' + st_date, st['STACK_TEST_DATE'], st['stack_date'])
    st = st.dropna(subset=['PGM_SYS_ID', 'ACTIVITY_ID', 'stack_date'])
    st = st.sort_values(['PGM_SYS_ID', 'ACTIVITY_ID', 'stack_date'], kind='mergesort').drop_duplicates(
        ['PGM_SYS_ID', 'ACTIVITY_ID'], keep='first'
    )
    status_counts = st['AIR_STACK_TEST_STATUS_CODE'].value_counts(dropna=False).to_dict()
    _check(
        checks,
        'stack test status examples',
        f'AIR_STACK_TEST_STATUS_CODE counts {status_counts}',
        'the documented Fail code FAI appears in the parsed status column of the current snapshot',
        status_counts.get('FAI', 0) > 0,
    )

    tv = tables['titlev'].copy()
    tmem = members['ICIS-AIR_TITLEV_CERTS.CSV']
    tv_id = _pick(tv, ['PGM_SYS_ID'], 'ICIS-AIR_TITLEV_CERTS.csv', tmem, 'facility identifier field')
    tv_act = _pick(tv, ['ACTIVITY_ID'], 'ICIS-AIR_TITLEV_CERTS.csv', tmem, 'activity identifier field')
    tv_date = _pick(
        tv,
        [
            'CERTIFICATION_DATE',
            'TV_CERTIFICATION_DATE',
            'TITLEV_CERTIFICATION_DATE',
            'ANNUAL_CERTIFICATION_DATE',
            'CERT_DATE',
            'CERTIFICATION_RECEIVED_DATE',
            'RECEIVED_DATE',
            'ACTIVITY_DATE',
            'ACTUAL_END_DATE',
        ],
        'ICIS-AIR_TITLEV_CERTS.csv',
        tmem,
        'certification date field',
    )
    tv_flag = _pick(
        tv,
        ['FACILITY_RPT_DEVIATION_FLAG', 'DEVIATION_FLAG'],
        'ICIS-AIR_TITLEV_CERTS.csv',
        tmem,
        'deviation flag field',
    )
    tv = tv[[tv_id, tv_act, tv_date, tv_flag]].rename(
        columns={
            tv_id: 'PGM_SYS_ID',
            tv_act: 'ACTIVITY_ID',
            tv_date: 'CERTIFICATION_DATE',
            tv_flag: 'FACILITY_RPT_DEVIATION_FLAG',
        }
    )
    _require(
        tv,
        'title V extract',
        tmem,
        ['PGM_SYS_ID', 'ACTIVITY_ID', 'CERTIFICATION_DATE', 'FACILITY_RPT_DEVIATION_FLAG'],
    )
    tv['PGM_SYS_ID'] = _clean_text(tv['PGM_SYS_ID'])
    tv['ACTIVITY_ID'] = _clean_text(tv['ACTIVITY_ID'])
    tv['tv_date'] = _parse_date(tv['CERTIFICATION_DATE'])
    flag_vals = _clean_text(tv['FACILITY_RPT_DEVIATION_FLAG']).str.upper()
    tv['deviation'] = flag_vals.str.startswith('Y', na=False).astype(bool)
    _date_check(checks, 'Title V certification date column ' + tv_date, tv['CERTIFICATION_DATE'], tv['tv_date'])
    tv = tv.dropna(subset=['PGM_SYS_ID', 'ACTIVITY_ID', 'tv_date'])
    tv = tv.sort_values(['PGM_SYS_ID', 'ACTIVITY_ID', 'tv_date'], kind='mergesort').drop_duplicates(
        ['PGM_SYS_ID', 'ACTIVITY_ID'], keep='first'
    )
    flag_counts = flag_vals.value_counts(dropna=False).to_dict()
    yes_cnt = int(sum(value for key, value in flag_counts.items() if isinstance(key, str) and key.startswith('Y')))
    no_cnt = int(sum(value for key, value in flag_counts.items() if isinstance(key, str) and key.startswith('N')))
    total_flag = int(sum(flag_counts.values()))
    unrecognized_cnt = total_flag - yes_cnt - no_cnt
    _check(
        checks,
        'Title V deviation flag interpretation',
        f'FACILITY_RPT_DEVIATION_FLAG counts {flag_counts}; confirmed Yes values {yes_cnt}; No values {no_cnt}; unrecognized or blank values {unrecognized_cnt}',
        'confirmed Yes values count as reported deviations, No values count as none, and any other value is recorded here and treated as no confirmed deviation instead of aborting the build',
        yes_cnt > 0 and (yes_cnt + no_cnt) > 0,
    )

    fa = tables['formal'].copy()
    amem = members['ICIS-AIR_FORMAL_ACTIONS.CSV']
    fa_id = _pick(fa, ['PGM_SYS_ID'], 'ICIS-AIR_FORMAL_ACTIONS.csv', amem, 'facility identifier field')
    fa_act = _pick(fa, ['ACTIVITY_ID'], 'ICIS-AIR_FORMAL_ACTIONS.csv', amem, 'activity identifier field')
    fa_date = _pick(
        fa,
        ['SETTLEMENT_ENTERED_DATE', 'SETTLEMENT_DATE'],
        'ICIS-AIR_FORMAL_ACTIONS.csv',
        amem,
        'settlement date field',
    )
    fa_pen = _pick(
        fa,
        ['PENALTY_AMOUNT', 'FINAL_PENALTY_AMOUNT'],
        'ICIS-AIR_FORMAL_ACTIONS.csv',
        amem,
        'penalty amount field',
    )
    fa = fa[[fa_id, fa_act, fa_date, fa_pen]].rename(
        columns={
            fa_id: 'PGM_SYS_ID',
            fa_act: 'ACTIVITY_ID',
            fa_date: 'SETTLEMENT_ENTERED_DATE',
            fa_pen: 'PENALTY_AMOUNT',
        }
    )
    _require(
        fa,
        'formal action extract',
        amem,
        ['PGM_SYS_ID', 'ACTIVITY_ID', 'SETTLEMENT_ENTERED_DATE', 'PENALTY_AMOUNT'],
    )
    fa['PGM_SYS_ID'] = _clean_text(fa['PGM_SYS_ID'])
    fa['ACTIVITY_ID'] = _clean_text(fa['ACTIVITY_ID'])
    fa['settlement_date'] = _parse_date(fa['SETTLEMENT_ENTERED_DATE'])
    fa['penalty'] = _num(fa['PENALTY_AMOUNT'])
    _date_check(checks, 'formal action settlement date', fa['SETTLEMENT_ENTERED_DATE'], fa['settlement_date'])
    pen_nonblank = int(_clean_text(fa['PENALTY_AMOUNT']).notna().sum())
    pen_good = int(fa['penalty'].notna().sum())
    _check(
        checks,
        'penalty amount numeric parse',
        f'{pen_good} parsed of {pen_nonblank} nonblank values',
        'penalty amounts parse as numbers and blank values stay missing rather than becoming zero',
        pen_nonblank == 0 or pen_good > 0,
    )
    fa = fa.dropna(subset=['PGM_SYS_ID', 'ACTIVITY_ID', 'settlement_date'])
    fa = fa.sort_values(['PGM_SYS_ID', 'ACTIVITY_ID', 'settlement_date'], kind='mergesort').drop_duplicates(
        ['PGM_SYS_ID', 'ACTIVITY_ID'], keep='first'
    )

    cand = fce[fce['comp_monitor_type_code'].isin(['FOO', 'FFO'])].copy()
    n_full_rows = int(len(cand))
    code_counts = fce['comp_monitor_type_code'].value_counts(dropna=False).to_dict()
    _check(
        checks,
        'full evaluation code examples',
        f'COMP_MONITOR_TYPE_CODE counts {code_counts}',
        'the documented full evaluation codes FOO and FFO both appear in the current snapshot',
        code_counts.get('FOO', 0) > 0 and code_counts.get('FFO', 0) > 0,
    )
    cand = cand.merge(has_program, left_on='PGM_SYS_ID', right_index=True, how='left')
    n_with_program = int(cand['has_program'].notna().sum())
    cand = cand[cand['has_program'].notna()].copy()
    cand['split'] = _assign_split(cand['evaluation_end_date'])
    cand = cand[cand['split'].notna()].copy()
    cand['horizon_end'] = cand['evaluation_end_date'] + pd.Timedelta(days=365)
    n_in_window = int(len(cand))
    cand = cand[cand['horizon_end'] <= EXTRACT_DATE].copy()
    n_mature = int(len(cand))
    cand = cand.reset_index(drop=True)
    cand['_row_id'] = np.arange(len(cand), dtype=np.int64)
    cand['evaluation_id'] = cand['PGM_SYS_ID'].astype(str) + ':' + cand['ACTIVITY_ID'].astype(str)

    ep = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date', 'horizon_end']].merge(
        vh, on='PGM_SYS_ID', how='left'
    )
    ep['active_hpv'] = (ep['hpv_dayzero_date'] <= ep['evaluation_end_date']) & (
        ep['hpv_resolved_date'].isna() | (ep['hpv_resolved_date'] > ep['evaluation_end_date'])
    )
    ep['same_day_hpv'] = ep['hpv_dayzero_date'].eq(ep['evaluation_end_date'])
    ep['label_hpv'] = (ep['hpv_dayzero_date'] > ep['evaluation_end_date']) & (
        ep['hpv_dayzero_date'] <= ep['horizon_end']
    )
    ep['prior_hpv'] = ep['hpv_dayzero_date'] < ep['evaluation_end_date']
    ep['prior_resolved'] = ep['hpv_resolved_date'].where(
        ep['hpv_resolved_date'] < ep['evaluation_end_date']
    )
    hpv_agg = ep.groupby('_row_id').agg(
        active_hpv=('active_hpv', 'max'),
        same_day_hpv=('same_day_hpv', 'max'),
        label=('label_hpv', 'max'),
        prior_hpv_count=('prior_hpv', 'sum'),
        last_hpv_resolution=('prior_resolved', 'max'),
    )
    hpv_agg = hpv_agg.reindex(cand['_row_id'])
    hpv_agg['active_hpv'] = hpv_agg['active_hpv'].fillna(False).astype(bool)
    hpv_agg['same_day_hpv'] = hpv_agg['same_day_hpv'].fillna(False).astype(bool)
    hpv_agg['label'] = hpv_agg['label'].fillna(False).astype(bool)
    hpv_agg['prior_hpv_count'] = hpv_agg['prior_hpv_count'].fillna(0).astype('Int64')
    cand = cand.merge(hpv_agg.reset_index(), on='_row_id', how='left')
    excluded_active = int(cand['active_hpv'].sum())
    excluded_same_day = int(cand['same_day_hpv'].sum())
    cand = cand[(~cand['active_hpv']) & (~cand['same_day_hpv'])].copy()

    full_fce = fce[fce['comp_monitor_type_code'].isin(['FOO', 'FFO'])][
        ['PGM_SYS_ID', 'evaluation_end_date']
    ]
    pre = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date']].merge(
        full_fce, on='PGM_SYS_ID', how='left', suffixes=('', '_prior')
    )
    pre['prior_full'] = (
        pre['evaluation_end_date_prior'] >= pre['evaluation_end_date'] - pd.Timedelta(days=365)
    ) & (pre['evaluation_end_date_prior'] < pre['evaluation_end_date'])
    pc = pre.groupby('_row_id')['prior_full'].sum()
    cand['prior_full_fce_365'] = cand['_row_id'].map(pc).fillna(0).astype(int)
    excluded_prior_fce = int((cand['prior_full_fce_365'] > 0).sum())
    cand = cand[cand['prior_full_fce_365'].eq(0)].copy()
    cand = (
        cand.sort_values(['PGM_SYS_ID', 'evaluation_end_date', 'ACTIVITY_ID'], kind='mergesort')
        .drop_duplicates(['PGM_SYS_ID', 'evaluation_end_date'], keep='first')
        .reset_index(drop=True)
    )
    _check(
        checks,
        'evaluation population funnel',
        'full evaluation rows {0}; with a programs row {1}; inside a frozen window {2}; with a fully observed 365-day horizon {3}; excluded for an active HPV episode {4}; excluded for a same-day HPV day-zero {5}; excluded for another full evaluation in the prior 365 days {6}; retained {7}'.format(
            n_full_rows,
            n_with_program,
            n_in_window,
            n_mature,
            excluded_active,
            excluded_same_day,
            excluded_prior_fce,
            len(cand),
        ),
        'each stage of the frozen population rule can only remove rows and at least one evaluation row is retained',
        n_full_rows > 0 and n_with_program > 0 and n_in_window > 0 and n_mature > 0 and len(cand) > 0,
    )

    ev = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date']].merge(
        fce[['PGM_SYS_ID', 'evaluation_end_date']], on='PGM_SYS_ID', how='left', suffixes=('', '_hist')
    )
    ev['prior_eval_3y'] = (
        ev['evaluation_end_date_hist'] >= ev['evaluation_end_date'] - pd.Timedelta(days=1095)
    ) & (ev['evaluation_end_date_hist'] < ev['evaluation_end_date'])
    ev['prior_date'] = ev['evaluation_end_date_hist'].where(
        ev['evaluation_end_date_hist'] < ev['evaluation_end_date']
    )
    ev_agg = ev.groupby('_row_id').agg(
        prior_evaluations_3y=('prior_eval_3y', 'sum'),
        last_prior_eval=('prior_date', 'max'),
    )
    cand = cand.merge(ev_agg.reset_index(), on='_row_id', how='left')
    cand['prior_evaluations_3y'] = cand['prior_evaluations_3y'].fillna(0).astype('Int64')
    cand['days_since_last_evaluation'] = (
        cand['evaluation_end_date'] - cand['last_prior_eval']
    ).dt.days.astype('Float64')

    se = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date']].merge(
        st[['PGM_SYS_ID', 'stack_date', 'AIR_STACK_TEST_STATUS_CODE']], on='PGM_SYS_ID', how='left'
    )
    se['prior_fail'] = (
        se['AIR_STACK_TEST_STATUS_CODE'].eq('FAI')
        & (se['stack_date'] >= se['evaluation_end_date'] - pd.Timedelta(days=1095))
        & (se['stack_date'] < se['evaluation_end_date'])
    )
    st_agg = se.groupby('_row_id').agg(prior_stack_test_failures_3y=('prior_fail', 'sum'))

    fe = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date']].merge(
        fa[['PGM_SYS_ID', 'settlement_date', 'penalty']], on='PGM_SYS_ID', how='left'
    )
    fe['prior_action'] = (
        fe['settlement_date'] >= fe['evaluation_end_date'] - pd.Timedelta(days=1095)
    ) & (fe['settlement_date'] < fe['evaluation_end_date'])
    fe['prior_penalty'] = fe['penalty'].where(fe['prior_action'])
    fa_agg = fe.groupby('_row_id').agg(
        prior_formal_actions_3y=('prior_action', 'sum'),
        prior_penalties_3y=('prior_penalty', lambda values: values.sum(min_count=1)),
    )

    te = cand[['_row_id', 'PGM_SYS_ID', 'evaluation_end_date']].merge(
        tv[['PGM_SYS_ID', 'tv_date', 'deviation']], on='PGM_SYS_ID', how='left'
    )
    te['prior_dev'] = (
        te['deviation'].fillna(False).astype(bool)
        & (te['tv_date'] >= te['evaluation_end_date'] - pd.Timedelta(days=1095))
        & (te['tv_date'] < te['evaluation_end_date'])
    )
    tv_agg = te.groupby('_row_id').agg(prior_tv_deviations_3y=('prior_dev', 'sum'))

    cand = cand.merge(st_agg.reset_index(), on='_row_id', how='left')
    cand = cand.merge(fa_agg.reset_index(), on='_row_id', how='left')
    cand = cand.merge(tv_agg.reset_index(), on='_row_id', how='left')
    for column in ['prior_stack_test_failures_3y', 'prior_formal_actions_3y', 'prior_tv_deviations_3y']:
        cand[column] = cand[column].fillna(0).astype('Int64')
    cand['prior_penalties_3y'] = cand['prior_penalties_3y'].astype('Float64')
    zero_actions = cand['prior_formal_actions_3y'].eq(0)
    missing_penalty = cand['prior_penalties_3y'].isna()
    cand.loc[zero_actions & missing_penalty, 'prior_penalties_3y'] = 0.0
    cand['prior_hpv_count'] = cand['prior_hpv_count'].fillna(0).astype('Int64')
    cand['days_since_hpv_resolution'] = (
        cand['evaluation_end_date'] - cand['last_hpv_resolution']
    ).dt.days.astype('Float64')

    cand[TARGET] = cand['label'].astype(int)

    cand = cand.merge(fac_use, on='PGM_SYS_ID', how='left')
    cand = cand.merge(prog_count, left_on='PGM_SYS_ID', right_index=True, how='left')
    cand = cand.merge(pol_count, left_on='PGM_SYS_ID', right_index=True, how='left')
    cand['program_count'] = cand['program_count'].fillna(0).astype('Int64')
    cand['pollutant_count'] = cand['pollutant_count'].fillna(0).astype('Int64')

    target_values = sorted(cand[TARGET].dropna().unique().tolist())
    _check(
        checks,
        'target values',
        f'values {target_values}; counts {cand[TARGET].value_counts().to_dict()}',
        'target is binary, nonmissing, and uses only 0 and 1',
        set(target_values).issubset({0, 1}) and bool(cand[TARGET].notna().all()),
    )

    split_summary = {}
    for name in ('train', 'eval', 'holdout'):
        part = cand[cand['split'] == name]
        split_summary[name] = {
            'rows': int(len(part)),
            'positives': int((part[TARGET] == 1).sum()),
        }
    _check(
        checks,
        'frozen split row and positive counts',
        split_summary,
        'train, eval and holdout each contain rows, at least one positive label and at least one negative label',
        all(value['rows'] > 0 and 0 < value['positives'] < value['rows'] for value in split_summary.values()),
    )

    max_horizon = cand['horizon_end'].max() if len(cand) else pd.NaT
    _check(
        checks,
        'label window fully observed at extract',
        f'max horizon end {max_horizon.date() if pd.notna(max_horizon) else None}; extract boundary {EXTRACT_DATE.date()}',
        'every horizon end falls on or before the 2026-11-07 snapshot boundary',
        bool(pd.notna(max_horizon)) and max_horizon <= EXTRACT_DATE,
    )

    active_after = int(cand['active_hpv'].sum())
    same_day_after = int(cand['same_day_hpv'].sum())
    max_prior_full = _safe_int(cand['prior_full_fce_365'].max()) if len(cand) else None
    _check(
        checks,
        'active HPV excluded at decision instant',
        f'{active_after} included rows had an active HPV episode at the evaluation date',
        'zero included rows',
        active_after == 0,
    )
    _check(
        checks,
        'same-day HPV day-zero excluded',
        f'{same_day_after} included rows had an HPV day-zero equal to the evaluation date',
        'zero included rows',
        same_day_after == 0,
    )
    _check(
        checks,
        'prior full evaluation within 365 days excluded',
        f'maximum prior full evaluations in the preceding 365 days among included rows {max_prior_full}',
        'zero',
        max_prior_full == 0,
    )

    dup_ids = int(cand['evaluation_id'].duplicated().sum())
    _check(checks, 'unique evaluation identifiers', f'{dup_ids} duplicate evaluation_id values', 'zero', dup_ids == 0)
    dup_facility_day = int(cand.duplicated(['PGM_SYS_ID', 'evaluation_end_date']).sum())
    _check(
        checks,
        'one included evaluation per facility and day',
        f'{dup_facility_day} duplicate facility and day rows',
        'zero',
        dup_facility_day == 0,
    )
    _check(
        checks,
        'identifier and time completeness',
        f'{int(cand["evaluation_id"].isna().sum())} missing evaluation identifiers; {int(cand["evaluation_end_date"].isna().sum())} missing evaluation dates',
        'zero missing identifiers and zero missing dates',
        bool(cand['evaluation_id'].notna().all()) and bool(cand['evaluation_end_date'].notna().all()),
    )

    join_ok = int(cand['state'].notna().sum())
    join_total = int(len(cand))
    join_ratio = join_ok / join_total if join_total else 0.0
    _check(
        checks,
        'facility join coverage for included rows',
        f'{join_ok} of {join_total} included rows carry a facility state value (ratio {join_ratio:.3f})',
        'at least 95 percent of included evaluation rows join to a facilities row on the facility identifier',
        join_total > 0 and join_ratio >= 0.95,
    )

    coverage = {name: int(cand[name].notna().sum()) for name in FEATURES}
    _check(
        checks,
        'declared feature coverage',
        coverage,
        'every declared feature has at least one nonmissing value in the retained rows; missing days and penalties stay blank rather than zero',
        all(value > 0 for value in coverage.values()),
    )

    min_program = _safe_int(cand['program_count'].min()) if len(cand) else None
    _check(
        checks,
        'program membership',
        f'minimum distinct program count among included rows {min_program}',
        'at least one distinct program code per included facility',
        min_program is not None and min_program >= 1,
    )
    agency_counts = cand['state_epa_flag'].value_counts(dropna=False).to_dict()
    _check(
        checks,
        'evaluation agency field',
        f'STATE_EPA_FLAG value counts {agency_counts}',
        'the lead agency field is populated for at least one included evaluation row',
        bool(cand['state_epa_flag'].notna().any()),
    )

    horizon_days = (cand['horizon_end'] - cand['evaluation_end_date']).dt.days
    unit_ok = bool((horizon_days == 365).all()) if len(cand) else False
    checks.append(
        {
            'check': '365-day outcome horizon unit and frame',
            'observed': f'horizon end minus evaluation date equals 365 days for {int((horizon_days == 365).sum())} of {len(cand)} rows; max horizon {max_horizon.date() if pd.notna(max_horizon) else None}',
            'expected': 'the label interval is (t, t plus 365 calendar days] with 365 treated as a day count, not as a calendar-year difference',
            'passed': unit_ok,
            'kind': 'unit',
            'unit': 'days',
            'frame': 'date interval strictly after the evaluation date through 365 days later, inclusive',
        }
    )

    failed = [item for item in checks if not item['passed']]
    if failed:
        raise AssertionError(('Source checks failed: ' + json.dumps(failed, default=str))[:4000])

    paths = {
        'train': output / 'public' / 'train.csv',
        'eval': output / 'public' / 'eval.csv',
        'holdout': output / 'private' / 'holdout.csv',
    }
    for name, path in paths.items():
        part = cand[cand['split'] == name].copy()
        part = part.sort_values(['evaluation_end_date', 'evaluation_id'], kind='mergesort')
        part['evaluation_end_date'] = part['evaluation_end_date'].dt.strftime('%Y-%m-%d')
        for column in TEXT_FEATURES:
            part[column] = part[column].astype('string')
        part = part[OUTPUT_COLUMNS]
        if list(part.columns) != OUTPUT_COLUMNS:
            raise AssertionError(f'Output column mismatch for {name}: {list(part.columns)}')
        part.to_csv(path, index=False, na_rep='')
    return checks

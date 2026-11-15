import csv
import math
import re
import shutil
import zipfile
from datetime import date, datetime, timedelta
from itertools import chain
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from source_io import fetch

URL = 'https://wildlife.faa.gov/assets/database_excel.zip'

FEATURES = [
    'ac_mass', 'ac_class', 'num_engs', 'type_eng', 'phase_of_flt', 'height_agl',
    'speed_kts', 'distance_nm', 'birds_struck', 'birds_seen', 'size', 'warned',
    'time_of_day', 'sky', 'precip', 'month', 'state', 'operator_class',
]
HEADER = ['index_nr', 'incident_date'] + FEATURES + ['substantial_damage']
ID_I = 0
DATE_I = 1
FEAT_OFFSET = 2
TARGET_I = len(HEADER) - 1
OPCLASS_I = FEAT_OFFSET + FEATURES.index('operator_class')
STRUCK_I = FEAT_OFFSET + FEATURES.index('birds_struck')
SEEN_I = FEAT_OFFSET + FEATURES.index('birds_seen')
PRECIP_I = FEAT_OFFSET + FEATURES.index('precip')

START_DATE = date(1990, 1, 1)
END_DATE = date(2022, 12, 31)
EVAL_START = date(2014, 1, 1)
HOLDOUT_START = date(2019, 1, 1)
HOLDOUT_END = date(2023, 1, 1)

MISSING_TOKENS = {'', 'NULL', 'NONE', 'NA', 'N/A', 'UNK', 'UNKNOWN', 'NAN'}
PRECIP_MISSING = {'', 'NULL', 'NA', 'N/A', 'UNK', 'UNKNOWN', 'NAN', 'ND'}
BAND_LABELS = ['0', '1', '2-10', '11-100', '>100']
BAND_MISSING = {'', 'NULL', 'NAN', 'NA', 'N/A', 'UNK', 'UNKNOWN', '-', 'ND', 'NONE', 'TBD'}
OP_UNKNOWN_TOKENS = {'UNK', 'UND', 'TBD', 'XXX', 'ZZZ', 'NON', 'NONE', 'NA'}

SOURCE_ALIASES = {
    'index_nr': ['INDEX_NR', 'INDEX_NO', 'INDEX', 'INDEXNUMBER', 'RECORD_ID'],
    'incident_date': ['INCIDENT_DATE', 'INCIDENTDATE', 'DATE'],
    'state': ['STATE', 'STATE_CODE', 'LOCATION_STATE'],
    'ac_class': ['AC_CLASS', 'AIRCRAFT_CLASS'],
    'ac_mass': ['AC_MASS', 'AIRCRAFT_MASS'],
    'num_engs': ['NUM_ENGS', 'NUM_ENG', 'NUMBER_ENGINES', 'ENGINES'],
    'type_eng': ['TYPE_ENG', 'ENGINE_TYPE'],
    'phase_of_flt': ['PHASE_OF_FLT', 'PHASE_OF_FLIGHT', 'PHASE'],
    'height_agl': ['HEIGHT', 'HEIGHT_AGL', 'HEIGHT_FT', 'HEIGHT_FEET'],
    'speed_kts': ['SPEED', 'SPEED_KTS', 'SPEED_KNOTS'],
    'distance_nm': ['DISTANCE', 'DIST_FROM_ARPT', 'DISTANCE_NM', 'DISTANCE_FROM_AIRPORT'],
    'birds_struck': ['NUM_STRUCK', 'BIRDS_STRUCK', 'STRUCK'],
    'birds_seen': ['NUM_SEEN', 'BIRDS_SEEN', 'SEEN'],
    'size': ['SIZE', 'SIZE_CODE'],
    'warned': ['WARNED', 'WARNING'],
    'time_of_day': ['TIME_OF_DAY', 'TIME_DAY', 'LIGHT'],
    'sky': ['SKY', 'SKY_CONDITION', 'CLOUD_COVER'],
    'precip': ['PRECIP', 'PRECIPITATION'],
    'opid': ['OPID', 'OPERATOR_ID'],
    'damage': ['DAMAGE_LEVEL', 'DAMAGE', 'DAMAGE_LVL'],
}

US_STATE_CODES = set('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split())
_STATE_NAMES = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'}
US_STATE_NAMES = {re.sub('[^A-Z]', '', k.upper()): v for k, v in _STATE_NAMES.items()}


def _norm(value):
    if value is None:
        return ''
    s = str(value).strip().upper()
    s = re.sub('[^A-Z0-9]+', '_', s).strip('_')
    return s


def _bounded(text, limit=4000):
    s = str(text)
    if len(s) <= limit:
        return s
    return s[:limit] + '... [truncated]'


def _text(value):
    if value is None:
        return ''
    if isinstance(value, float) and math.isnan(value):
        return ''
    return str(value).strip()


def _code(value):
    s = _text(value)
    if not s:
        return ''
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        s = str(int(value))
    elif re.fullmatch('[0-9]+[.]0', s):
        s = s[:-2]
    return s.upper()


def _cat(value, missing=None):
    s = _code(value)
    if not s:
        return ''
    toks = MISSING_TOKENS if missing is None else missing
    if s in toks:
        return ''
    return s


def _num(value):
    s = _text(value).replace(',', '')
    if not s:
        return None
    if s.upper() in MISSING_TOKENS:
        return None
    try:
        x = float(s)
    except ValueError:
        return None
    if not math.isfinite(x):
        return None
    return x


def _date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        v = float(value)
        if 20000 <= v <= 60000:
            return (datetime(1899, 12, 30) + timedelta(days=v)).date()
    s = _text(value)
    if not s:
        return None
    if re.fullmatch('[0-9]{8}', s):
        try:
            return datetime.strptime(s, '%Y%m%d').date()
        except ValueError:
            pass
    if re.fullmatch('[0-9]{5}', s):
        n = int(s)
        if 20000 <= n <= 60000:
            return (datetime(1899, 12, 30) + timedelta(days=n)).date()
    d = pd.to_datetime(s, errors='coerce')
    if pd.isna(d):
        return None
    return d.date()


def _id(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return ''
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return str(int(value))
    s = _text(value)
    if re.fullmatch('[0-9]+[.]0', s):
        s = s[:-2]
    return s


def _state(value):
    s = _text(value).upper()
    if not s:
        return None
    s = re.sub('[^A-Z]', '', s)
    if s in US_STATE_CODES:
        return s
    return US_STATE_NAMES.get(s)


def _operator_class(value):
    s = _code(value).replace(' ', '')
    if s in MISSING_TOKENS or s in OP_UNKNOWN_TOKENS:
        return ''
    if s in {'BUS', 'PVT', 'GOV', 'MIL'}:
        return s
    if re.fullmatch('[A-Z]{3}', s):
        return 'airline'
    return None


def _band(value):
    s = _code(value)
    if not s:
        return None
    t = re.sub('[ ]+', ' ', s.replace('\u2013', '-').replace('\u2014', '-')).strip()
    if t in BAND_MISSING:
        return None
    t2 = t.replace(' TO ', '-').replace(' THRU ', '-').replace(' THROUGH ', '-')
    t2 = re.sub(' ?- ?', '-', t2)
    if t2 in ('0', '1', '2-10', '11-100'):
        return t2
    if t2 in ('>100', '> 100', '100+', 'MORE THAN 100', 'OVER 100', 'GT 100', 'GREATER THAN 100'):
        return '>100'
    m = re.fullmatch('([0-9]+)', t2)
    if m:
        n = int(m.group(1))
        if n <= 1:
            return str(n)
        if n <= 10:
            return '2-10'
        if n <= 100:
            return '11-100'
        return '>100'
    m = re.fullmatch('([0-9]+)-([0-9]+)', t2)
    if m:
        hi = int(m.group(2))
        if hi <= 1:
            return str(hi)
        if hi <= 10:
            return '2-10'
        if hi <= 100:
            return '11-100'
        return '>100'
    return '@' + t2


def _resolve(header):
    norm_to_idx = {}
    for i, h in enumerate(header):
        n = _norm(h)
        if n and n not in norm_to_idx:
            norm_to_idx[n] = i
    cols = {}
    actual = {}
    missing = []
    for name, aliases in SOURCE_ALIASES.items():
        found = None
        for alias in aliases:
            n = _norm(alias)
            if n in norm_to_idx:
                found = norm_to_idx[n]
                break
        if found is None:
            missing.append(name)
        else:
            cols[name] = found
            actual[name] = header[found]
    return cols, actual, missing


def _summary(rows, date_idx, target_idx):
    if not rows:
        return {'rows': 0, 'positives': 0, 'min_date': None, 'max_date': None}
    dates = [r[date_idx] for r in rows]
    return {'rows': len(rows), 'positives': int(sum(r[target_idx] for r in rows)), 'min_date': min(dates).isoformat(), 'max_date': max(dates).isoformat()}


def _sort_key(record):
    s = record[ID_I]
    if re.fullmatch('[0-9]+', s):
        return (record[DATE_I], 0, int(s), s)
    return (record[DATE_I], 1, 0, s)


def _fmt(value):
    if value is None:
        return ''
    if isinstance(value, float):
        if math.isnan(value):
            return ''
        if value.is_integer():
            return str(int(value))
        return format(value, '.15g')
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def build(output, cache):
    output = Path(output)
    cache = Path(cache)
    public = output / 'public'
    private = output / 'private'
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    checks = []

    archive = Path(fetch(URL, cache, 'database_excel.zip'))
    archive_size = archive.stat().st_size
    checks.append({
        'check': 'publisher ZIP downloaded through source_io.fetch',
        'observed': {'path': str(archive), 'bytes': archive_size},
        'expected': 'nonempty ZIP archive from ' + URL,
        'passed': archive_size > 0,
    })
    if archive_size <= 0:
        raise AssertionError(_bounded('empty archive at ' + str(archive)))

    with zipfile.ZipFile(archive) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith('.xlsx') and not m.startswith('__MACOSX') and not Path(m).name.startswith('~$')]
        if not members:
            raise AssertionError(_bounded('no .xlsx member in ' + str(archive) + '; members ' + repr(zf.namelist())))
        member = max(members, key=lambda m: zf.getinfo(m).file_size)
        member_size = zf.getinfo(member).file_size
        workbook_path = cache / 'faa_wildlife_strike_source.xlsx'
        with zf.open(member) as src, open(workbook_path, 'wb') as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)

    checks.append({
        'check': 'largest XLSX workbook member selected from publisher ZIP',
        'observed': {'member': member, 'bytes': member_size},
        'expected': 'a nonempty .xlsx strike workbook inside the ZIP',
        'passed': member_size > 0,
    })
    if member_size <= 0:
        raise AssertionError(_bounded('empty workbook member ' + member))

    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        selected_sheet = None
        selected_header = None
        selected_header_pos = None
        selected_head_rows = None
        selected_it = None
        diagnostics = {}
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            it = ws.iter_rows(values_only=True)
            head_rows = []
            header = None
            header_pos = None
            for i in range(15):
                try:
                    row = next(it)
                except StopIteration:
                    break
                head_rows.append(row)
                norms = {_norm(c) for c in row if c is not None}
                if 'INCIDENT_DATE' in norms and ('DAMAGE_LEVEL' in norms or 'DAMAGE' in norms):
                    header = row
                    header_pos = i
                    break
            diagnostics[sheet_name] = {'header_found': header is not None, 'first_rows': [list(r) for r in head_rows[:2]]}
            if header is not None:
                selected_sheet = sheet_name
                selected_header = header
                selected_header_pos = header_pos
                selected_head_rows = head_rows
                selected_it = it
                break
        if selected_header is None:
            raise AssertionError(_bounded('workbook header not found; archive member ' + repr(member) + '; sheets ' + repr(wb.sheetnames) + '; diagnostics ' + repr(diagnostics)))

        cols, actual, missing = _resolve(selected_header)
        if missing:
            raise AssertionError(_bounded(
                'missing source field(s) ' + repr(missing)
                + '; archive member ' + repr(member)
                + '; sheet ' + repr(selected_sheet)
                + '; observed headers ' + repr(list(selected_header))
                + '; resolved fields ' + repr(actual)
                + '; alias candidates ' + repr({k: SOURCE_ALIASES[k] for k in missing})
            ))
        checks.append({
            'check': 'required source fields resolved from workbook header',
            'observed': {'sheet': selected_sheet, 'archive_member': member, 'resolved_fields': actual},
            'expected': 'documented FAA strike-report fields for record id, incident date, state, aircraft descriptors, encounter geometry, pilot observations, weather, operator identifier and the manager-selected damage code',
            'passed': len(missing) == 0,
        })

        idx_id = cols['index_nr']
        idx_date = cols['incident_date']
        idx_state = cols['state']
        idx_ac_class = cols['ac_class']
        idx_ac_mass = cols['ac_mass']
        idx_num_engs = cols['num_engs']
        idx_type_eng = cols['type_eng']
        idx_phase = cols['phase_of_flt']
        idx_height = cols['height_agl']
        idx_speed = cols['speed_kts']
        idx_distance = cols['distance_nm']
        idx_struck = cols['birds_struck']
        idx_seen = cols['birds_seen']
        idx_size = cols['size']
        idx_warned = cols['warned']
        idx_tod = cols['time_of_day']
        idx_sky = cols['sky']
        idx_precip = cols['precip']
        idx_opid = cols['opid']
        idx_damage = cols['damage']

        def val(row, i):
            return row[i] if i < len(row) else None

        allowed = {'N': 0, 'M': 0, 'M?': 0, 'S': 1, 'D': 1}
        damage_counts = {}
        base_counts = {'invalid_date': 0, 'outside_date': 0, 'outside_state': 0, 'no_aircraft': 0, 'blank_damage': 0}
        unexpected_in_pop = {}
        unexpected_samples = {}
        missing_id_count = 0
        missing_id_samples = []
        unrecognized_opid_count = 0
        unrecognized_opid_samples = []
        band_token_counts = {'birds_struck': {}, 'birds_seen': {}}
        band_token_overflow = {'birds_struck': 0, 'birds_seen': 0}
        band_missing_tokens = {'birds_struck': {}, 'birds_seen': {}}
        band_unexpected = {}
        band_unexpected_samples = {}
        none_audit = {'precip': 0, 'sky': 0, 'time_of_day': 0, 'warned': 0, 'size': 0}
        records = []

        def note_band_token(col, raw):
            tok = _code(raw) or '(blank)'
            d = band_token_counts[col]
            if tok in d:
                d[tok] = d[tok] + 1
            elif len(d) < 40:
                d[tok] = 1
            else:
                band_token_overflow[col] = band_token_overflow[col] + 1
            return tok

        data_iter = chain(selected_head_rows[selected_header_pos + 1:], selected_it)
        for row in data_iter:
            if row is None:
                continue
            raw_id = _id(val(row, idx_id))
            dt = _date(val(row, idx_date))
            dkey = re.sub('[^A-Z0-9?]', '', _code(val(row, idx_damage)))
            if not dkey:
                dkey = '__blank__'
            damage_counts[dkey] = damage_counts.get(dkey, 0) + 1
            if dt is None:
                base_counts['invalid_date'] += 1
                continue
            if dt < START_DATE or dt > END_DATE:
                base_counts['outside_date'] += 1
                continue
            state = _state(val(row, idx_state))
            if state is None:
                base_counts['outside_state'] += 1
                continue
            ac_class = _cat(val(row, idx_ac_class))
            ac_mass = _cat(val(row, idx_ac_mass))
            if not ac_class and not ac_mass:
                base_counts['no_aircraft'] += 1
                continue
            if dkey == '__blank__':
                base_counts['blank_damage'] += 1
                continue
            if dkey not in allowed:
                unexpected_in_pop[dkey] = unexpected_in_pop.get(dkey, 0) + 1
                samples = unexpected_samples.setdefault(dkey, [])
                if len(samples) < 5:
                    samples.append(raw_id)
                continue
            if not raw_id:
                missing_id_count += 1
                if len(missing_id_samples) < 5:
                    missing_id_samples.append({'incident_date': dt.isoformat(), 'state': state, 'damage_code': dkey})
                continue
            op_class = _operator_class(val(row, idx_opid))
            if op_class is None:
                unrecognized_opid_count += 1
                if len(unrecognized_opid_samples) < 10:
                    unrecognized_opid_samples.append({'index_nr': raw_id, 'opid': _text(val(row, idx_opid))})
                op_class = ''
            bands = {}
            for col, idx_band in (('birds_struck', idx_struck), ('birds_seen', idx_seen)):
                raw_band = val(row, idx_band)
                b = _band(raw_band)
                tok = note_band_token(col, raw_band)
                if b is not None and b.startswith('@'):
                    band_unexpected[tok] = band_unexpected.get(tok, 0) + 1
                    smp = band_unexpected_samples.setdefault(tok, [])
                    if len(smp) < 5:
                        smp.append(raw_id)
                    b = None
                elif b is None and tok in BAND_MISSING:
                    band_missing_tokens[col][tok] = band_missing_tokens[col].get(tok, 0) + 1
                bands[col] = b
            size_v = _cat(val(row, idx_size))
            warned_v = _cat(val(row, idx_warned))
            tod_v = _cat(val(row, idx_tod))
            sky_v = _cat(val(row, idx_sky))
            precip_raw = _code(val(row, idx_precip))
            precip_v = '' if (not precip_raw or precip_raw in PRECIP_MISSING) else precip_raw
            for key, raw_tok in (
                ('precip', precip_raw),
                ('sky', _code(val(row, idx_sky))),
                ('time_of_day', _code(val(row, idx_tod))),
                ('warned', _code(val(row, idx_warned))),
                ('size', _code(val(row, idx_size))),
            ):
                if raw_tok == 'NONE':
                    none_audit[key] = none_audit[key] + 1
            records.append((
                raw_id, dt,
                ac_mass, ac_class, _num(val(row, idx_num_engs)), _cat(val(row, idx_type_eng)),
                _cat(val(row, idx_phase)), _num(val(row, idx_height)), _num(val(row, idx_speed)),
                _num(val(row, idx_distance)), bands['birds_struck'], bands['birds_seen'],
                size_v, warned_v, tod_v, sky_v, precip_v, dt.month, state, op_class,
                allowed[dkey],
            ))

        unexpected_all = {k: v for k, v in damage_counts.items() if k not in allowed and k != '__blank__'}
        damage_passed = not unexpected_in_pop
        checks.append({
            'check': 'DAMAGE code coverage and blank exclusion',
            'observed': {'all_codes': dict(sorted(damage_counts.items())), 'blank_damage_rows_in_base_population': base_counts['blank_damage'], 'unexpected_codes_outside_population': unexpected_all},
            'expected': 'allowed label codes N, M, M-question, S and D; blank DAMAGE dropped and never labelled 0; a nonblank code outside the allowed set is recorded when it sits outside the frozen population and fails construction when it sits inside it',
            'passed': damage_passed,
        })
        if not damage_passed:
            raise AssertionError(_bounded('unexpected DAMAGE code(s) in frozen population: ' + repr(unexpected_in_pop) + '; samples ' + repr(unexpected_samples) + '; all damage counts ' + repr(damage_counts) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        pop_passed = len(records) > 0
        checks.append({
            'check': 'frozen population filters applied',
            'observed': {'included_rows': len(records), 'excluded_counts': base_counts},
            'expected': 'incident_date from 1990-01-01 through 2022-12-31; state in the 50 U.S. states or DC; at least one of ac_class or ac_mass present; allowed DAMAGE code; nonempty INDEX_NR',
            'passed': pop_passed,
        })
        if not pop_passed:
            raise AssertionError(_bounded('no rows survived frozen population filters; excluded ' + repr(base_counts) + '; damage codes ' + repr(damage_counts) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        id_passed = missing_id_count == 0
        checks.append({
            'check': 'stable index_nr present for every included row',
            'observed': {'missing_id_count': missing_id_count, 'samples': missing_id_samples},
            'expected': 'nonempty INDEX_NR on every included source row',
            'passed': id_passed,
        })
        if not id_passed:
            raise AssertionError(_bounded('missing INDEX_NR in included rows: count ' + str(missing_id_count) + '; samples ' + repr(missing_id_samples) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        seen_ids = set()
        duplicate_samples = []
        duplicate_count = 0
        for r in records:
            ident = r[ID_I]
            if ident in seen_ids:
                duplicate_count += 1
                if len(duplicate_samples) < 5:
                    duplicate_samples.append(ident)
            else:
                seen_ids.add(ident)
        duplicate_passed = duplicate_count == 0
        checks.append({
            'check': 'included INDEX_NR values are unique',
            'observed': {'duplicate_count': duplicate_count, 'samples': duplicate_samples},
            'expected': 'zero duplicate stable IDs across train, eval and holdout',
            'passed': duplicate_passed,
        })
        if not duplicate_passed:
            raise AssertionError(_bounded('duplicate INDEX_NR values: count ' + str(duplicate_count) + '; samples ' + repr(duplicate_samples) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        op_values = {r[OPCLASS_I] for r in records}
        allowed_op = {'', 'airline', 'BUS', 'PVT', 'GOV', 'MIL'}
        stray_op = sorted(v for v in op_values if v not in allowed_op)
        checks.append({
            'check': 'OPID tokens outside documented operator categories are left missing',
            'observed': {'unrecognized_opid_rows': unrecognized_opid_count, 'samples': unrecognized_opid_samples, 'distinct_operator_class_values': sorted(op_values), 'stray_values': stray_op},
            'expected': 'operator_class limited to airline for a three-letter operator code, BUS, PVT, GOV, MIL, or blank; a token matching no documented category receives no class value instead of a guessed one',
            'passed': not stray_op,
        })
        if stray_op:
            raise AssertionError(_bounded('stray operator_class values: ' + repr(stray_op) + '; samples ' + repr(unrecognized_opid_samples) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        band_dist = {'birds_struck': {}, 'birds_seen': {}}
        for r in records:
            for col, k in (('birds_struck', STRUCK_I), ('birds_seen', SEEN_I)):
                v = r[k]
                key = v if v else '(missing)'
                d = band_dist[col]
                d[key] = d.get(key, 0) + 1
        band_passed = not band_unexpected
        checks.append({
            'check': 'NUM_STRUCK and NUM_SEEN encoded as the published ordinal animal-number bands',
            'kind': 'unit',
            'observed': {
                'birds_struck_values': dict(sorted(band_dist['birds_struck'].items())),
                'birds_seen_values': dict(sorted(band_dist['birds_seen'].items())),
                'raw_tokens_birds_struck': dict(sorted(band_token_counts['birds_struck'].items())),
                'raw_tokens_birds_seen': dict(sorted(band_token_counts['birds_seen'].items())),
                'tokens_beyond_first_40_distinct': band_token_overflow,
                'tokens_treated_as_missing': {k: dict(sorted(v.items())) for k, v in band_missing_tokens.items()},
                'unexpected_tokens_in_population': band_unexpected,
                'unexpected_samples': band_unexpected_samples,
            },
            'expected': 'the strike report asks for animal numbers in the bands 1, 2-10, 11-100 and more than 100, so NUM_STRUCK and NUM_SEEN are ordinal category fields rather than counts; emitted values are the band labels plus a zero band and a single-animal band, a raw integer is folded into the band that contains it, a blank stays missing and is never zero, and any other nonblank token inside the frozen population fails construction',
            'passed': band_passed,
        })
        if not band_passed:
            raise AssertionError(_bounded('unexpected animal-number band token(s) inside the frozen population: ' + repr(band_unexpected) + '; samples ' + repr(band_unexpected_samples) + '; raw token counts ' + repr(band_token_counts) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        precip_values = {}
        for r in records:
            v = r[PRECIP_I]
            key = v if v else '(missing)'
            precip_values[key] = precip_values.get(key, 0) + 1
        none_count = precip_values.get('NONE', 0)
        precip_passed = none_count > 0
        top_precip = dict(sorted(precip_values.items(), key=lambda kv: (-kv[1], kv[0]))[:12])
        checks.append({
            'check': 'PRECIPITATION no-precipitation category retained as a value',
            'observed': {'top_values': top_precip, 'distinct_values': len(precip_values), 'no_precipitation_rows': none_count, 'raw_none_tokens_by_field': dict(sorted(none_audit.items()))},
            'expected': 'the strike report lists None alongside Fog, Rain and Snow for precipitation, so the NONE code is the documented no-precipitation category and must be emitted as a value rather than folded into missing; only a blank field stays missing, and NONE seen in other coded fields is counted for audit',
            'passed': precip_passed,
        })
        if not precip_passed:
            raise AssertionError(_bounded('precipitation NONE category absent from the constructed rows; observed values ' + repr(top_precip) + '; raw NONE tokens by field ' + repr(none_audit) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        coverage = {}
        for j, name in enumerate(FEATURES):
            k = FEAT_OFFSET + j
            n = 0
            for r in records:
                v = r[k]
                if v is None:
                    continue
                if isinstance(v, str) and not v:
                    continue
                n += 1
            coverage[name] = n
        empty_features = [f for f in FEATURES if coverage[f] == 0]
        coverage_passed = not empty_features
        checks.append({
            'check': 'every declared feature has nonempty constructed coverage',
            'observed': coverage,
            'expected': 'each declared feature column has at least one nonmissing value; missing values stay missing and are never zero-filled',
            'passed': coverage_passed,
        })
        if not coverage_passed:
            raise AssertionError(_bounded('declared feature(s) empty after parsing: ' + repr(empty_features) + '; coverage ' + repr(coverage) + '; archive member ' + repr(member) + '; observed headers ' + repr(list(selected_header))))

        train = [r for r in records if r[DATE_I] < EVAL_START]
        eval_rows = [r for r in records if EVAL_START <= r[DATE_I] < HOLDOUT_START]
        holdout = [r for r in records if HOLDOUT_START <= r[DATE_I] < HOLDOUT_END]
        assigned = len(train) + len(eval_rows) + len(holdout)
        split_summary = {
            'train': _summary(train, DATE_I, TARGET_I),
            'eval': _summary(eval_rows, DATE_I, TARGET_I),
            'holdout': _summary(holdout, DATE_I, TARGET_I),
        }
        split_passed = assigned == len(records) and all(len(rows) > 0 and _summary(rows, DATE_I, TARGET_I)['positives'] > 0 for rows in [train, eval_rows, holdout])
        checks.append({
            'check': 'fixed half-open chronological splits contain rows and positives',
            'observed': split_summary,
            'expected': 'train 1990-01-01 to 2013-12-31; eval 2014-01-01 to 2018-12-31; holdout 2019-01-01 to 2022-12-31; each split nonempty with at least one positive',
            'passed': split_passed,
        })
        if not split_passed:
            raise AssertionError(_bounded('split integrity failure: ' + repr(split_summary) + '; assigned ' + str(assigned) + ' of ' + str(len(records)) + '; archive member ' + repr(member)))

        outputs = {
            'train': (public / 'train.csv', train),
            'eval': (public / 'eval.csv', eval_rows),
            'holdout': (private / 'holdout.csv', holdout),
        }
        for label, (path, rows) in outputs.items():
            with open(path, 'w', newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh, lineterminator=chr(10))
                writer.writerow(HEADER)
                for r in sorted(rows, key=_sort_key):
                    writer.writerow([_fmt(r[ID_I]), _fmt(r[DATE_I])] + [_fmt(r[FEAT_OFFSET + j]) for j in range(len(FEATURES))] + [_fmt(r[TARGET_I])])

        observed_headers = {}
        observed_counts = {}
        for label, (path, rows) in outputs.items():
            with open(path, newline='', encoding='utf-8') as fh:
                reader = csv.reader(fh)
                observed_headers[label] = next(reader)
                observed_counts[label] = sum(1 for _ in reader)
        expected_counts = {label: len(rows) for label, (path, rows) in outputs.items()}
        output_passed = all(observed_headers[label] == HEADER for label in outputs) and observed_counts == expected_counts
        checks.append({
            'check': 'written CSV headers and row counts match the frozen schema',
            'observed': {'headers': observed_headers, 'row_counts': observed_counts},
            'expected': {'headers': HEADER, 'row_counts': expected_counts},
            'passed': output_passed,
        })
        if not output_passed:
            raise AssertionError(_bounded('written CSV mismatch: observed headers ' + repr(observed_headers) + '; expected headers ' + repr(HEADER) + '; observed counts ' + repr(observed_counts) + '; expected counts ' + repr(expected_counts)))
    finally:
        wb.close()

    if not all(c.get('passed') for c in checks):
        bad = [c for c in checks if not c.get('passed')]
        raise AssertionError(_bounded('failed checks: ' + repr(bad)))
    return checks

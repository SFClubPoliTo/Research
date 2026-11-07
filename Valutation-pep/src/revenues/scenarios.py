"""D05 adapter: validated workbook values, no Excel engine or G3 fallback."""
import argparse
from copy import deepcopy
import csv
import hashlib
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import yaml

from src.fcff.model import build_params, fcff

ROOT = Path(__file__).resolve().parents[2]
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ROWS = {'bear': 16, 'base': 22, 'growth': 28}


def read_scenarios(path):
    """Read this delivery's numeric cells and independently check cached results.

    This is a fixed-layout adapter, not a general Excel formula evaluator.
    Shared formulas are accepted only through numerically verified caches.
    """
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        strings = [''.join(item.itertext()) for item in
                   ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in
                ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        sheets = {}
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).find('s:sheets', NS):
            rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = rels[rid]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            sheets[sheet.attrib['name']] = {
                c.attrib['r']: c for c in ET.fromstring(archive.read(target)).findall('.//s:sheetData/s:row/s:c', NS)}

    def number(sheet, address, allow_text=False):
        try:
            cell = sheets[sheet][address]
            if cell.get('t') not in (None, 'n') and not (allow_text and cell.get('t') == 's'):
                raise ValueError('not numeric')
            raw = cell.find('s:v', NS).text
            value = float(strings[int(raw)] if cell.get('t') == 's' else raw)
            if not np.isfinite(value):
                raise ValueError('not finite')
            return value
        except (KeyError, AttributeError, TypeError, ValueError) as exc:
            raise ValueError(f'D05 missing/invalid cached number: {sheet}!{address}') from exc

    def check(actual, expected, label):
        if not np.allclose(actual, expected, rtol=1e-10, atol=1e-11):
            raise ValueError(f'D05 inconsistent values: {label}; recalculate/check the workbook')

    years = [number('Scenari', f'{c}11', allow_text=True) for c in 'DEFGHIJKLM']
    if years != list(range(2026, 2036)):
        raise ValueError('D05 requires FY2026-FY2035')
    r0, terminal = number('Scenari', 'B4'), number('Scenari', 'B5')
    method, k = number('Scenari', 'B6'), number('Scenari', 'B7')
    if r0 <= 0 or not 0 < terminal < 1 or method not in (1, 2) or not 0 <= k <= 1:
        raise ValueError('D05 invalid base, maturity or convergence controls')
    weight = number('Ipotesi', 'B31')
    if not 0 <= weight <= 1:
        raise ValueError('D05 invalid macro weight')
    scenarios = {}
    for (name, row), hypothesis_column in zip(ROWS.items(), 'BCD'):
        initial = number('Ipotesi', hypothesis_column + '32')
        check(initial, weight * number('Ipotesi', hypothesis_column + '23') +
              (1-weight) * number('Ipotesi', hypothesis_column + '18'), name + ' triangulation')
        organic = [initial] * 5
        for _ in range(5):
            organic.append(organic[-1] + ((terminal-initial)/6 if method == 1 else k*(terminal-organic[-1])))
        adjustment = [number('Scenari', f'{c}{row-1}') for c in 'DEFGHIJKLM']
        check(adjustment, [number('Scenari', 'B8') + number('Scenari', 'B9')] + [0.]*9, name + ' FX/M&A')
        check([number('Scenari', f'{c}{row-2}') for c in 'DEFGHIJKLM'], organic, name + ' convergence')
        growth = np.array([number('Scenari', f'{c}{row}') for c in 'DEFGHIJKLM'])
        check(growth, np.array(organic)+adjustment, name + ' reported growth')
        if np.any(growth <= -1):
            raise ValueError('D05 growth must exceed -1')
        revenues = np.array([number('Scenari', f'{c}{row+1}') for c in 'DEFGHIJKLM'])
        check(revenues, r0*np.cumprod(1+growth), name + ' revenue reference')
        check(number('Scenari', f'C{row+1}'), r0, name + ' base')
        check(number('Scenari', f'N{row}'), terminal, name + ' maturity')
        check(number('Scenari', f'N{row+1}'), revenues[-1]*(1+terminal), name + ' terminal revenue')
        scenarios[name] = {'g_path': growth.tolist(), 'expected_revenues': revenues.tolist(),
                           'range': f'Scenari!D{row}:M{row}'}
    if not np.all(np.array(scenarios['bear']['g_path']) <= scenarios['base']['g_path']) or not np.all(
            np.array(scenarios['base']['g_path']) <= scenarios['growth']['g_path']):
        raise ValueError('D05 scenario ordering is invalid')
    return {'r0': r0, 'g_terminal': terminal, 'years': list(range(2026, 2036)),
            'method': int(method), 'k': k, 'scenarios': scenarios,
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def prepare_scenario(cfg, scenario=None, is_final_run=False):
    """Return a private effective config; preserve the delivered D07 baseline."""
    cfg = deepcopy(cfg)
    spec = cfg['revenues'].get('d05')
    if spec is None:
        if scenario is not None:
            raise ValueError('Scenario selection requires revenues.d05')
        return cfg, None
    if is_final_run and spec.get('status') != 'real':
        raise RuntimeError('Pipeline block: D05 date/source review is still provisional')
    name = spec['scenario'] if scenario is None else scenario
    if name not in ROWS:
        raise ValueError('D05 scenario must be bear, base or growth')
    delivery = read_scenarios(ROOT / spec['source'])
    if not np.isclose(delivery['r0'], cfg['revenues']['r0'], rtol=0, atol=1e-9):
        raise ValueError('D05 base revenue disagrees with shared config/D04')
    terminal = cfg['rates_and_terminal']
    if not np.isclose(delivery['g_terminal'], terminal['g_terminal'], rtol=0, atol=1e-12):
        raise ValueError('D05 maturity requires alignment with G3 g_terminal')
    growth = delivery['scenarios'][name]['g_path']
    params = cfg['fcff_parameters']
    # Validate all delivered vectors before deriving anything; do not fill missing G2 inputs.
    fcff(np.full((1, 10), delivery['r0']), delivery['r0'], params)
    assumptions = {'status': params['status'], 'ricavo_base': delivery['r0'], 'growth': growth[:5],
                   'm_growth': params['margine'][:5], 'tau_growth': params['aliquota'][:5],
                   'm_inf': terminal['margin_terminal'], 'tau_inf': terminal['tax_terminal'],
                   'g_inf': terminal['g_terminal'], 'roic_inf': terminal['roic_terminal'],
                   **{key: params[key] for key in ('da', 'capex', 'nwc')}}
    # Use G2's own option-A builder. Preserve margins/taxes exactly as delivered.
    params['reinv_rate'] = build_params(assumptions)['reinv_rate'].tolist()
    cfg['revenues']['g_path'] = growth
    info = {key: delivery[key] for key in ('source_sha256', 'years', 'method', 'k')}
    info.update(scenario=name, source=spec['source'], status=spec['status'],
                g_path=growth, g_terminal=delivery['g_terminal'],
                reinv_rate=params['reinv_rate'], range=delivery['scenarios'][name]['range'])
    return cfg, info


def main():
    parser = argparse.ArgumentParser(description='D05 deterministic revenue/FCFF references; no G3 valuation')
    parser.add_argument('--config', default='config/config.yaml')
    parser.add_argument('--output', default='output/d05_reference.csv')
    args = parser.parse_args()
    cfg = yaml.safe_load((ROOT / args.config).read_text(encoding='utf-8'))
    dest = ROOT / args.output
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['scenario', 'year', 'growth', 'revenues', 'nopat', 'reinvest', 'fcff'])
        for name in ROWS:
            effective, _ = prepare_scenario(cfg, name)
            g = np.array(effective['revenues']['g_path'])
            r0 = effective['revenues']['r0']
            r = r0 * np.cumprod(1+g)
            nopat, reinvest, flows = fcff(r[None, :], r0, effective['fcff_parameters'])
            for i in range(10):
                writer.writerow([name, 2026+i, g[i], r[i], nopat[0,i], reinvest[0,i], flows[0,i]])
    print(f'D05 reference: {dest}')


if __name__ == '__main__':
    main()

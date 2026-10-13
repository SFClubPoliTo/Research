"""Bounded quotes from a common time/state surface, with explicit provenance."""
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from layout import DATA, OUTPUTS

BASE = np.log1p(.2 / 1.15) / .2


class Policy:
    def __init__(self, csv_path=None):
        source = Path(csv_path) if csv_path else OUTPUTS / 'hft3/baseline_audit/temporal_policy.csv'
        cache = DATA / 'processed/policy_5sd_241.npz'
        fingerprint = hashlib.sha256(source.read_bytes()).hexdigest()
        valid = False
        if cache.exists() and csv_path is None:
            with np.load(cache, allow_pickle=False) as stored:
                valid = str(stored['source_sha256']) == fingerprint
                if valid:
                    self.times = stored['times'].copy()
                    self.y = stored['y'].copy()
                    self.value = stored['value'].copy()
        if not valid:
            d = pd.read_csv(source, float_precision='round_trip')
            d = d[(d.domain_sd == 5) & (d.points == 241)]
            self.times = np.sort(d.t.unique())
            self.y = np.sort(d.y.unique())
            ordered = d.sort_values(['t', 'q', 'y'])
            self.value = ordered.theta.to_numpy().reshape(len(self.times), 13, len(self.y))
            if csv_path is None:
                cache.parent.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(cache, times=self.times, y=self.y, value=self.value, source_sha256=fingerprint)
        self.clamps = 0
        self.source_sha256 = fingerprint

    def values(self, t, q, y, *, count_clamps=True):
        t, q, y = np.broadcast_arrays(t, q, y)
        if np.any((t < 0) | (t > 1) | (np.abs(q) > 6)) or not np.all(q == np.floor(q)):
            raise ValueError('Time/inventory outside policy domain')
        if not np.all(np.isfinite(y)):
            raise ValueError('Nonfinite policy state')
        if count_clamps:
            self.clamps += int(np.count_nonzero((y < self.y[0]) | (y > self.y[-1])))
        y = np.clip(y, self.y[0], self.y[-1])
        k = np.clip(np.searchsorted(self.times, t) - 1, 0, len(self.times)-2)
        w = (t-self.times[k])/(self.times[k+1]-self.times[k])
        j = np.clip(np.searchsorted(self.y, y)-1, 0, len(self.y)-2)
        a = (y-self.y[j])/(self.y[j+1]-self.y[j])
        qi = q.astype(int) + 6
        return (1-w)*((1-a)*self.value[k, qi, j]+a*self.value[k, qi, j+1]) + w*((1-a)*self.value[k+1, qi, j]+a*self.value[k+1, qi, j+1])

    def offsets(self, t, q, y, cross_shift=0.):
        q = np.asarray(q)
        v = self.values(t, q, y)
        bid = np.clip(BASE-self.values(t, np.minimum(q+1, 6), y, count_clamps=False)+v+cross_shift, .02, 4)
        ask = np.clip(BASE-self.values(t, np.maximum(q-1, -6), y, count_clamps=False)+v-cross_shift, .02, 4)
        return np.where(q < 6, bid, np.nan), np.where(q > -6, ask, np.nan)

"""How much ECG information does the PPG carry? (Track 1.5 information-transfer analysis)

  beats.py       pair ECG and PPG beats, block templates, ECG delineation, PPG pulse features
  agreement.py   method 4: PRV vs HRV (Bland-Altman, ICC), pulse-arrival-time jitter
  coherence.py   method 1: magnitude-squared coherence, linear (Wiener) predictability, beat-region R^2
  infotheory.py  method 2: KSG mutual information, conditional MI, transfer entropy (+ surrogates)
  probes.py      method 5: per-feature ML probes, rate-only vs PPG, noise ceilings, information bounds
  forward.py     method 3: electro-mechano-optical forward model + Fisher information / Cramer-Rao bounds
"""

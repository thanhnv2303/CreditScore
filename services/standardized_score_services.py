import numpy as np
from scipy.stats.stats import _contains_nan


def get_standardized_score_info(a, axis=0, ddof=0, nan_policy='propagate'):
    a = np.asanyarray(a)

    contains_nan, nan_policy = _contains_nan(a, nan_policy)

    if contains_nan and nan_policy == 'omit':
        mns = np.nanmean(a=a, axis=axis, keepdims=True)
        sstd = np.nanstd(a=a, axis=axis, ddof=ddof, keepdims=True)
    else:
        mns = a.mean(axis=axis, keepdims=True)
        sstd = a.std(axis=axis, ddof=ddof, keepdims=True)

    return mns[0], sstd[0]

### example
# data = np.array([6, 7, 7, 12.21, 13, 13, 15.123, 16, 19, 22])
#
# mns, sstd = get_standardized_score_info(a=data)
#
# zscore = stats.zscore(data)
# print(zscore)
# print(mns)
# print(sstd)
# print(str((6 - mns) / sstd))

### dict to list value

# dictttt= {
#     "a":1,
#     "b":2.5,
#     "c":3
# }
# lst = list(dictttt.values())
# print(lst)
"""Multi-asset covariance proxy, not a fitted full-HJB residual correction."""
import numpy as np


def psd_factor(matrix):
    if not np.allclose(matrix, matrix.T, atol=1e-14):
        raise ValueError('Covariance must be symmetric')
    eig, vec = np.linalg.eigh(matrix)
    if eig.min() < -1e-12*max(float(eig.max()), 1e-30):
        raise ValueError('Covariance is not positive semidefinite')
    factor = vec @ np.diag(np.sqrt(np.maximum(eig, 0)))
    return factor


def covariance(sigma, correlation):
    return sigma[..., :, None]*correlation*sigma[..., None, :]


def portfolio_variance(q, cov):
    return np.einsum('...i,...ij,...j->...', q, cov, q)


def cross_matrix(cov):
    return cov*(1-np.eye(cov.shape[-1]))


def correction(t, q, cov, gamma=.2):
    # Frozen covariance approximation to the omitted integrated cross-risk.
    return -.5*gamma*(1-t)*portfolio_variance(q, cross_matrix(cov))


def shifts(t, q, cov, gamma=.2):
    # delta_bid += shift, delta_ask -= shift, then apply bounds.
    return gamma*(1-t)*np.einsum('...ij,...j->...i', cross_matrix(cov), q)


def self_test():
    corr = np.array([[1., .7], [.7, 1.]])
    cov = covariance(np.array([1.1, 1.3]), corr)
    q = np.array([3., 0.])
    s = shifts(.25, q, cov)
    assert s[1] > 0 and s[0] == 0
    for i in range(2):
        unit = np.eye(2)[i]
        assert np.isclose(correction(.25, q+unit, cov)-correction(.25, q, cov), -s[i])
        assert np.isclose(correction(.25, q-unit, cov)-correction(.25, q, cov), s[i])
    assert correction(1, q, cov) == 0
    assert np.all(shifts(.25, q, np.diag(np.diag(cov))) == 0)
    assert shifts(.25, q, covariance(np.array([1.1, 1.3]), np.array([[1., -.7], [-.7, 1.]])))[1] < 0
    assert portfolio_variance(q-np.array([0., 1.]), cov) < portfolio_variance(q, cov)
    # A finite unit trade can increase risk after the hedge is already large.
    q = np.array([3., -6.])
    assert portfolio_variance(q-np.array([0., 1.]), cov) > portfolio_variance(q, cov)
    assert np.allclose(psd_factor(cov)@psd_factor(cov).T, cov)
    try:
        psd_factor(np.array([[1., 2.], [2., 1.]]))
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid covariance accepted')
    return 'PASS cross-gains, terminal, zero/negative correlation, finite-trade risk and PSD'

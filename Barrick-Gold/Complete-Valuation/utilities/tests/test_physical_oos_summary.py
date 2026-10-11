import pytest
from barrick_unified.physical_oos_summary import summarize_matched_origins


def row(origin='2026-07-10',target_date='2026-07-13',prediction=101.,target=102.):
    return dict(origin=origin,target_date=target_date,predictive_mean=prediction,target=target,
                no_change_error=100.-target,predictive_quantiles=[90.,95.,100.,105.,110.],
                p_optimizer_success=False)


def test_common_support_preserves_failed_optimizer_and_excludes_unmatched_dates():
    result=summarize_matched_origins({'a':[row(),row('2026-07-13','2026-07-14',1000.)],
                                      'b':[row(prediction=103.)]})
    assert result['common_targets']==1
    assert result['models']['a']['rmse']==1
    assert result['models']['a']['unmatched']==1
    assert result['models']['a']['p_optimizer_failures']==1
    assert result['models']['a']['mean_squared_loss_difference_vs_no_change']==-3


def test_mismatched_targets_or_duplicate_origins_are_rejected():
    with pytest.raises(ValueError,match='target values'):
        summarize_matched_origins({'a':[row()],'b':[row(target=103.)]})
    with pytest.raises(ValueError,match='unique'):
        summarize_matched_origins({'a':[row(),row()]})


def test_future_training_is_rejected():
    bad=row();bad['training_last']='2026-07-11'
    with pytest.raises(ValueError,match='training'):
        summarize_matched_origins({'a':[bad]})

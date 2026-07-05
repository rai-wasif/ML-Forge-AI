# ROC-AUC

ROC-AUC measures how well a classifier ranks positive examples above negative examples across thresholds.
It is useful when probabilities matter and when class balance is imperfect.

For binary classification, a ROC-AUC of 0.5 is random ranking and 1.0 is perfect ranking.
Accuracy can be misleading on imbalanced data, so ROC-AUC should be reviewed with precision, recall, and F1.

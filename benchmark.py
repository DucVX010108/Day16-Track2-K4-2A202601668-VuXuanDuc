import time
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score
import lightgbm as lgb

# 1. Đo thời gian nạp dữ liệu
t0 = time.time()
df = pd.read_csv('creditcard.csv')
load_time = time.time() - t0

# 2. Tiền xử lý & Phân chia tập train/test
X = df.drop(columns=['Class', 'Time'])
y = df['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

# 3. Cấu hình & Huấn luyện mô hình
params = {
    'objective': 'binary',
    'metric': 'auc',
    'boosting_type': 'gbdt',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'verbose': -1,
    'n_jobs': -1
}

t_train_start = time.time()
gbm = lgb.train(
    params,
    train_data,
    num_boost_round=500,
    valid_sets=[test_data],
    callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
)
train_time = time.time() - t_train_start
best_iteration = gbm.best_iteration

# 4. Đánh giá chất lượng mô hình
y_pred_prob = gbm.predict(X_test, num_iteration=best_iteration)
y_pred_class = (y_pred_prob >= 0.5).astype(int)

auc = float(roc_auc_score(y_test, y_pred_prob))
acc = float(accuracy_score(y_test, y_pred_class))
f1 = float(f1_score(y_test, y_pred_class))
prec = float(precision_score(y_test, y_pred_class))
rec = float(recall_score(y_test, y_pred_class))

# 5. Đo độ trễ suy luận đơn bản ghi (Latency 1 row)
sample_1 = X_test.iloc[[0]]
latencies = []
for _ in range(100):
    t_start = time.perf_counter()
    _ = gbm.predict(sample_1, num_iteration=best_iteration)
    latencies.append((time.perf_counter() - t_start) * 1000)
latency_1_row = float(np.mean(latencies))

# 6. Đo thông lượng hàng loạt (Throughput batch 1000 rows)
sample_1000 = X_test.iloc[:1000]
t_tp_start = time.perf_counter()
_ = gbm.predict(sample_1000, num_iteration=best_iteration)
throughput_time = time.perf_counter() - t_tp_start
throughput_qps = float(1000.0 / throughput_time)

# 7. Xuất kết quả
results = {
    "load_data_time_sec": round(load_time, 4),
    "train_time_sec": round(train_time, 4),
    "best_iteration": int(best_iteration),
    "auc_roc": round(auc, 4),
    "accuracy": round(acc, 6),
    "f1_score": round(f1, 4),
    "precision": round(prec, 4),
    "recall": round(rec, 4),
    "latency_1_row_ms": round(latency_1_row, 4),
    "throughput_1000_rows_qps": round(throughput_qps, 2)
}

print(json.dumps(results, indent=4))
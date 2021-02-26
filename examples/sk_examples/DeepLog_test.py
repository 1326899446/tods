import numpy as np
from tods.tods_skinterface.primitiveSKI.detection_algorithm.DeepLog_skinterface import DeepLogSKI
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

#prepare the data
data = np.loadtxt("./500_UCR_Anomaly_robotDOG1_10000_19280_19360.txt")

X_train = np.expand_dims(data[:10000], axis=1)
X_test = np.expand_dims(data[10000:], axis=1)

transformer = DeepLogSKI()
transformer.fit(X_train)

prediction_labels_train = transformer.predict(X_train)

prediction_labels = transformer.predict(X_test)
prediction_score = transformer.predict_score(X_test)

print("Primitive: ", transformer.primitive)
print("Prediction Labels\n", prediction_labels)
print("Prediction Score\n", prediction_score)

# y_true = prediction_labels_train[:1000]
# y_pred = prediction_labels[:1000]
y_true = prediction_labels_train
y_pred = prediction_labels

print('Accuracy Score: ', accuracy_score(y_true, y_pred))

confusion_matrix(y_true, y_pred)

print(classification_report(y_true, y_pred))

precision, recall, thresholds = precision_recall_curve(y_true, y_pred)
f1_scores = 2*recall*precision/(recall+precision)

print('Best threshold: ', thresholds[np.argmax(f1_scores)])
print('Best F1-Score: ', np.max(f1_scores))
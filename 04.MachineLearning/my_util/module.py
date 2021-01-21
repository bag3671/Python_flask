from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import numpy as np


def pca_accuracy(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.3, random_state=2021
)
    dtc = DecisionTreeClassifier(random_state=2021)
    dtc.fit(X_train, y_train)
    pred = dtc.predict(X_test)
    acc = accuracy_score(y_test, pred)
    return np.round(acc, 4)
def draw_compare(df,filename):
    fig, axs = plt.subplots(figsize=(12,4),ncols=2,nrows=1)
    columns = ['target','cluster']
    markers = ['^',"s",'o']
    for k, column in enumerate(columns):
        ax = axs[k]
        for i, marker in enumerate(markers):
            x_axis_data = df[df[column]==i]['pca_x']
            y_axis_data = df[df[column]==i]['pca_y']
            ax.scatter(x_axis_data, y_axis_data, marker=marker,label=wine.target_names[i])
        if k == 0:
            ax.set_title('Original Data')
            ax.set_ylabel('PCA Component 2')
            ax.legend()
        else:
            ax.set_title('Clustered Data')
        ax.set_xlabel('PCA Component 1')
        plt.savefig(filename)
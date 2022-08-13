import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    labels = []
    evidence = []
    with open(filename) as f:
        reader = csv.reader(f)
        e = []
        next(reader)
        for row in reader:
            e = []
            for i, col in enumerate(row):
                e.append(convert_data_type(col, i))
            labels.append(e[-1])
            evidence.append(e[:-1])
    return (evidence, labels)
                 
def convert_data_type(val, index):
    if index == 0 or index == 2 or index == 4 or index == 11 or index == 12 or index == 13 or index == 14:
        return int(val)
    elif index == 1 or index == 3 or index == 5 or index == 6 or index == 7 or index == 8 or index == 9:
        return float(val)
    elif index == 10:
        months = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5, "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}
        return months[val]
    elif index == 15:
        return 1 if val == "Returning_Visitor" else 0
    else:
        return 1 if val == "TRUE" else 0

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    trues = 0
    g_trues = 0
    falses = 0
    g_falses = 0

    for label, prediction in zip(labels, predictions):
        if label  == 1:
            trues += 1
            if prediction == 1:
                g_trues += 1
        else:
            falses += 1
            if prediction == 0:
                g_falses += 1
    return (g_trues/trues, g_falses/falses)

if __name__ == "__main__":
    main()

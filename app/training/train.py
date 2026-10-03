import os
import numpy as np

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "faces"
)

print("Training started...")
print("Dataset:", DATASET_PATH)

total = 0

for student in os.listdir(DATASET_PATH):

    student_path = os.path.join(DATASET_PATH, student)

    if not os.path.isdir(student_path):
        continue

    print("Student:", student)

    for file in os.listdir(student_path):

        if file.endswith(".npy"):

            file_path = os.path.join(student_path, file)

            np.load(file_path)

            total += 1

print()
print("Training completed!")
print("Total embeddings:", total)
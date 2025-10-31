import os
import numpy as np
import pandas as pd

folder = "/Users/kellyschulte/Project_swe4s/test_data"
for i in os.listdir(folder):
    if i.endswith(".npy"):
        # Load your .npy file
        data = np.load(os.path.join(folder, i))

        # Convert to a pandas DataFrame
        df = pd.DataFrame(data, columns=[f"{i}"])

        # Display the DataFrame
        print(df.head())

        # Optional: save as CSV
        df.to_csv(f"{i}.csv", index=False)
        print(f" Saved {i}.csv")

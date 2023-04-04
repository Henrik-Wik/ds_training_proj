#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import preprocessing as pp

df_training = pp.load_data()
#%%
df_training = pp.clean_data(df_training)

# %%
df_training = df_training[df_training["exercise"].str.contains("band") == False]

print("Number of different exercises: ", df_training["exercise"].nunique())

# %% [markdown]
# I also removed all the exercises containing the word band, since I dont have a weight value for those.

# %%
exercise_rename_list = {
    "rdls": "romanian deadlifts",
    "regular dl": "deadlifts",
    "utfall": "lunges",
    "utfall?": "lunges",
    "bw lunges": "lunges",
    "bw hypers": "hyperextensions",
    "hyper extensions": "hyperextensions",
    "hypers": "hyperextensions",
    "hyperextension": "hyperextensions",
    "militärpress": "overhead press",
    "axelpress": "db shoulder press",
    "back squat": "squats",
    "backsquats": "squats",
    "bench press (pause)": "bench press",
    "larsen press": "bench press",
    "bw pullups": "pull ups",
    "pullups": "pull ups",
    "pull ups*": "pull ups",
    "weighted pull ups": "pull ups",
    "weighted chin ups": "chin ups",
    "barbell benchpress": "bench press",
    "weighted push ups": "push ups",
    "weighted push up": "push ups",
    "sissy sqauts": "sissy squats",
    "biceps": "bicep curls",
    "bw atg split squats": "atg split squats",
    "atg split squat": "atg split squats",
    "oblique maskin": "obliques",
    "delt row": "inverted delt rows",
    "inverted delt row": "inverted delt rows",
    "rear delt row": "wide grip rows",
    "wide row": "wide grip rows",
    "trx rows": "inverted rows",
    "ring rows": "inverted rows",
    "inverted row": "inverted rows",
    "single leg machine curls": "hamstring curls",
    "leg curls": "hamstring curls",
}

df_training["exercise"] = df_training["exercise"].replace(exercise_rename_list)
print("All exercises:\n", df_training.exercise.unique())
print("\nNumber of different exercises: ", df_training.exercise.nunique())

# %%
print(
    "\nTop 10 number of sets of each exercise:\n",
    df_training["exercise"].value_counts().head(10),
)

# %%
df_training = df_training.groupby("exercise").filter(lambda x: len(x) > 4)

print(
    "\nTop 10 number of sets of each exercise:\n",
    df_training["exercise"].value_counts().head(10),
)
print("\nNumber of different exercises: ", df_training.exercise.nunique())

# %% [markdown]
# ## Weight data
# ### Start with cleaning
#
# This time I can put the raw data directly in python because it is already pretty well structured.

# %%
df = pd.read_csv("data/weight.csv")
df = df.drop(
    columns=[
        "Fat mass (kg)",
        "Bone mass (kg)",
        "Muscle mass (kg)",
        "Hydration (kg)",
        "Comments",
    ],
    axis=1,
)
df = df.rename(columns={"Date": "date", "Weight (kg)": "bodyweight"})

df.head()

# %%
df["date"] = pd.to_datetime(df.date)
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df = df.drop("date", axis=1)
df = df.set_index(["year", "month", "day"])
df = df.iloc[::-1]

df.head()

# %% [markdown]
# We fixed the multi-index in the same way as the training data, but there are multiple entries for the same day.
#
# We will take the mean for those and include only one entry per day.

# %%
df = df.groupby(["year", "month", "day"]).mean()
df_weight = df
df_weight.head(10)

# %% [markdown]
# Now it looks like how I want it.

# %% [markdown]
# We can then join all the data tables on the index

# %%
df = df_training.join(df_weight, None, how="left")

df = df.reset_index(level=["year", "month", "day"])
df["date"] = pd.to_datetime(df[["year", "month", "day"]])
df = df.drop(["year", "month", "day"], axis=1)
df.head()

# %%
df = df.dropna(subset=["exercise"])

# df.to_csv('data/Training and Weight data clean.csv', index=False)

df.set_index("date", inplace=True)

# %%
# Calculating tonnage

df["tonnage"] = (
    df["weight"] * df["reps"] * df["set #"].count() / 1000
)  # Divide by 1000 to get tonnes
df["tonnage_avg"] = df["tonnage"].rolling(window=100).mean()
# %%
# Total tonnage resampled weekly and monthly to mmore easily visualize
df_weekly = df.resample("W").mean()
df_monthly = df.resample("M").mean()

df_weekly["tonnage"].plot(kind="line", figsize=(10, 8))
df_monthly["tonnage"].plot(kind="line", figsize=(10, 8))
plt.title("Total Tonnage Over Time")
plt.xlabel("Date")
plt.ylabel("Weight (Tonnes)")
plt.legend(["weekly", "monthly"])

# %%
# Top 10 Exercises
df["exercise"].value_counts().nlargest(10).plot(kind="bar", figsize=(10, 8))
plt.title("Top 10 Exercises")
plt.xlabel("Exercise")
plt.ylabel("Total Count")
# %%
# Tonnage line graphs
exercise_names = [
    "hamstring curls",
    "sumo dl",
    "bench press",
    "inverted rows",
    "pull ups",
    "squats",
    "romanian deadlifts",
    "overhead press",
]

fig, axs = plt.subplots(4, 2, figsize=(10, 8))

for i, exercise_name in enumerate(exercise_names):
    row = i // 2
    col = i % 2
    exercise_df = df[df["exercise"] == exercise_name]
    exercise_df["tonnage"] = (
        exercise_df["weight"]
        * exercise_df["reps"]
        * exercise_df["set #"].count()
        / 1000
    )  # Divide by 1000 to get tonnes
    grouped_df = exercise_df.groupby("date")["tonnage"].sum().reset_index()
    axs[row, col].plot(grouped_df["date"], grouped_df["tonnage"])
    axs[row, col].set_title(f"Tonnage for {exercise_name}")
    axs[row, col].set_xlabel("Date")
    axs[row, col].set_ylabel("Weight (Tonnes)")
    axs[row, col].tick_params(axis="x", rotation=45)

plt.tight_layout()
# %%
# Tonnage Boxplots
exercise_names = [
    "hamstring curls",
    "sumo dl",
    "bench press",
    "inverted rows",
    "pull ups",
    "squats",
    "romanian deadlifts",
    "overhead press",
]

fig, axs = plt.subplots(4, 2, figsize=(10, 8))

for i, exercise_name in enumerate(exercise_names):
    row = i // 2
    col = i % 2
    exercise_df = df[df["exercise"] == exercise_name]
    exercise_df["tonnage"] = (
        exercise_df["weight"]
        * exercise_df["reps"]
        * exercise_df["set #"].count()
        / 1000
    )  # Divide by 1000 to get tonnes
    grouped_df = exercise_df.groupby("date")["tonnage"].sum().reset_index()
    axs[row, col].boxplot(grouped_df["tonnage"])
    axs[row, col].set_title(f"Tonnage for {exercise_name}")
    axs[row, col].set_xlabel("Exercise")
    axs[row, col].set_ylabel("Weight (Tonnes)")

plt.tight_layout()
# %%
# Weight box plots
exercise_names = [
    "hamstring curls",
    "sumo dl",
    "bench press",
    "inverted rows",
    "pull ups",
    "squats",
    "romanian deadlifts",
    "overhead press",
]

fig, axs = plt.subplots(4, 2, figsize=(10, 8))

for i, exercise_name in enumerate(exercise_names):
    row = i // 2
    col = i % 2
    exercise_df = df[df["exercise"] == exercise_name]
    grouped_df = exercise_df.groupby("date")["weight"].max().reset_index()
    axs[row, col].boxplot(grouped_df["weight"])
    axs[row, col].set_title(f"Weight for {exercise_name}")
    axs[row, col].set_ylabel("Weight (Kg)")
    axs[row, col].set_xticklabels({exercise_name})


plt.tight_layout()
# %%
# Max Weight over time Linegraphs
exercise_names = [
    "hamstring curls",
    "sumo dl",
    "bench press",
    "inverted rows",
    "pull ups",
    "squats",
    "romanian deadlifts",
    "overhead press",
]

fig, axs = plt.subplots(4, 2, figsize=(10, 8))

for i, exercise_name in enumerate(exercise_names):
    row = i // 2
    col = i % 2
    exercise_df = df[df["exercise"] == exercise_name]
    exercise_df["max_weight"] = exercise_df.groupby("date")["weight"].transform("max")
    grouped_df = exercise_df.groupby("date")["max_weight"].max().reset_index()
    axs[row, col].plot(grouped_df["date"], grouped_df["max_weight"])
    axs[row, col].set_title(f"Max Weight for {exercise_name}")
    axs[row, col].set_xlabel("Exercise")
    axs[row, col].set_ylabel("Weight (Kg)")
    axs[row, col].tick_params(axis="x", rotation=45)


plt.tight_layout()
# %%

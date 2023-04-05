# %%
import re

import pandas as pd

# load data
# df = pd.read_csv("data/November 2022 full body merged.csv", sep=";")
df = pd.read_csv("data/Träningsschema December Upper lower 6d HEMMA.csv", sep=";")


# %% #FIXME
# misspelled exercise, changed all to lower case
df.rename(columns={"excercise": "exercise"}, inplace=True)
df.exercise = df.exercise.str.lower()
# fill missing dates with previous date
df.Date = df.Date.fillna(method="ffill")

df = df[df.Date.str.contains("Date") == False]


# %%
# Split date into year, month, day
df["date"] = pd.to_datetime(df.Date)
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

columns_to_keep = [
    "year",
    "month",
    "day",
    "exercise",
    "set 1",
    "set 2",
    "set 3",
    "set 4",
]


columns_to_drop = [col for col in df.columns if col not in columns_to_keep]

df.drop(columns=columns_to_drop, inplace=True)

# %%
# drop missing values
# df.dropna(inplace=True)

for i in range(1, 5):
    df[f"set {i} reps"] = df[f"set {i}"].apply(
        lambda x: re.split("x|\*", x)[0] if isinstance(x, str) else None
    )
    df[f"set {i} weight"] = df[f"set {i}"].apply(
        lambda x: re.split("x|\*", x)[1] if isinstance(x, str) and ('x' in x or '*' in x) else None
    )

# %%
df.drop(columns=["set 1", "set 2", "set 3", "set 4"], inplace=True)

# melt the dataframe into a long format
melted_df = pd.melt(
    df,
    id_vars=["year", "month", "day", "exercise"],
    value_vars=[
        "set 1 reps",
        "set 2 reps",
        "set 3 reps",
        "set 4 reps",
        "set 1 weight",
        "set 2 weight",
        "set 3 weight",
        "set 4 weight",
    ],
    var_name="set",
    value_name="values",
)

# %%
# separate the 'set' column into 'set number' and 'metric' columns
melted_df[["set_name", "set #"]] = melted_df["set"].str.extract(
    r"(set) (\d+)", expand=True
)
melted_df["type"] = melted_df["set"].str.extract(r"(\w+)$", expand=True)

# drop the original 'set' column
melted_df = melted_df.drop(columns=["set"])


# %%
# pivot the dataframe to get reps and weights in separate columns
pivoted_df = melted_df.pivot_table(
    index=["year", "month", "day", "exercise", "set #"],
    columns="type",
    values="values",
    aggfunc="first",
).reset_index()

df = pivoted_df.set_index(["year", "month", "day"])
df = pivoted_df[pivoted_df["reps"] != 0]

# %%

df[['reps','weight']] = df[['reps','weight']].replace(r'[a-zA-Z]', '', regex=True)
df.replace(',','.', regex=True, inplace=True)


#%%


df.head(20)


# %%

# %% [markdown]
# # Training and Health Analysis

# %% [markdown]
# ## Training data
# ### We start by importing the data and cleaning it

# %% [markdown]
# I did a rough cleaning of the data in Power BI in order to more easily see what data to remove and change. Then for the more thorough cleaning I import all the data from csv-files into python with pandas.

# %%
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('data/Trainingdata Rough Clean.csv')

df.rename(columns={"excercise": "exercise"}, inplace=True)
df.exercise = df.exercise.str.lower()
df = df[df.Date.str.contains('Date') == False]
df.head()

# %% [markdown]
# I first need to fix the dates so I can easily sort by year month and day.

# %%
df['date'] = pd.to_datetime(df.Date)
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

df.head()

# %% [markdown]
# I also want the reps and weights for all the sets in the same column so i need to do some manipulation here.

# %%
# melt the dataframe into a long format
melted_df = pd.melt(df, id_vars=['year', 'month', 'day', 'exercise'],
                    value_vars=['set 1 reps', 'set 2 reps', 'set 3 reps', 'set 4 reps',
                                'set 1 weight', 'set 2 weight', 'set 3 weight', 'set 4 weight'],
                    var_name='set', value_name='values')

# separate the 'set' column into 'set number' and 'metric' columns
melted_df[['set_name', 'set #', 'type']
          ] = melted_df['set'].str.split(' ', expand=True)

# drop the original 'set' column
melted_df = melted_df.drop(columns=['set'])

# pivot the dataframe to get reps and weights in separate columns
pivoted_df = melted_df.pivot_table(index=['year', 'month', 'day', 'exercise', 'set #'],
                                   columns='type', values='values').reset_index()

pivoted_df.head()

# %% [markdown]
# Now it looks like I want it to, however, I want to remove the 'type' column header, which could be done by exporting the dataframe without index.

# %%
# removed type column by exporting
pivoted_df.to_csv('data/Trainingdata remove index.csv', index=False)

# %%
df_training = pd.read_csv('data/Trainingdata remove index.csv')
df_training = df_training.set_index(['year', 'month', 'day'])
df_training = df_training[df_training['reps'] != 0]

df_training.head(10)

# %% [markdown]
# We fix the index, and also remove all sets where I have done zero reps.

# %%
df_training = df_training[df_training['exercise'].str.contains(
    'band') == False]

print('Number of different exercises: ', df_training['exercise'].nunique())

# %% [markdown]
# I also removed all the exercises containing the word band, since I dont have a weight value for those.

# %%
exercise_rename_list = {
    'rdls': 'romanian deadlifts',
    'regular dl': 'deadlifts',
    'utfall': 'lunges',
    'utfall?': 'lunges',
    'bw lunges': 'lunges',
    'bw hypers': 'hyperextensions',
    'hyper extensions': 'hyperextensions',
    'hypers': 'hyperextensions',
    'hyperextension': 'hyperextensions',
    'militärpress': 'overhead press',
    'axelpress': 'db shoulder press',
    'back squat': 'squats',
    'backsquats': 'squats',
    'bw pullups': 'pull ups',
    'pullups': 'pull ups',
    'pull ups*': 'pull ups',
    'weighted pull ups': 'pull ups',
    'weighted chin ups': 'chin ups',
    'barbell benchpress': 'bench press',
    'weighted push ups': 'push ups',
    'weighted push up': 'push ups',
    'sissy sqauts': 'sissy squats',
    'biceps': 'bicep curls',
    'bw atg split squats': 'atg split squats',
    'atg split squat': 'atg split squats',
    'oblique maskin': 'obliques',
    'delt row': 'inverted delt rows',
    'inverted delt row': 'inverted delt rows',
    'rear delt row': 'wide grip rows',
    'wide row': 'wide grip rows',
    'trx rows': 'inverted rows',
    'ring rows': 'inverted rows',
    'inverted row': 'inverted rows',
    'single leg machine curls': 'hamstring curls',
    'leg curls': 'hamstring curls',
}
df_training['exercise'] = df_training['exercise'].replace(exercise_rename_list)
print("All exercises:\n", df_training.exercise.unique())
print("\nNumber of different exercises: ", df_training.exercise.nunique())

# %%
print('\nTop 10 number of sets of each exercise:\n',
      df_training['exercise'].value_counts().head(10))

# %%
df_training = df_training.groupby('exercise').filter(lambda x: len(x) > 4)

print('\nTop 10 number of sets of each exercise:\n',
      df_training['exercise'].value_counts().head(10))
print('\nNumber of different exercises: ', df_training.exercise.nunique())

# %% [markdown]
# ## Weight data
# ### Start with cleaning
#
# This time I can put the raw data directly in python because it is already pretty well structured.

# %%
df = pd.read_csv('data/weight.csv')
df = df.drop(columns=['Fat mass (kg)', 'Bone mass (kg)',
             'Muscle mass (kg)', 'Hydration (kg)', 'Comments'], axis=1)
df = df.rename(columns={'Date': 'date', 'Weight (kg)': 'bodyweight'})

df.head()

# %%
df['date'] = pd.to_datetime(df.date)
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df = df.drop('date', axis=1)
df = df.set_index(['year', 'month', 'day'])
df = df.iloc[::-1]

df.head()

# %% [markdown]
# We fixed the multi-index in the same way as the training data, but there are multiple entries for the same day.
#
# We will take the mean for those and include only one entry per day.

# %%
df = df.groupby(['year', 'month', 'day']).mean()
df_weight = df
df_weight.head(10)

# %% [markdown]
# Now it looks like how I want it.

# %% [markdown]
# We can then join all the data tables on the index

# %%
df = df_training.join(df_weight, None, how='left')

df = df.reset_index(level=['year', 'month', 'day'])
df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
df = df.drop(['year', 'month', 'day'], axis=1)
df.head()

# %%
df = df.dropna(subset=['exercise'])

df.to_csv('data/Training and Weight data clean.csv', index=False)
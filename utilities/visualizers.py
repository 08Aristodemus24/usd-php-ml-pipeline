import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import os

def disp_cat_feat(df: pd.DataFrame, cat_cols: list | pd.Index, fig_dims: tuple=(3, 2), img_title: str="untitled", save_img: bool=True, style: str='dark'):
    """
    suitable for all discrete input

    displays frequency of categorical features of a dataframe
    """

    styles = {
        'dark': 'dark_background',
        'solarized': 'Solarized_Light2',
        '538': 'fivethirtyeight',
        'ggplot': 'ggplot',
    }

    plt.style.use(styles.get(style, 'default'))

    # unpack dimensions of figure
    rows, cols = fig_dims
    
    # setup figure
    # fig, axes = plt.subplots(rows, cols, figsize=(15, 15), gridspec_kw={'width_ratios': [3, 3], 'height_ratios': [5, 5, 5]})
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
    axes = axes.flat
    fig.tight_layout(pad=7)

    # helper function
    def hex_color_gen():
        rgb_gen = lambda: np.random.randint(0, 255)
        color = "#%02X%02X%02X" % (rgb_gen(), rgb_gen(), rgb_gen())
        return color

    # loop through all categorical features and see their frequencies
    for index, col in enumerate(cat_cols):
        # get value and respective counts of current categorical column
        val_counts = df[col].value_counts()

        # count the number of unique values if it exceeds 10 use
        # only the first 10 of teh value counts to visualize
        n_unqiue = 10 if val_counts.shape[0] > 10 else val_counts.shape[0]

        # get all unqiue categories of the feature/column
        keys = list(val_counts.keys())

        colors = [hex_color_gen() for _ in range(n_unqiue)]
        print(colors, n_unqiue)
        chosen_colors = np.random.choice(colors, n_unqiue, replace=False)
        
        # list all categorical columns no of occurences of each of their unique values
        ax = val_counts[:n_unqiue].plot(kind='barh', ax=axes[index], color=chosen_colors)

        # annotate bars using axis.containers[0] since it contains
        # all 
        print(ax.containers[0])
        ax.bar_label(ax.containers[0], )
        ax.set_ylabel('no. of occurences', )
        ax.set_xlabel(col, )
        ax.set_title(img_title, )
        ax.legend()

        # current column
        print(col)

    if save_img:
        os.makedirs('./figures & images/', exist_ok=True)
        plt.savefig(f'./figures & images/{img_title}.png')
        plt.show()


def view_feat_outliers(df: pd.DataFrame, num_cols: list | pd.Index, fig_dims: tuple=(3, 2), img_title: str="untitled", save_img: bool=True, style: str='dark'):
    """
    
    """
    styles = {
        'dark': 'dark_background',
        'solarized': 'Solarized_Light2',
        '538': 'fivethirtyeight',
        'ggplot': 'ggplot',
    }

    plt.style.use(styles.get(style, 'default'))

    # unpack dimensions of figure
    rows, cols = fig_dims
    
    # setup figure
    # fig, axes = plt.subplots(rows, cols, figsize=(15, 15), gridspec_kw={'width_ratios': [3, 3], 'height_ratios': [5, 5, 5]})
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
    axes = axes.flat
    fig.tight_layout(pad=7)

    # calculate mean, std, median, 75th, 50th, and 25th quartile, min, 
    # max, and count all numerical columns in the  
    num_cols_desc = df[num_cols].describe()
    # print(num_cols_desc.loc["75%", :])
    # print(num_cols_desc.loc["max", :])

    # get 75th and 25th percentile of all columns
    _75_p = num_cols_desc.loc["75%", :]
    _25_p = num_cols_desc.loc["25%", :]

    iqr = _75_p - _25_p
    # print(f"iqr: {iqr}")

    upper_bound = _75_p + (1.5 * iqr)
    lower_bound = _25_p - (1.5 * iqr)
    # print(f"upper bound: {upper_bound}")
    # print(f"lower bound: {lower_bound}")

    
    # loop through each column and create boxplot for each
    for i, col in enumerate(num_cols):
        col_median =  df[col].median()
        col_outliers = df.loc[(df[col] <= lower_bound[col]) | (df[col] >= upper_bound[col]), col]
        # outliers[col] = col_outliers

        # create boxplots
        # meta data for boxplot design
        kwargs_list = [
            
        ]

        # colors to choose from
        colors = ["#f54949", "#f59a45", "#afb809", "#51ad00", "#03a65d", "#035aa6", "#03078a", "#6902e6", "#c005e6", "#fa69a3", "#240511", "#052224", "#402708",]
        sampled_idx = np.random.choice(list(range(len(colors))), size=1, replace=False)[0]
        kwargs = {
            "whiskerprops": dict(color=colors[sampled_idx]),
            "boxprops": dict(color=colors[sampled_idx], facecolor=colors[sampled_idx]),
            "capprops": dict(color=colors[sampled_idx]),
            "flierprops": dict(markeredgecolor=colors[sampled_idx], color=colors[sampled_idx]),
            "medianprops": dict(color=colors[sampled_idx]),
        }
        # print(kwargs)

        # build boxplot
        # a patch artist of true will fill the box plot a notch of 
        # true will let's say wedge the box plot in the median of the box
        # to represent the median
        ax = df.boxplot(column=col, vert=False, figsize=(15, 15), ax=axes[i], patch_artist=True, notch=True, **kwargs)
        
        # shifts the 
        offset = -5

        arrowprops = {
            'arrowstyle': '->'
        }

        _95_p = np.quantile(df[col], 0.95)
        _05_p = np.quantile(df[col], 0.05)
        print(f"{_95_p if col.lower() == "age" else ""}")
        lower_whisker = lower_bound[col]
        upper_whisker = upper_bound[col]

        # annotate each boxplots median, 75th, 25th, 95th, and 5th percentiles
        ax.annotate(f'median: {round(col_median, 2)}', xy=(col_median, 1), xytext=(col_median + offset, 1.375), arrowprops=arrowprops)
        ax.annotate(f'75%: {round(num_cols_desc[col]["75%"], 2)}', xy=(num_cols_desc[col]["75%"], 1), xytext=(num_cols_desc[col]["75%"] + offset, 0.75), arrowprops=arrowprops)
        ax.annotate(f'25%: {round(num_cols_desc[col]["25%"], 2)}', xy=(num_cols_desc[col]["25%"], 1), xytext=(num_cols_desc[col]["25%"] + offset, 0.75), arrowprops=arrowprops)
        ax.annotate(f'95%: {round(_95_p, 2)}', xy=(round(_95_p, 2), 1), xytext=(round(_95_p, 2) + offset, 1.25), arrowprops=arrowprops)
        ax.annotate(f'5%: {round(_05_p, 2)}', xy=(round(_05_p, 2), 1), xytext=(round(_05_p, 2) + offset, 1.25), arrowprops=arrowprops)
        ax.annotate(f'max: {round(num_cols_desc[col]["max"], 2)}', xy=(num_cols_desc[col]["max"], 1), xytext=(num_cols_desc[col]["max"] + offset, 0.75), arrowprops=arrowprops)
        ax.annotate(f'min: {round(num_cols_desc[col]["min"], 2)}', xy=(num_cols_desc[col]["min"], 1), xytext=(num_cols_desc[col]["min"] + offset, 0.75), arrowprops=arrowprops)
        ax.annotate(f'lower whisker: {lower_whisker}', xy=(lower_whisker, 1), xytext=(lower_whisker + offset, 1.25), arrowprops=arrowprops)
        ax.annotate(f'upper whisker: {upper_whisker}', xy=(upper_whisker, 1), xytext=(upper_whisker + offset, 1.25), arrowprops=arrowprops)

        ax.set_ylabel("")
        ax.set_xlabel(col)

    
    if save_img:
        os.makedirs('./figures & images/', exist_ok=True)
        plt.savefig(f'./figures & images/{img_title}.png')
        plt.show()

def plot_forex_signals(
    df: pd.DataFrame, 
    cols_to_use: list=["volume", "volume_weighted", "highest_price", "lowest_price", "opening_price", "closing_price"], 
    fig_size: tuple=(15, 30), 
    img_title: str="untitled", 
    save_img: bool=True, 
    style="dark"
):
    """
    suitable for all discrete input

    displays frequency of categorical features of a dataframe
    """

    styles = {
        'dark': 'dark_background',
        'solarized': 'Solarized_Light2',
        '538': 'fivethirtyeight',
        'ggplot': 'ggplot',
    }

    plt.style.use(styles.get(style, 'default'))

    # setup figure
    rows = len(cols_to_use)
    fig, axes = plt.subplots(rows, 1, figsize=fig_size)
    axes = axes.flat
    fig.tight_layout(pad=7)

    # helper function
    def hex_color_gen():
        rgb_gen = lambda: np.random.randint(0, 255)
        color = "#%02X%02X%02X" % (rgb_gen(), rgb_gen(), rgb_gen())
        return color
    
    # create ticks for x-axis derived from df's basic statistics
    df_stats = df.describe()
    x_ticks = pd.date_range(start=df_stats.loc["min", "timestamp"], end=df_stats.loc["max", "timestamp"], periods=df.shape[0])
    
    # loop through all categorical features and see their frequencies
    for index, col in enumerate(cols_to_use):
        
        # list all categorical columns no of occurences of each of their unique values
        axis = df.plot(x="timestamp", y=col, kind='line', ax=axes[index], color=hex_color_gen(), alpha=0.75)

        #
        axis.set_xticks([x_tick for i, x_tick in enumerate(x_ticks) if i % 50 == 0]) 
        axis.set_xlabel("timestamp", )
        axis.tick_params(axis='x', labelrotation=45.0)
        axis.set_ylabel(col, )
        
        axis.set_title(img_title, )
        axis.legend()

        # current column
        print(col)

    if save_img:
        os.makedirs('./figures & images/', exist_ok=True)
        plt.savefig(f'./figures & images/{img_title}.png')
        plt.show()
import json
import pandas as pd

def get_brand_username(filename = "brand2username.csv"):
    df = pd.read_csv("brand2username.csv")
    brands = list(df['Brand'].values)
    usernames = list(df['TikTok Username'].values)
    return (df, brands, usernames)

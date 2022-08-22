from datetime import date
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd

from app import cache

DEFAULT_DATA_FILE = "./data/golf_scores.xlsx"
MEMOIZE_TIMEOUT = 60


def convert_date(
    in_date: Union[str, date, datetime, np.datetime64],
    out_type: str,
    in_fmt: str = None,
) -> Union[str, date, datetime]:
    """
    Converts a date with a standardish type into many other types.

    The default is to return a date string that can be used in a SQL query to filter
    by dates, e.g., '2022-06-23' (includes the quotes).

    Args:
        in_date: Type should be date, datetime, or a str like yyyy-mm-dd
            (`%Y-%m-%d`), yyyymmdd (`%Y%m%d`), or another format specified with in_fmt.
        out_type: "date", "datetime", "str10" (yyyy-mm-dd), "str8" (yyyymmdd), or a
            another date format string like "%b-%Y". Use "sql10" and "sql8" to add
            single quotes surrounding the date.

    Returns:
        The date in the specified output type and format.

    """
    if in_date is None:
        return None
    # convert to date type
    # first convert str to datetime, then datetime to date
    if isinstance(in_date, np.datetime64):
        in_date = pd.to_datetime(in_date)
    if isinstance(in_date, str):
        if in_fmt is not None:
            in_date = datetime.strptime(in_date, in_fmt).date()
        elif len(in_date) == 8:
            in_date = datetime.strptime(in_date, "%Y%m%d").date()
        elif len(in_date) == 10:
            in_date = datetime.strptime(in_date, "%Y-%m-%d").date()
        elif len(in_date) == 19:
            in_date = datetime.strptime(in_date, "%Y-%m-%dT%H:%M:%S").date()
        else:
            raise ValueError
    if isinstance(in_date, datetime):
        in_date = in_date.date()
    # then convert to output type
    if out_type == "date":
        return in_date
    elif out_type == "datetime":
        return datetime(in_date.year, in_date.month, in_date.day)
    elif out_type == "str8":
        return in_date.strftime("%Y%m%d")
    elif out_type == "str10":
        return in_date.strftime("%Y-%m-%d")
    elif out_type == "sql8":
        return in_date.strftime("'%Y%m%d'")
    elif out_type == "sql10":
        return in_date.strftime("'%Y-%m-%d'")
    elif isinstance(out_type, str):
        return in_date.strftime(out_type)
    raise ValueError


def parse_data_file(xls: pd.ExcelFile = None) -> pd.DataFrame:
    if xls is None:
        xls = pd.ExcelFile(DEFAULT_DATA_FILE)
    df = pd.read_excel(xls, sheet_name="Scores")
    cs = pd.read_excel(xls, sheet_name="Courses")
    df = df.merge(cs, how="left", on=["Course", "Tee", "Hole"])

    df["ScoreToPar"] = df["Score"] - df["Par"]
    df["PuttsToPar"] = df["Putts"] - 2

    # GIR: Is # of non-putts taken <= # of non-putts allowed (based on par)?
    df["GIR"] = df["Score"] - df["Putts"] <= df["Par"] - 2

    def fir_func(data):
        if data["Par"] > 3:
            if data["TeeAccuracy"] == "H":
                return True
            else:
                return False
        return None

    df["FIR"] = df.apply(fir_func, axis=1)

    return df


def filter_df(
    df: pd.DataFrame,
    dates: str = None,
    date_range: list = None,
    golfers: list = None,
    courses: list = None,
):
    if dates is None:
        pass
    elif dates == "Last 20 rounds":
        dates_of_last_20 = df["Date"].unique()
        dates_of_last_20.sort()
        dates_of_last_20 = dates_of_last_20[::-1][0:20]
        date_range = [
            convert_date(min(dates_of_last_20), "str10"),
            convert_date(max(dates_of_last_20), "str10"),
        ]

    if date_range is not None:
        df = df[(df["Date"] >= date_range[0]) & (df["Date"] <= date_range[1])]

    if golfers is not None and golfers != []:
        df = df[df["Golfer"].isin(golfers)]

    if courses is not None and courses != []:
        df = df[df["Course"].isin(courses)]

    return df


@cache.memoize(timeout=MEMOIZE_TIMEOUT)
def get_scores(df: pd.DataFrame) -> pd.DataFrame:
    scores = (
        df.groupby(["Golfer", "Date", "Course", "Tee"])
        .agg(
            Score=("Score", "sum"),
            ScoreToPar=("ScoreToPar", "sum"),
            Putts=("Putts", "sum"),
            PuttsToPar=("PuttsToPar", "sum"),
            NumHoles=("Hole", "count"),
            GreensHit=("GIR", "sum"),
            GIR=("GIR", "mean"),
            NumFairways=("FIR", "count"),
            FairwaysHit=("FIR", "sum"),
            FIR=("FIR", "mean"),
        )
        .reset_index()
    )
    return scores

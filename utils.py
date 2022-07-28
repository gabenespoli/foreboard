from datetime import date
from datetime import datetime
from typing import Union

import pandas as pd


def convert_date(
    in_date: Union[str, date, datetime],
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
    if isinstance(in_date, str):
        if in_fmt is not None:
            in_date = datetime.strptime(in_date, in_fmt).date()
        elif len(in_date) == 8:
            in_date = datetime.strptime(in_date, "%Y%m%d").date()
        elif len(in_date) == 10:
            in_date = datetime.strptime(in_date, "%Y-%m-%d").date()
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


def filter_gf(
    gf: pd.DataFrame,
    dates: list = None,
    golfers: list = None,
    courses: list = None,
):
    if dates is not None:
        min_date = convert_date(dates[0], "datetime")
        max_date = convert_date(dates[1], "datetime")
        gf = gf[gf["Date"] >= min_date & gf["Date"] >= max_date]

    if golfers is not None:
        gf = gf[gf["Golfer"].isin(golfers)]

    if courses is not None:
        gf = gf[gf["Course"].isin(courses)]

    return gf

Version 20190212_00
-------------------
- Added Holiday features
    - New column is_holiday (True/False) True if the movie was released on US holiday (real or observed)
    - holiday_name, the closest holiday to the release date
    - days_from_holiday number of days between the release and the closest holiday (-) numbers means the release was
        before the holiday (for instance -31 Labor Day, means that the movie was released in Aug
        as Labor Day is first Monday in Sept).  Positive numbers mean the release was that many days after the holiday
        so that 3 Christmas represents a release on Dec 28.  Zero means it was released on the holiday.
TO CONSIDER
    - May want to bucket the movies, since there are only 14 holidays per year (max) we may want to say T/F movies within
      1 week of a holiday are True, but outside that False.

Version 20190211_15
-------------------
- First pass of clean-up
    - determined whether a movie was part of a series (belongs_to_collection)
    - removed 5 movies that had no release date and no title
    - fixed up release date
        - Fixed Century, those release dates with 2 digit centurys coming in between 19 and 99 were considered 20th
        century movies (19xx) while the others were set to the 21st century (20xx)
        - Separated out the release month and release day of the month as well as the release day of the week
        (Monday = 0, Sunday = 6)
        - Created dummy columns for all represented genres.  NOTE: some movie are categorized into multiple genres
        - Create dummy columns for top 13 spoken languages (representative of all languages that have been featured in
        at least 70 (1%) of the films in the dataset + Spoken_Lang_Other
        - Created dummy columns for 98 countries where production took place
        -
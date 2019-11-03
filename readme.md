#kinja-archive
This is a file I wrote for some friends who used to work at Gawker to scrape their post archives into a text format. I've since updated it for changes to Kinja, but decided to change the name since Gawker posts are no longer on Kinja.

This is a work in progress, and in its current form it will require you to know how too use a command line and Python 3. I wouldn't recommend trying this wrote unless you're comfortable with programming. I'm working on making it user friendly.

Currently, in order to run, you will need to edit kinja.py and change the variable "url" on line 14 to that of your Kinja profile page. 

```url = "https://kinja.com/your-profile-here"```

Then simply run `python kinja.py` and it will take care of the rest.
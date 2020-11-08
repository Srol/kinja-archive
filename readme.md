# kinja-archive

This code downloads your Kinja archive.

**Important**: this attempts to intelligently filter content, so some of your text, especially using unusual features like attributions, may be left behind.

**ALSO**: Pages without titles and pages with Unicode (emoji, non-ascii characters) are probably not going to work yet, sorry.

Python 3.7 is recommended. Not sure how far back this would go.

You'll need library bs4 as well.

Run it: python kinja.py \<username\> [--images] [--urls-only]

Where 'username' is your real Kinja username, where your profile lives,
and --images will download the images in your articles if you wish.

--urls-only will simply grab your history and print all URLs to the
screen. No local files will be created.

Otherwise, the script will create new folders underneath by year.

I take no blame for bandwidth costs or any other ill consequences. Don't
run this in an environment where you might break anything.

# Flashbot

A Discord bot for TCC SI Leaders.

## Commands

### !create (activity name) [additional parameters]
This command generates a virtual activity for you to use. Valid activity names are as follows:
#### catastrophe [terms separated by commas. The first term will be the mural's name]
This command generates a mural on Mural and places the terms provided scattered throughout the mural as sticky notes. The first term in the comma-separated list will be used as the mural's name. Both facilitator and visitor links will be returned.
#### stoplight [terms separated by commas (min 1, max 6)
This command generates a slide on Google Slides with red, yellow, and green circles to indicate student confidence on the specified topics. Each topic will have its own area on the slide. The link to the generated slide will be returned, which can then be copy-pasted to your own presentation.

### !sessionplan [number of minutes - valid values: 60, 50]
Generates a session plan for a one-hour session. If 50 is passed in as an optional parameter, the session plan will be made for a 50-minute session instead.

### !activity (activity name)
Posts the description and VARK designation of the specified activity.

### !schedule (TCC campus name or abbreviation)
Posts the TinyURL link of the SI schedule at the specified campus.

### !helpdocs
Sends a link to this help document.

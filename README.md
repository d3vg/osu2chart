# osu2chart
A GUI tool for converting osu!mania maps to Clone Hero charts.

This was made for those who prefer the charting workflow of the osu!mania editor over the charting workflow of Moonscraper and Feedback, however it can be used to just play around with, too.

Here is a [YouTube video](https://www.youtube.com/watch?v=gpp6JAtrq2k) demonstrating the usage of the program.

How to use
---
1. Download and install the latest version of [Python](https://www.python.org/downloads/).
2. Download this repository as a .zip file to your computer and extract.
3. Go to the folder where you extracted the files to and open `osu2chart.pyw` and a GUI window should open.


The following rules are used when converting the .osu file:

All Maps
---
- The Creator is treated as the "Charter"
- The Tags metadata can be treated as the "Genre"
- The Overall Difficulty (OD) is treated as the "Difficulty"
- The map preview time is used as the "PreviewStart"

<6K maps
---
- Key 1-5 = GRYBO `(N # length)`

6K~9K maps:
---
- Key 1   = Open Strum `(N 7 length)`
- Key 2-6 = GRYBO
- Key 7   = Forced Note `(N 5 0)`
- Key 8   = Tap Note `(N 6 0)`
- Key 9   = Starpower (Use long notes) `(S 2 length)`

\>9K maps (co-op maps)
---
* Same as their single player counterparts above, except the "2P" side of notes are converted to co-op note tracks (e.g. for a 10K map, keys 1-5 are the normal Single track, and keys 6-10 are the Double track for that difficulty)

Things to consider / known issues
---
- Quotation marks in metadata fields cut off in Moonscraper/Clone Hero,
  consider using single quotation marks instead.

- If your map has multiple BPM changes, you may run into Moonscraper giving you a bunch of warnings saying that time signatures must be aligned to the measure set by the previous time signature. This warning *does not actually affect gameplay*, but will cause the measure lines on the fretboard in Clone Hero to not line up as you would expect. If you do not want this, you must work around this limitation and place all of your BPM changes at the starts of measures as you are tempo mapping.

- .osu files only contain millisecond precision time values for timing points and hit objects, which is not enough accuracy when converting to the .chart format. This can lead to notes not always being snapped to "the grid" in Moonscraper. However, the tool does attempt to quantize the notes in an effort to minimize the effects of this and it's hardly ever a real issue. If your conversion happens to have a lot of these off the grid notes, consider upping the resolution to `192`, which sometimes seems to help.


# Iterate over file listing and do something for each file.
# Handy for batch renaming stuff, like subtitle files.

for dirname in $(ls Subs); do echo cp -i Subs/$dirname/* ./$dirname.srt; done

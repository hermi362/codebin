# Iterate over file listing and do something for each file.
# Handy for batch renaming stuff, like subtitle files.

for dirname in $(ls Subs); do echo cp -i Subs/$dirname/* ./$dirname.srt; done
for dirname in Subs/*;     do echo cp -i Subs/$dirname/* ./$dirname.srt; done
# The second version uses globbing, which is better because if a certain filename has a space in it, the first version will split that filename into two.


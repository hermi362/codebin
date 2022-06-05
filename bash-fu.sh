# Iterate over file listing and do something for each file.
# Handy for batch renaming stuff, like subtitle files.

for dirname in $(ls Subs); do echo cp -i Subs/$dirname/2_*.srt   ./$dirname.srt; done

# This version uses globbing, which is better because if a subtitle filename has a space in it, the version using $(ls Subs) will split that filename into two.
cd Subs; for dirname in ./*; do echo cp -i $dirname/2_*.srt ../$dirname.srt; done


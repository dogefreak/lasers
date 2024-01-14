# Developments on Showkontrol's OSC to QuickShow
In this project I tried to fetch the TC Supply Showkontrol OSC signal to automatically sync to QuickShow.
The goal of doing this was to automatically sync the BPM to QuickShow based on the active Pioneer DJ deck's BPM.

These are the OSC commands the scripts are supposed to receive from ShowKontrol (which is port 7000 by default):
- /pangolin/deck1/bpm f BPM
- /pangolin/deck2/bpm f BPM
- /pangolin/deck3/bpm f BPM
- /pangolin/deck4/bpm f BPM
- /pangolin/mixer/activedeck i 1-4

Unfortunately I haven't continued the development. This is because I switched to a solution based on [Beat Link Trigger](https://github.com/Deep-Symmetry/beat-link-trigger)!

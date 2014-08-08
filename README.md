RERAN
=======

RERAN is a record and replay tool for the smartphone Android operating system. At a high level, it captures the input events sent from the phone to the operating system of a user session, and then allows the sequence of events to be sent into the phone programatically.

# Overview
RERAN consists of three steps. First events are recorded with the Android SDK's getevent tool, then the output is sent into RERAN's Translate program. The output from the Translate program is then sent into RERAN's Replay program
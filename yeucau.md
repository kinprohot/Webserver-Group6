CS631 -- Advanced Programming in the UNIX Environment - Group Project
Group Project: Write a simple web server
Summary
The objective of this assignment is for you to write a simple web server that speaks a limited version of HTTP/1.0 as defined in RFC1945. This gives you occasion to understand the process of reading an RFC and implementing a well-known protocol as well as a lot more coding experience using the socket(2) API.

You will implement the sws(1) command as described in the manual page provided to you here.

This is a non-trivial programming assignment -- do not postpone starting to work on this! Try to first get the basics right, then add functionality one by one, always ensuring that the added code did not break any previous functionality. If you're stuck, describe your problem on the mailing list or on Slack.

Team work
This assignment will be completed in groups. Your team will use git(1) to collaborate and track your progress.

Please note that all members of the team are expected to participate and need to contribute in equal parts. Your git commit log will be part of the final submission, and your ability to collaborate with your team mates a factor in your grade. Commit early, commit often, communicate regularly. Stronger team members have the responsibility to guide and mentor less advanced team members, not to write all the code themselves. I expect your final README to include details about the collaboration and division of work: summarize what parts where completed by whom, how you collaborated, and how each of you contributed.

Additional considerations
Please carefully read RFC1945 to understand version 1.0 of the Hyper Text Transfer Protocol.

Please carefully read RFC3875 to understand the Common Gateway Interface.

Your program should behave as one would expect from a regular system daemon. That is, it should detach from the controlling terminal and run in the background, accept multiple simultaneous connections, not generate any messages on stdout unless in debugging mode etc.

Your program does have to return normal HTTP/1.0 status codes as described in the RFC.

Note: your web server only needs to accept relative URIs (see RFC1945, Section 3.2.1); does not need to handle RFC1738 percent-encoded URIs; does not need to validate URIs against reserved character use.

While your server speaks HTTP/1.0, it should accept HTTP/1.1 requests and simply answer them as if they were HTTP/1.0 requests. This allows you to use a normal browser to access your server.

Supported Systems
As usual, your code must compile and run on our standard reference platform, NetBSD 11.0.

In addition, your code must also compile and run on these two systems:

linux.cs631.dotwtf.wtf # SSH host key fingerprints are:
SHA256:H7StG3NkV4KM3VgFu6D52KvPZSQuOpBqZHWfNITp2qw
SHA256:gJp2GfrUOzXsACwgv8gqc+TclUGFJp272q5x5arQ6Z4
SHA256:hzSsTKR/LqnZyO8GNC9XvwHl11x1OJb8zBPXGjORtog
omnios.cs631.dotwtf.wtf # SSH host key fingerprints are:
SHA256:rhmn5RgISE2wfCeoCHVIptTP73nhZRYgWxz+9xlA+7k
SHA256:mSrbAcHpz9qPbVEcFhGT0qQ749MTru0GnPHQXw/7iWg
SHA256:gDE9kckofygttcskxHpXO7K74+povSOGkIbmCvLW37E
Deliverables and Due Date
As always, your program will:

follow the general homework guidelines
follow the best coding practices discussed in class
be accompanied by a Makefile, README, checklist, and git log
You will submit a tar archive of all your files. The tar archive will be named "user1-user2-user3.tar", and extract into a directory named "user1-user2-user3", where user1 etc. are the usernames of your group's members.

The due date for this assignment is 2026-12-14 15:59:59. Please attach the file to an email sent from your @stevens.edu email address to jschauma@stevens.edu with a subject of "[CS631] group project".
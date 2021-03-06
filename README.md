# Command-line Getting Things Done App

## Usage

pygtd.py new stuff for inbox\
pygtd.py -d # Process inbox\
pygtd.py -n # Review Next Actions

## Background

There are probably a million todo apps, and about half of them market
themselves as being good for GTD. Who needs another one? I've tried dozens.
(Some of my favorites are MyLife Organized, Effexis Achieve Planner (hasn't
been updated since 2007, but it still works just fine), Doit.im, and
EveryTask.) But surprisingly few do what I would like them to do: guide me
through/automate the process of applying GTD methodology. (EveryTask and
Achieve Planner come the closest.)

Many try to please everyone by being flexible, accommodating whatever approach
or combination of approaches you prefer. That's fine if you have a clearly
defined approach of your own, and the discipline to apply it consistently.
However, I find that it usually leads to me getting lost in the complexity, or
I just end up becoming lazy and inconsistent in my implementation, and
eventually stop using it entirely.

GTD can be life-changing, but the hard part is applying it completely and
sticking with it consistently. So I'm trying to make it easier by automating
the process. Rather than simply a todo app that _can_ be used to apply GTD, I'm
writing a program to guide you through the process of actually applying GTD.

I've made several ways to quickly and easily capture any idea into your Inbox.
Then, when you decide to process your Inbox, it will go through each item,
FIFO, and you will be asked to decide what it is/what if anything you will do
about it. If it's a Next Action, you will be prompted to write a sentence
describing the specific physical action you will take, which will be added to
your Next Actions list. If it takes multiple steps, it's a Project, in which
case you will be prompted to describe what you're desired outcome is--what
exactly 'done' will look like. It's ok to decide to not decide; send it to your
Someday/Maybe list to reconsider later. By doing so, you have made a clear
distinction between things you are committed to getting done, and those you
aren't.

I've found a great deal of procrastination is really procrastination of decision-making. Setting aside time regularly to make decisions, and separating thinking from doing, is a big part of what makes GTD so powerful.

## Capturing Ideas to Your Inbox

For ease of use, make a short alias for pygtd. I use 'gt'. Then type the
command followed by text to be entered. Quotes are not necessary as long as you
don't use any special characters; if no optional argument flags are used (-i,
-q, etc), all arguments will be gathered into a single string, which will be
saved as a new Inbox item.

For rapid entry into Inbox without having to switch to a terminal, (assuming
you're using Linux) insure xterm is installed (since it's lightweight) and add
a shortcut key that runs the command 'xterm -e /bin/bash -c
/path/to/quick_add.py' (without quotes...change path as appropriate). -e
tells xterm to run the following command, and -c tells bash to run the
following command. This will run the command with bash even if bash isn't your
default shell. (I use zsh with OMZSH, which takes a little while to be ready
for input.) This will quickly open a window with a prompt. Add text and hit
enter, and the window will close and the text will be saved as a new Inbox
item.

quick_add.py -c will save the contents of your clipboard as a new Inbox item,
and could also be added to a keyboard shortcut.

The prompt can also be used to enter multiple tasks by calling the main program
with the option -Q. Hit Ctrl-C to exit.

## Where Are the Contexts?

I haven't done them yet. Maybe I will eventually, but it's not a priority.
Personally, I have one only context at the moment. Even for most people...
@Home, @Office, @Errands, and @Agendas[x-person] might be appropriate. Having
all those plus @Phone, @Computer, @Email, etc... Has no one else noticed
noticed that these are all the same device these days? Ok, there's stuff you
could do anywhere, and stuff you need to be sitting in front of your notebook
or desktop to do.

Anyway, the point is, contexts aren't the defining feature of GTD, or, for that
matter, the most important one. The point of contexts is so you can quickly see
what you could do at the moment. Far more important is that you collect ideas
as they occur, that you process them and maintain sharp boundaries between the
categories of Next Actions, Projects, etc., that each Next Action is a
specific physical action that doesn't have undecided intermediary steps...

# Waist Tracker

(Will probably move to separate repo at some point.)

CLI app for recording waist and shoulder measurements. Calculates your ideal
measurements.

## Usage

waist_tracker.py -c # record waist measurement in cm\
waist_tracker.py -i # record waist measurement in inches\
waist_tracker.py -s # record shoulder measurement in cm\
waist_tracker.py -si # record shoulder measurement in inches\
waist_tracker.py -l # view records

## Background

Inspired by the [Adonis
Index](http://www.criticalbench.com/review_adonis_index_workout.htm) program.
(I don't get any affiliate money.) It's a decent but pretty standard
body-building program. (Although it recommends against deadlifts, which is
controversial.) If you're a man and want a better body, you probably need more
muscle and less fat. I.e., broader shoulders and a slimmer waist. And I find
waist size a more appropriate metric than weight, since I don't care how much I
weigh, and muscle weighs more than fat. The main thing I got from the program
was specific numbers to aim for.

I lost 8 cm already! From [intermittent
fasting](https://en.wikipedia.org/wiki/Intermittent_fasting); ie, not eating
before 2 pm. But I find that keeping track of my measurements helps to stay
motivated.

You shouldn't stress too much about your physique, or compare yourself to some
idea of 'perfection', but if you want to get in better shape, it's useful to
know what shape you'd like to be in. It's hard to get somewhere if you don't
know where you're going. The ideal proportions are also useful for knowing when
enough is enough--it's possible to get too skinny or too big, so just getting
bigger or thinner isn't a well-defined goal.

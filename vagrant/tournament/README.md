# Mini Tournament

This is a mini swiss pairings tournament powered by a python backend and SQL
database. Go to [vagrant/tournament](https://github.com/AndreiCommunication/fullstack-nanodegree-vm/tree/master/vagrant/tournament) directory to look at the relevant files.

* `tournament.py` is the python interface interacting with the SQL database
* `tournament.sql` creates the empty SQL tables if they don't already exist
* `tournament_test.py` can be run using `python tournament_test.py` to ensure
that `tournament.py` is functioning correctly
* `server.py` is the python server for the HTML content
* `templates.py` includes the HTML templates used by `server.py`

### View

First, [log in to the virtual machine](#) and then do the following:

* Enter the tournament directory:

```
cd /vagrant/tournament
```

* Host the website on local host, port 8000

```
python server.py
```

* Open the url `http://localhost:8000/` in your browser to view.

## Interact

After hosting onto local host (see [View](#view) for instructions), interact
with the website in the following way:

Click on the **Show Players** tab to display currently registered player. To
delete a player click the 'X' at the end of the respective row.  To Add players,
click on **Add Player** and enter a non-empty string that has at most 9
characters.

Click on **Swiss Pairing** to go to the tournament view. Click on the player
that won the match to settle the match. Once all matches in a round are settled,
a new round will start IF a winner has not already been decided. A winner is
decided according to Swiss Tournament fashion and is the player with the most
wins after the correct number of rounds have been played:

```
Number of Rounds | Number of Players
        1                 2
        2                 3,4
        3                 5,6,7,8
        4                 9-16
```

And so on.

### Issues

* If more than 8 players are included in the tournament, problems with the way
the tournament is displayed arise. No effort was made to combat this as the
purpose of the project was not related to the frontend, but if someone wants
to use this project with this issue addressed, I'd be glad to address it.

* If an odd number of players are included, a bug occurs where the last playing
player will be swapped from round to round with the excluded player when they
have the same number of wins (probably 0 wins apiece). Again, no effort was made
to correct this, but it wouldn't be difficult to address if there is a need for
this.

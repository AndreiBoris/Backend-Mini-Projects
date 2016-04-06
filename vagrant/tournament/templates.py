# HTML template for the forum page
HTML_WRAP = '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swiss Tournament</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha/css/bootstrap.css">
  <style>
    .flexbox {
        display: flex;
    }
    .player-listing {
      display: flex;
      font-size: 1.2rem;
    }
    .player-listing + .player-listing {
        border-top: 1px solid #999;
        }
    .player-listing__name {
      width: 15em;
    }
    .player-listing__wins {
      width: 6em;
    }
    .player-listing__matches {
      width: 6em;
    }
    .player-listing__delete {
      margin-left: 0.75em;
    }
    .swiss-pairings {
        display: flex;
    }
    .match {
      display: flex;
      font-size: 1.2rem;
      width: 14em;
    }
    .match__player {
      width: 6em;
    }
    .match__player__button {
      width: 100%%;
    }
    .hidden {
      display: none;
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
</head>
<body>
  <div class="container">
    <div class="row" style="height: 5vh"></div>
    <div class="row" style="margin-bottom: 1em">
      <div class="col-xs-3">
        <button class="btn btn-default" id="add-player">Add Player</button>
      </div>
      <div class="col-xs-3">
        <form method="post" action="/ShowPlayers">
          <button class="btn btn-default" type="submit">Show Players</button>
        </form>
      </div>
      <div class="col-xs-3">
        <form method="post" action="/SwissPairings">
          <button class="btn btn-info" type="submit">Swiss Pairings</button>
        </form>
      </div>
      <div class="col-xs-3">
        <form method="post" action="/DeletePlayers">
          <button class="btn btn-danger" type="submit">Delete All</button>
        </form>
      </div>
    </div>
    <div class="row">
      <div class="col-xs-12">
        <form class="hidden" id="new-player-form" method="post" action="/AddPlayer">
          <input name="new-player"  type="text">
          <button class="btn btn-primary" type="submit">Add</button>
        </form>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        %s
      </div>
    </div>
  </div>
  <script>
    var $newPlayerForm = $('#new-player-form');
    $('#add-player').on('click', function() {
      $newPlayerForm.toggleClass('hidden');
    });
  </script>
</body>
</html>
'''

## HTML template for an individual player
PLAYER = '''\
    <li class="player-listing">
        <div class="player-listing__name">
            Name: <b>%(name)s</b>
        </div>
        <div class="player-listing__wins">
            Wins: <b>%(wins)s</b>
        </div>
        <div class="player-listing__matches">
            Matches: <b>%(matches)s</b>
        </div>
        <div>
            Tourny Wins: <b>%(tournyWins)s</b>
        </div>
        <div class="player-listing__delete">
            <form method="post" action="/DeleteOnePlayer">
                <input type="hidden" name="playerid" value="%(playerid)s">
                <button class="btn btn-danger" type="submit">X</button>
            </form>
        </div>

    </li>
'''

## HTML template for a match
PENDINGMATCH = '''\
    <li class="match">
        <div class="match__player">
            <form method="post" action="/ReportMatch">
                <input type="hidden" name="winnerid" value="%(first_player_id)s">
                <input type="hidden" name="matchindex" value="%(match_index)s">
                <button class="btn btn-info match__player__button" type="submit">%(first_player)s</button>
            </form>
        </div>
        <div class="match__vs">
            <b>v.</b>
        </div>
        <div class="match__player">
            <form method="post" action="/ReportMatch">
                <input type="hidden" name="winnerid" value="%(second_player_id)s">
                <input type="hidden" name="matchindex" value="%(match_index)s">
                <button class="btn btn-info match__player__button" type="submit">%(second_player)s</button>
            </form>
        </div>
    </li>
'''

## HTML template for a played match
PLAYEDMATCH = '''\
    <li class="match">
        <div class="match__player">
            <button class="btn btn-%(first_player_status)s match__player__button" type="submit">%(first_player)s</button>
        </div>
        <div class="match__vs">
            <b>v.</b>
        </div>
        <div class="match__player">
            <button class="btn btn-%(second_player_status)s match__player__button" type="submit">%(second_player)s</button>
        </div>
    </li>
'''

TOURNAMENTROUND = '<ul class="swiss-pairings">%s</ul>'

TOURNAMENTCONCLUSION = '''\
<h2> The winner is %s!</h2>
<div class="flexbox">
    <form method="post" action="/ReportTournament">
        <input type="hidden" name="storeTournament" value="store">
        <button class="btn btn-primary" type="submit">Store Tournament</button>
    </form>
    <form method="post" action="/ReportTournament">
        <input type="hidden" name="storeTournament" value="discard">
        <button class="btn btn-danger" type="submit">Discard Tournament</button>
    </form>
</div>
'''

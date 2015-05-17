from collections import defaultdict
from random import choice, randint

from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, CommitException, select, commit
from tornado.web import authenticated

from wlsports.db import Team as TeamEntity
from wlsports.db import Player as PlayerEntity
from wlsports.db import Sport as SportEntity
from wlsports.db import Game as GameEntity

from wlsports.handlers import APIHandler
from wlsports.util import invert_dict_nonunique


class Team(APIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "usernames": {"type": "array"},
                "name": {"type": "string"},
                "sport": {"enum": ["Basketball", "Soccer"]}
            },
            "required": ["usernames", "name", "sport"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
    )
    def put(self):
        """
        PUT to create a team

        * `name`
        * `usernames`: list of players in team (INCLUDING YOURSELF!!)
        * `sport`: One of "Basketball" or "Soccer"
        """
        attrs = dict(self.body)

        with db_session:
            if TeamEntity.get(name=attrs['name']):
                raise APIError(
                    409,
                    log_message="Team with name {} already exists!"
                    .format(attrs['name'])
                )

            # Add team mates
            players = []
            for pname in attrs["usernames"]:
                player = PlayerEntity.get(username=pname)
                api_assert(
                    player is not None,
                    400,
                    log_message="No player exists with name {}!".format(pname)
                )
                players.append(player)

            # Get sport
            sport = SportEntity[attrs['sport']]

            # Create team
            team = TeamEntity(
                name=attrs['name'],
                users=players,
                sport=sport,
                wins=0,
                losses=0,
                ties=0,
                points_ratio=0.0
            )

            return {'name': team.name}

    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "usernames": {"type": "array"},
                "name": {"type": "string"},
                "sport": {"enum": ["Basketball", "Soccer"]}
            }
        },
    )
    def get(self, name):
        """
        Get team with `name`
        """
        with db_session:
            team = TeamEntity.get(name=name)
            if team is None:
                raise APIError(
                    400,
                    log_message="Team with name {} does not exist!"
                    .format(name)
                )

            usernames = [p.username for p in team.users]
            name = team.name
            sport_name = team.sport.name

            return {
                "usernames": usernames,
                "name": name,
                "sport": sport_name
            }


class Matchmake(APIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "team_name": {"type": "string"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "game_id": {"type": "number"}
            }
        }
    )
    def post(self):
        """
        Does matchmaking by finding a rival team for the provided `team_name`,
        creates a new game with the two teams and returns the game_id
        for that game
        """
        team_name = self.body['team_name']
        with db_session:
            myteam = TeamEntity.get(name=team_name)
            sport_name = myteam.sport.name
            if myteam is None:
                raise APIError(
                    400,
                    log_message="Team with name {} does not exist!"
                    .format(team_name)
                )

            ### Figure out rival team

            # Find teams that are of the same sport and also
            # that they don't contain any players from myteam
            sport_teams = select(team for team in TeamEntity
                                 if team.sport.name == sport_name)[:]
            print sport_teams, [[player.username for player in team.users] for team in sport_teams ]
            myteam_names = [player.username for player in myteam.users]
            print myteam_names
            sport_teams = [team for team in sport_teams if all(
                player.username not in myteam_names for player in team.users
            )]
            print sport_teams
            sport_teams.append(myteam)
            num_teams = len(sport_teams)
            api_assert(
                num_teams > 1,
                409,
                "There are no other teams with all different people!"
            )

            overall_rankings = defaultdict(lambda: 0)

            teams_wlratio = sorted([
                (team, float(team.wins) / (team.losses or 1))
                for team in sport_teams
            ], key=lambda t: t[1], reverse=True)
            for i, (team, wlratio) in enumerate(teams_wlratio):
                overall_rankings[team.name] += i
            teams_pointsratio = sorted([
                (team, team.points_ratio) for team in sport_teams
            ], key=lambda t: t[1], reverse=True)
            for i, (team, points_ratio) in enumerate(teams_pointsratio):
                overall_rankings[team.name] += i

            myranking = overall_rankings[myteam.name]
            ranking_vals = overall_rankings.values()
            rankings_by_ranking = invert_dict_nonunique(overall_rankings)

            who_you_verse_index = None
            print(overall_rankings)
            while (who_you_verse_index not in ranking_vals):
                print(who_you_verse_index)
                from time import sleep
                sleep(0.4)
                if len(rankings_by_ranking) == 1:
                    who_you_verse_index = myranking
                else:
                    who_you_verse_index = choice(
                        [rval for rval in ranking_vals
                         if rval != myranking and
                         abs(rval - myranking) <= 10]
                    )

            rival_team_name = rankings_by_ranking[who_you_verse_index][0]
            if rival_team_name == myteam.name:
                rival_team_name = rankings_by_ranking[who_you_verse_index][1]
            rival_team = TeamEntity[rival_team_name]

            game = GameEntity(
                teams=[myteam, rival_team],
                host=PlayerEntity[self.get_current_user()]
            )
            commit()

            return {"game_id": game.id}

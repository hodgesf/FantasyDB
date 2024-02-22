from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL



app = Flask(__name__)
# Database configuration
app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
app.config["MYSQL_USER"] = "cs340_hodgesf"
app.config["MYSQL_PASSWORD"] = "6811"
app.config["MYSQL_DB"] = "cs340_hodgesf"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

app.secret_key = 'your_secret_key_here'

db = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET', 'POST'])
def users():
    title = "Users"
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        cur = db.connection.cursor()
        cur.execute("INSERT INTO Users (Username, Email) VALUES (%s, %s)", (username, email))
        db.connection.commit()
        cur.close()
        return redirect('/users')
    else:
        show_all = request.args.get('show_all') == 'true'  # Check if the show_all parameter is true

        if show_all:
            # If show_all is true, fetch all players
            cur = db.connection.cursor()
            cur.execute("""
                SELECT Users.Username, Users.Email, Users.UserID
                FROM Users""")
            users = cur.fetchall()
            cur.close()
        else:
            query = request.args.get('query')
            if query:
                # If there's a search query, filter players based on the query
                cur = db.connection.cursor()
                cur.execute("""
                    SELECT Users.Username, Users.Email
                    FROM Users
                    WHERE Users.Username LIKE %s OR Users.Email LIKE %s
                """, (f"%{query}%", f"%{query}%"))
                users = cur.fetchall()
                cur.close()
            else:
                users = []  # Initialize players list to empty if no search query

        return render_template('users.html', users=users, show_all=show_all, title=title)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        cur = db.connection.cursor()
        # Update the user's information in the database
        cur.execute("""
            UPDATE Users
            SET Username = %s, Email = %s
            WHERE UserID = %s
        """, (username, email, user_id))
        db.connection.commit()
        cur.close()
        return redirect('/users')
    else:
        # Fetch the user's current information to pre-populate the form
        cur = db.connection.cursor()
        cur.execute("SELECT Username, Email FROM Users WHERE UserID = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        
        print("User data:", user_data)  # Print user data for debugging
        
        if user_data:
            username = user_data['Username']  # Access values by key
            email = user_data['Email']  # Access values by key

    return render_template('edit_user.html', user_id=user_id, username=username, email=email, users=user_data)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        cur = db.connection.cursor()
        # Delete associated fantasy teams
        cur.execute("DELETE FROM FantasyTeams WHERE UserID = %s", (user_id,))
        # Delete the user
        cur.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
        db.connection.commit()
        flash('User and associated fantasy teams deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the user: ' + str(e), 'error')
        db.connection.rollback()
    finally:
        cur.close()
    return redirect('/users')



@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']

        # Example mapping of player positions to PlayerTypeID
        position_to_id = {
            "Quarterback": 1,
            "Wide Receiver": 2,
            "Running Back": 3,
            "Tight End": 4,
            "Kicker": 5,
            "Defense/Special Team": 6
        }

        player_type_id = position_to_id.get(position)

        if player_type_id:
            cur = db.connection.cursor()
            cur.execute("INSERT INTO Players (PlayerTypeID, PlayerName) VALUES (%s, %s)", (player_type_id, name))
            db.connection.commit()
            cur.close()
            return redirect('/players')
        else:
            return "Invalid player position"

    else:
        # If it's a GET request
        show_all = request.args.get('show_all') == 'true'  # Check if the show_all parameter is true

        if show_all:
            # If show_all is true, fetch all players
            cur = db.connection.cursor()
            cur.execute("""
                            SELECT Players.PlayerName, PlayerTypes.PlayerPosition, Players.PlayerID
                            FROM Players
                            JOIN PlayerTypes ON Players.PlayerTypeID = PlayerTypes.PlayerTypeID
                        """)

            players = cur.fetchall()
            cur.close()
        else:
            query = request.args.get('query')
            if query:
                # If there's a search query, filter players based on the query
                cur = db.connection.cursor()
                cur.execute("""
                    SELECT Players.PlayerName, PlayerTypes.PlayerPosition, Players.PlayerID
                    FROM Players
                    JOIN PlayerTypes ON Players.PlayerTypeID = PlayerTypes.PlayerTypeID
                    WHERE Players.PlayerName LIKE %s OR PlayerTypes.PlayerPosition LIKE %s
                """, (f"%{query}%", f"%{query}%"))
                players = cur.fetchall()
                cur.close()
            else:
                players = []  # Initialize players list to empty if no search query

        return render_template('players.html', players=players, show_all=show_all)

@app.route('/edit_player/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    if request.method == "POST":
        player_name = request.form['player_name']
        position = request.form['position']
        cur = db.connection.cursor()
        # Update the player's information in the database
        cur.execute("""
                        UPDATE Players
                        JOIN PlayerTypes ON Players.PlayerTypeID = PlayerTypes.PlayerTypeID
                        SET Players.PlayerName = %s, PlayerTypes.PlayerPosition = %s
                        WHERE Players.PlayerID = %s
                    """, (player_name, position, player_id))

        db.connection.commit()
        cur.close()
        return redirect('/players')
    else:
        # Fetch the player's current information to pre-populate the form
        cur = db.connection.cursor()
        cur.execute("""
                        SELECT Players.PlayerName, PlayerTypes.PlayerPosition
                        FROM Players
                        JOIN PlayerTypes ON Players.PlayerTypeID = PlayerTypes.PlayerTypeID
                        WHERE Players.PlayerID = %s
                    """, (player_id,))

        player_data = cur.fetchone()
        cur.close()
        
        print("Player data:", player_data)  # Print player data for debugging
        
        if player_data:
            player_name = player_data['PlayerName']  # Access values by key
            position = player_data['PlayerPosition']  # Access values by key

    return render_template('edit_player.html', player_id=player_id, player_name=player_name, position=position, players=player_data)


@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    try:
        cur = db.connection.cursor()
        # Delete the player
        cur.execute("DELETE FROM Players WHERE PlayerID = %s", (player_id,))
        db.connection.commit()
        flash('Player deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the player: ' + str(e), 'error')
        db.connection.rollback()
    finally:
        cur.close()
    return redirect('/players')


@app.route('/teams', methods=['GET', 'POST'])
def teams():
    title = "Teams"
    if request.method == 'POST':
        team_name = request.form['team_name']
        username = request.form['username']

        # Check if the user exists in the Users table
        cur = db.connection.cursor()
        cur.execute("SELECT UserID FROM Users WHERE Username = %s", (username,))
        user_result = cur.fetchone()

        if user_result:
            # User exists, retrieve their UserID
            user_id = user_result[0]
        else:
            # User does not exist, insert the new user and retrieve their UserID
            cur.execute("INSERT INTO Users (Username) VALUES (%s)", (username,))
            db.connection.commit()
            user_id = cur.lastrowid

        # Insert the new team with the obtained UserID
        cur.execute("INSERT INTO FantasyTeams (TeamName, UserID) VALUES (%s, %s)", (team_name, user_id))
        db.connection.commit()
        cur.close()

        return redirect('/teams')
    else:
        show_all = request.args.get('show_all') == 'true'  # Check if the show_all parameter is true

        if show_all:
            # If show_all is true, fetch all teams
            cur = db.connection.cursor()
            cur.execute("""
                SELECT FantasyTeams.TeamName, Users.Username, Users.Email, FantasyTeams.FantasyTeamID
                FROM FantasyTeams
                JOIN Users ON FantasyTeams.UserID = Users.UserID;
                """)
            teams = cur.fetchall()
            cur.close()
        else:
            query = request.args.get('query')
            if query:
                # If there's a search query, filter teams based on the query
                cur = db.connection.cursor()
                cur.execute("""
                    SELECT FantasyTeams.TeamName, Users.Username, Users.Email, FantasyTeams.FantasyTeamID
                    FROM FantasyTeams
                    JOIN Users ON FantasyTeams.UserID = Users.UserID
                    WHERE FantasyTeams.TeamName LIKE %s OR Users.Username LIKE %s OR Users.Email LIKE %s
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                teams = cur.fetchall()
                cur.close()
            else:
                teams = []  # Initialize teams list to empty if no search query

        return render_template('teams.html', title=title, teams=teams, show_all=show_all)
    

@app.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    if request.method == 'POST':
        team_name = request.form['team_name']
        username = request.form['username']

        cur = db.connection.cursor()
        try:
            # Update the team's information in the database
            cur.execute("""
                            UPDATE FantasyTeams 
                            JOIN Users ON FantasyTeams.UserID = Users.UserID
                            SET FantasyTeams.TeamName = %s, Users.Username = %s
                            WHERE FantasyTeams.FantasyTeamID = %s
                        """, (team_name, username, team_id))

            db.connection.commit()
            cur.close()
            return redirect('/teams')
        except Exception as e:
            # Handle any database errors
            print("Error updating team:", e)
            db.connection.rollback()
            cur.close()
            flash("An error occurred while updating the team.")
            return redirect('/teams')
    else:
        # Fetch the team's current information to pre-populate the form
        cur = db.connection.cursor()
        
        cur.execute("""
                        SELECT FantasyTeams.TeamName, Users.Username
                        FROM FantasyTeams
                        JOIN Users ON FantasyTeams.UserID = Users.UserID
                        WHERE FantasyTeams.FantasyTeamID = %s
                    """, (team_id,))
        team_data = cur.fetchone()
        cur.close()

        if team_data:
            team_name = team_data['TeamName']  # Access the first element for TeamName
            username = team_data['Username']   # Access the second element for Username
        
    

        return render_template('edit_team.html', teams=team_data, team_id=team_id, team_name=team_name, username=username)


@app.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    cur = db.connection.cursor()
    # Delete the team
    cur.execute("DELETE FROM FantasyTeams WHERE FantasyTeamID = %s", (team_id,))
    db.connection.commit()
    flash('Team deleted successfully.', 'success')
    cur.close()
    return redirect('/teams')




@app.route('/player_types', methods=['GET', 'POST'])
def player_types():
    title = "Player Types"
    if request.method == 'POST':
        player_position = request.form['player_position']

        # Check if the player type already exists in the PlayerTypes table
        cur = db.connection.cursor()
        cur.execute("SELECT PlayerTypeID FROM PlayerTypes WHERE PlayerPosition = %s", (player_position,))
        player_type_result = cur.fetchone()

        if player_type_result:
            # Player type exists, retrieve its PlayerTypeID
            player_type_id = player_type_result[0]
        else:
            # Player type does not exist, insert the new player type and retrieve its PlayerTypeID
            cur.execute("INSERT INTO PlayerTypes (PlayerPosition) VALUES (%s)", (player_position,))
            db.connection.commit()
            player_type_id = cur.lastrowid

        cur.close()

        return redirect('/player_types')
    else:
        show_all = request.args.get('show_all') == 'true'  # Check if the show_all parameter is true

        if show_all:
            # If show_all is true, fetch all player types
            cur = db.connection.cursor()
            cur.execute("SELECT * FROM PlayerTypes")
            player_types = cur.fetchall()
            cur.close()
        else:
            query = request.args.get('query')
            if query:
                # If there's a search query, filter player types based on the query
                cur = db.connection.cursor()
                cur.execute("SELECT * FROM PlayerTypes WHERE PlayerPosition LIKE %s", (f"%{query}%",))
                player_types = cur.fetchall()
                cur.close()
            else:
                player_types = []  # Initialize player types list to empty if no search query

        return render_template('player_types.html', title=title, player_types=player_types, show_all=show_all)
    

@app.route('/edit_player_type/<int:player_type_id>', methods=['GET', 'POST'])
def edit_player_type(player_type_id):
    if request.method == 'POST':
        player_position = request.form['position']

        cur = db.connection.cursor()
        # Update the team's information in the database
        cur.execute("""UPDATE PlayerTypes 
                        SET PlayerPosition = %s
                        WHERE PlayerTypeID = %s
                    """, (player_position, player_type_id))
        db.connection.commit()
        cur.close()
        return redirect('/player_types')
        
    else:
        # Fetch the team's current information to pre-populate the form
        cur = db.connection.cursor()
        cur.execute("""SELECT PlayerTypeID, PlayerPosition from PlayerTypes
                    WHERE PlayerTypeID = %s
                    """, (player_type_id,))
        team_data = cur.fetchone()
        cur.close()

        if team_data:
            player_type_id = team_data['PlayerTypeID']  # Access the first element for TeamName
            player_position = team_data['PlayerPosition']   # Access the second element for Username
        
        return render_template('edit_player_types.html', player_type_id=player_type_id, player_position=player_position)
    



@app.route('/delete_player_type/<int:player_type_id>', methods=['POST'])
def delete_player_type(player_type_id):
    cur = db.connection.cursor()
    # Delete the team
    cur.execute("DELETE FROM PlayerTypes WHERE PlayerTypeID = %s", (player_type_id,))
    db.connection.commit()
    flash('Team deleted successfully.', 'success')
    cur.close()
    return redirect('/player_types')



@app.route('/team_has_players', methods=['GET', 'POST'])
def team_has_players():
    title = "Team Has Players"
    if request.method == 'POST':
        fantasy_team_name = request.form['fantasy_team_name']
        player_name = request.form['player_name']

        # Fetch the last pick number for the given fantasy team
        cur = db.connection.cursor()


        # Insert the new player into the TeamHasPlayers table
        cur.execute("""
            INSERT INTO TeamHasPlayers (PlayerID, FantasyTeamID)
            VALUES (
            (SELECT PlayerID FROM Players WHERE PlayerName = %s),
            (SELECT FantasyTeamID FROM FantasyTeams WHERE TeamName = %s)
                    )""", (player_name, fantasy_team_name))
        db.connection.commit()
        cur.close()

        return redirect('/team_has_players')
    else:
        show_all = request.args.get('show_all') == 'true'  # Check if the show_all parameter is true

        if show_all:
            # If show_all is true, fetch all team-player associations
            cur = db.connection.cursor()
            cur.execute("""
                SELECT TeamHasPlayers.TeamHasPlayerID, Players.PlayerName, FantasyTeams.TeamName, TeamHasPlayers.PickNumber
                FROM TeamHasPlayers
                JOIN Players ON TeamHasPlayers.PlayerID = Players.PlayerID
                JOIN FantasyTeams ON TeamHasPlayers.FantasyTeamID = FantasyTeams.FantasyTeamID
                ORDER BY TeamHasPlayers.PickNumber ASC
                        """)
            team_has_players = cur.fetchall()
            cur.close()
        else:
            query = request.args.get('query')
            if query:
                # If there's a search query, filter team-player associations based on the query
                cur = db.connection.cursor()
                cur.execute("""
                    SELECT TeamHasPlayers.TeamHasPlayerID, Players.PlayerName, FantasyTeams.TeamName, TeamHasPlayers.PickNumber
                    FROM TeamHasPlayers
                    JOIN Players ON TeamHasPlayers.PlayerID = Players.PlayerID
                    JOIN FantasyTeams ON TeamHasPlayers.FantasyTeamID = FantasyTeams.FantasyTeamID
                    WHERE Players.PlayerName LIKE %s OR FantasyTeams.TeamName LIKE %s
                """, (f"%{query}%", f"%{query}%"))
                team_has_players = cur.fetchall()
                cur.close()
            else:
                team_has_players = []  # Initialize team-player associations list to empty if no search query

        return render_template('team_has_players.html', title=title, team_has_players=team_has_players, show_all=show_all)

@app.route('/edit_team_player/<int:team_has_player_id>', methods=['GET', 'POST'])
def edit_team_player(team_has_player_id):
    if request.method == 'POST':
        player_name = request.form['player_name']
        pick_number = request.form['pick_number']
        fantasy_team = request.form['fantasy_team']
        
        cur = db.connection.cursor()
        cur.execute("""
            UPDATE TeamHasPlayers
            SET PickNumber = %s
            WHERE TeamHasPlayerID = %s
        """, (pick_number, team_has_player_id))
        
        cur.execute("""
            UPDATE FantasyTeams
            SET TeamName = %s
            WHERE FantasyTeamID = (
                SELECT FantasyTeamID
                FROM TeamHasPlayers
                WHERE TeamHasPlayerID = %s
            )
        """, (fantasy_team, team_has_player_id))
        
        cur.execute("""
            UPDATE Players
            SET PlayerName = %s
            WHERE PlayerID = (
                SELECT PlayerID
                FROM TeamHasPlayers
                WHERE TeamHasPlayerID = %s
            )
        """, (player_name, team_has_player_id))
        
        db.connection.commit()
        cur.close()
        
        return redirect('/team_has_players')
    
    else:
        cur = db.connection.cursor()
        cur.execute("""
            SELECT 
                TeamHasPlayerID, 
                FantasyTeams.TeamName,
                Players.PlayerName,
                TeamHasPlayers.PickNumber
            FROM 
                TeamHasPlayers
            JOIN 
                FantasyTeams ON TeamHasPlayers.FantasyTeamID = FantasyTeams.FantasyTeamID
            JOIN 
                Players ON TeamHasPlayers.PlayerID = Players.PlayerID
            WHERE 
                TeamHasPlayerID = %s
        """, (team_has_player_id,))
        
        team_data = cur.fetchone()
        cur.close()

        if team_data:
            pick_number = team_data['PickNumber']  
            fantasy_team = team_data['TeamName']   
            player_name = team_data['PlayerName']
        
        return render_template('edit_team_player.html', pick_number=pick_number, fantasy_team=fantasy_team, player_name=player_name)

@app.route('/delete_team_player/<int:team_has_player_id>', methods=['POST'])
def delete_team_player(team_has_player_id):
    cur = db.connection.cursor()
    # Delete the team
    cur.execute("DELETE FROM TeamHasPlayers WHERE TeamHasPlayerID = %s", (team_has_player_id,))
    db.connection.commit()
    flash('Team deleted successfully.', 'success')
    cur.close()
    return redirect('/team_has_players')

if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask, render_template, url_for, flash, redirect
from forms import PlayerNumForm, NameForm, AnswerForm
from game import Question, Player, calcWinner

app = Flask(__name__)

app.config['SECRET_KEY'] = 'nusmmirhdl4472'

games = [
    {"game": 1,
    "teams": ["Man Utd", "Watford"],
    "result": 1
    },
    {"game": 2,
    "teams": ["Hudd", "Arsenal"],
    "result": 2
    },
    {"game": 3,
    "teams": ["Swansea", "Stoke"],
    "result": 3}
    ]

# player objects
players = []
fixList = []
results = []
# player scores dictionary
highscores = []
sortedArray = []
topTen = []

# when new game is started the players list is cleared
def resetGame():
    del players[:]

def resetHighscores():
    del highscores[:]


#read last line of scores.txt and add to highscores array
def addToHighscores():
    with open('scores.txt', 'r') as r:
        player = {}
        last_line = r.readlines()[-1]
        name, score = last_line.split(':')
        player['name'] = name
        player['score'] = score
        highscores.append(player)

#function to extract scores from scores.txt and create dictionary of highscore player objects
def getHighscores():
    with open('scores.txt', 'r') as r:
        for line in r:
            player = {}
            name, score = line.split(':')
            player['name'] = name
            player['score'] = score
            highscores.append(player)


# create fixtures for the game questions
def getFixtures():
    for game in games:
        home = game['teams'][0]
        away = game['teams'][1]
        result = game['result']
        question = Question(home, away, result)
        fixture = question.fixture()
        res = question.res()
        fixList.append(fixture)
        results.append(res)


getHighscores()
sortedHighscores = sorted(highscores, key=lambda item: item['score'], reverse=True)
topTen = sortedHighscores[0:10]

getFixtures()

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', games=games)


@app.route("/newgame", methods=['GET', 'POST'])
def newgame():
    resetGame()
    form = PlayerNumForm()
    if form.validate_on_submit():
        numPlayers = int(form.players.data)
        flash(f'{numPlayers} player game created!', 'dark')
        return redirect(url_for('enternames', id=1, numPlayers=numPlayers))
    return render_template('newgame.html', title='newgame', form=form )



@app.route("/enternames/<int:id>/<int:numPlayers>", methods=['GET', 'POST'])
def enternames(id, numPlayers):
    form = NameForm()
    if form.validate_on_submit():
        name = form.playername.data
        players.append(name)
        flash(f'Good luck {name}!! ', 'dark')
        if id < numPlayers:
            return redirect(url_for('enternames', id=id+1, numPlayers=numPlayers))
        elif id == numPlayers:
            return redirect(url_for('game', id=1, pNum=1, name=players[0], score=0, attempt=1))
    return render_template('enternames.html', form=form, id=id, numPlayers=numPlayers)


@app.route("/game/<int:id>/<int:pNum>/<name>/<int:score>/<int:attempt>", methods=['GET', 'POST'])
def game(id, pNum, name, score, attempt):
    form = AnswerForm()
    if form.validate_on_submit():
        name = name
        player = Player(name)
        plrAnswer = form.answer.data
        correctRes = results[id-1]
        #questions 1 and 2 of 3 1 player game
        if id <= 2:
            if attempt == 1:
                if plrAnswer != correctRes:
                    flash(f'Wrong answer {name}, you have one more attempt', 'dark')
                    return redirect(url_for('game', id=id, pNum=pNum, name=name, score=score, attempt=2))
                else:
                    flash(f'You are correct {name}', 'success')
                    return redirect(url_for('game', id=id+1, pNum=pNum, name=name, score=score+plrAnswer, attempt=1))
            elif attempt == 2:
                if plrAnswer != correctRes:
                    flash(f'Wrong answer {name}', 'dark')
                    return redirect(url_for('game', id=id+1, pNum=pNum, name=name, score=score, attempt=1))
                else:
                    flash(f'You are correct {name}', 'success')
                    return redirect(url_for('game', id=id+1, pNum=pNum, name=name, score=score+1, attempt=1))
        #last question 1 player game
        elif id == 3:
            if attempt == 1:
                if plrAnswer != correctRes:
                    flash(f'Wrong answer {name}, you have one more attempt', 'dark')
                    return redirect(url_for('game', id=3, pNum=pNum, name=name, score=score, attempt=2))
                else:
                    score = score + plrAnswer
                    return redirect(url_for('winner', pNum=pNum, name=name, score=score))
            if attempt == 2:
                if plrAnswer != correctRes:
                    flash(f'Wrong answer {name}', 'dark')
                    return redirect(url_for('winner', name=name, score=score))
                else:
                    score = score +1
                    return redirect(url_for('winner', name=name, score=score))
    return render_template('game.html', form=form, games=games,
                                   id=id, players=players, fixList=fixList, results=results, name=name, pNum=pNum)



@app.route("/winner/<string:name>/<int:score>", methods=['GET', 'POST'])
def winner(name, score):
    name = name
    score = score
    # if len(players) == 1:
    with open('scores.txt', 'a') as w:
        name = name
        score = score
        w.write(f'{name}:{score}\n')
        # if len(highscores) > 0:
        #     addToHighscores()
    # else:
    #     # Sort players by score
    #     players.sort(key=lambda x: x.score, reverse=True)
    #     if len(players) > 1:
    #         calcWinner(players[0], players[1])
    return render_template('winner.html', players=players, calcWinner=calcWinner, highscores=highscores, name=name, score=score)

print(highscores)

@app.route("/leaderboard", methods=['GET', 'POST'])
def leaderboard():
    resetHighscores()
    getHighscores()
    print(highscores)
    sortedHighscores = sorted(highscores, key=lambda item: item['score'], reverse=True)
    topTen = sortedHighscores[0:10]
    return render_template('leaderboard.html', title='leaderboard', highscores=highscores, sortedHighscores=sortedHighscores, topTen=topTen)


@app.route("/rules")
def rules():
    return render_template('rules.html')


if __name__ == '__main__':
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)
    #app.run(debug=True, host='0.0.0.0')
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True)
    app.run(host = os.environ.get("IP"),
            port = int(os.environ.get("PORT", 5000)),
            debug = True)

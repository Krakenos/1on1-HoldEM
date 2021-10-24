# 1on1-HoldEM
Server + Client of 1 on 1 Texas hold em poker. Server uses machine learning for opponent's moves.

# Client
Client is a basic game written in C# on Unity engine. Assets for cards were taken from [boardgame pack](https://www.kenney.nl/assets/boardgame-pack). None of the game logic happens on the client's side. Client sends and retrieves information from server via REST API.

# Server
Server is written in Python using Django and Django Rest frameworks along with Celery for asynchronous task for machine learning and synchronisation with google sheets. Moves made by player's opponent are based on data collected from previous games(we are learning from choices that player made and we are assuming these choices are correct, hence the goal is not to create the AI that always wins, but AI that makes human-like choices). Server performs fitting on 3 different machine learning algorythms(Gaussian naive bayes, Decision tree classifier, Random forest classifier) after a set amount of data is collected. Prediction for move is always made with algorythm that had the highest average accuracy on collected data. 

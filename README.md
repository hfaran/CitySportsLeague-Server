# WeLikeSports

Create an account. Join a team, or make one and invite friends. Matchmake to get matched for games with teams of a similar skill level. Enter your score to keep it fresh.

* Client: https://github.com/g4-SL/Windows10-GameMatchmaking
* Backend for submission for [IEEE Vancouver Windows 10 Hackathon](http://sites.ieee.org/vancouver-cs/archives/357)

## Setup

```bash
sudo pip install virtualenvwrapper
mkvirtualenv welikesports
pip install -r requirements.txt
```

## Usage

```bash
workon welikesports
cd src
./app.py --cookie-secret supersecuresecret --port 8585 --debug
```

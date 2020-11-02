# QotNews

## Self-hosting

Install dependencies:

```text
# Python:
$ sudo apt update
$ sudo apt install python3 python3-pip python-virtualenv python3-virtualenv

# Yarn / nodejs:
# from https://yarnpkg.com/lang/en/docs/install/#debian-stable
$ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
$ echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
$ sudo apt update
$ sudo apt install yarn
```

Clone this repo:

```text
$ git clone https://gogs.tannercollin.com/tanner/qotnews.git
$ cd qotnews
```

### API Server

Create a venv, activate it, and install:

```text
$ cd apiserver
$ virtualenv -p python3 env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```

Configure Praw for your Reddit account (optional):

* Go to https://www.reddit.com/prefs/apps
* Click "Create app"
* Name: whatever
* App type: script
* Description: blank
* About URL: blank
* Redirect URL: your GitHub profile
* Submit, copy the client ID and client secret into `settings.py` below

```text
(env) $ vim settings.py.example
```

Edit it and save it as `settings.py`.

Now you can run the server:

```text
(env) $ python server.py
```

### Readability Server

Used as a fallback if outline.com doesn't work

```text
# In a different terminal
$ cd ../readerserver
$ yarn install
```

Now you can run the server:

```text
$ node main.js
```

### Webclient

```text
# In a different terminal
$ cd ../webclient
$ yarn install
$ yarn build
```

The webclient is served by the API server, so you can close this terminal.

### Security

It's recommended to run QotNews as its own Linux user, kept alive with [supervisor](https://pypi.org/project/supervisor/).

Add a `qotnews` Linux user, move the repo into its home folder.

Configure `/etc/supervisor/conf.d/qotnews.conf`:

```text
[program:qotnewsapi]
user=qotnews
directory=/home/qotnews/qotnews/apiserver
command=/home/qotnews/qotnews/apiserver/env/bin/python -u server.py
stopsignal=INT
autostart=true
autorestart=true
stderr_logfile=/var/log/qotnewsapi.log
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/qotnewsapi.log
stdout_logfile_maxbytes=1MB

[program:qotnewsreader]
user=qotnews
directory=/home/qotnews/qotnews/readerserver
command=node main.js
autostart=true
autorestart=true
stderr_logfile=/var/log/qotnewsreader.log
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/qotnewsreader.log
stdout_logfile_maxbytes=1MB
```

To expose QotNews to http / https, you should configure nginx to reverse proxy:

```text
server {
    listen 80;

    root /var/www/html;
    index index.html index.htm;

    server_name news.t0.vc;

    location / {
        proxy_pass http://127.0.0.1:33842/;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then run `sudo certbot --nginx` and follow the prompts, enable redirect.

## License

This program is free and open-source software licensed under the MIT License. Please see the `LICENSE` file for details.

That means you have the right to study, change, and distribute the software and source code to anyone and for any purpose. You deserve these rights. Please take advantage of them because I like pull requests and would love to see this code put to use.

## Acknowledgements

This project was inspired by auto-playing videos, "pardon the interruption", paywalls, and GDPR cookie-banners.

Thanks to all the devs behind Python, Flask, Node, React, Readability.js, Outline, and Tildes (u/Deimos).

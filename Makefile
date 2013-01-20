REMOTE_HOST = eh13.c3pb.de
REMOTE_PATH = /www/register/srv
REMOTE_USER = root

FILES=index.cgi \
		*.py \
		settings.default.json \
		css/*.css \
		img/* \
		js/*

all: upload

pack: $(FILES)
	tar -cvzf eh13-register.tar.gz $?

upload: $(FILES)
	tar -c -f - $? | ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_PATH); tar xv"

upload-settings: settings.json
	scp settings.json $(REMOTE_USER)@$(REMOTE_HOST):/$(REMOTE_PATH)

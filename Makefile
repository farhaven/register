REMOTE_HOST = eh13.c3pb.de
REMOTE_PATH = /www/register/srv
REMOTE_USER = root

FILES=index.cgi \
		menu.py \
		html.py \
		userlist.py \
		usermgmt.py

all: upload

upload: $(FILES)
	pax -w $(.ALLSRC) | ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_PATH); tar xv"

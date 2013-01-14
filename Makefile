REMOTE_HOST = unobtanium.de
REMOTE_PATH = ~www/eh13-test/srv
REMOTE_USER = gbe

all: upload

upload: index.cgi html.py user.py test.sh
	pax -w $(.ALLSRC) | ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_PATH); pax -rv"

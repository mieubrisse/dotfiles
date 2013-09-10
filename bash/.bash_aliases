# Add Apache alias bins to PATH
APACHE_HOME=/etc/apache2
alias	go-apache="cd $APACHE_HOME"

# Fun decrypt stuff
alias decrypt=/home/mieubrisse/junk/decrypt/decrypt.py

# Map command to open last vim session
VIM_SESSION="~/.vim/.saved-session.vim"
alias   vims="vim -S $VIM_SESSION"

# Make piping to xclip go to X clipboard
alias xclip="xclip -selection 'clipboard'"

# Connect to remlnx with one command
alias remlnx-connect="ssh today1@remlnx.ews.illinois.edu"

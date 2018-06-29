# check if in virtual environment
# https://stackoverflow.com/questions/15454174/how-can-a-shell-function-know-if-it-is-running-within-a-virtualenv/15454916

python -c 'import sys; print(sys.real_prefix)' 2>/dev/null && INVENV=1 || INVENV=0

# echo $INVENV
# if $INVENV is 1, then in virtualenv

if [ $INVENV -eq 1 ]; then
    rm spotifyvis/migrations/00*
    sudo -u postgres psql -f reset_db.sql 
    python manage.py makemigrations
    python manage.py migrate 
fi

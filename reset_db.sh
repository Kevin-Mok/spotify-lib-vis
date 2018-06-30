# check if in virtual environment
# https://stackoverflow.com/questions/15454174/how-can-a-shell-function-know-if-it-is-running-within-a-virtualenv/15454916

# python -c 'import sys; print(sys.real_prefix)' 2>/dev/null && INVENV=1 || INVENV=0
# INVENV=$(python -c 'import sys; print ("1" if hasattr(sys, "real_prefix") else "0")')

# if $INVENV is 1, then in virtualenv
# echo $INVENV
# if [ $INVENV -eq 1 ]; then
rm login/migrations/0* api/migrations/0*
sudo -u postgres psql -f reset_db.sql 
python manage.py makemigrations
python manage.py migrate 
python manage.py runserver 
# fi

psql -c "drop database wotjam"
psql -c "create database wotjam"
python deploy_tool.py -t2 wotjam postgres
sh deploy.sh 
psql -f fixtures.sql wotjam
psql -f fixtures2.sql wotjam

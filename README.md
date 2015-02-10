To install the entire stack and run locally:

    git clone https://github.com/Caullyn/fullstack_after
    
Deploy DB Schema.
Create a PostgreSQL Database, and run deploy_tool.py for schema and deploy.sh for DB Functions (additional python packages may be required). Also optional fixture examples.

    psql -c 'drop database wotjam;'
    psql -c 'create database wotjam;'
    cd fullstack_after/tools/
    python deploy_tool.py -t2 wotjam postgres
    sh deploy.sh 
    psql -f fixtures.sql wotjam
    psql -f fixtures2.sql wotjam
    
Install Node packages

    cd ../node
    npm install express		
    npm install http-server	
    npm install node-dbi	
    npm install pg
    
Run nodeJS api

    node api.js

In a new terminal window, Run http-server

    cd public/
    http-server 

Open http://localhost:8080/event.html in browser
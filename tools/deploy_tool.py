#!/usr/bin/env python
# 
# |~\ _|)| _ |_|   
# |_/}_| |(_) _|   
#                                                                                                     
#
# This script deploys version migrations to Databases.
# Format: python deploy_tool.py <hostname> <db_name> <user_name>
#
#
############################################################################################################
from optparse import OptionParser
from fabric.api import run, local, env, settings
from datetime import timedelta, datetime
import getpass
import psycopg2
import os, sys
import time
import re	#regexp if needed

db_name = ''
user_name = ''
mig = 0
mig_file = ''
game_target = 0
ver_rank = 1
inst_rank = 1
init_rank   =   1   
success = False
version = 0
pw = ''
table = ''
dir = ''
host = ''
start_time = time.time()
description = ''

use = "usage: %prog [options] dbname username"
  
def insert_schema_version():
    global host, port, db_name, user_name, ver_rank, inst_rank, mig, mig_file, success, mig, table
    
    start_time = time.time()
    if mig_file:
        dbcon = psycopg2.connect(dbname=db_name, user=user_name, password=pw, host=host, port=port)
        cur = dbcon.cursor()
        cur.execute("DELETE FROM public.%(t)s WHERE script = '%(f)s;'" % {"f": mig_file, "t": table })
        dbcon.commit()
        if mig_file == '<< Flyway Init >>':
            cur.execute("INSERT INTO public.%(t)s SELECT %(y)s, %(r)s, %(v)s, '%(d)s', 'SQL', '%(f)s', 1, user, now(), 1, %(s)s, '','','','','','';" 
            % {"y": ver_rank, "r": inst_rank, "v": mig, "d":  mig_file, "f": mig_file, "s": success, "t": table})
            mig = 1
        else:
            statinfo = os.stat(mig_file)
            size = str(statinfo.st_size)
            cur.execute("INSERT INTO public.%(t)s SELECT %(y)s, %(r)s, %(v)s, '%(d)s', 'SQL', '%(f)s', %(z)s, user, now(), 0, %(s)s, '','','','','','';" 
            % {"y": ver_rank, "r": inst_rank, "v": mig, "d":  mig_file.split('__')[1].split('.sql')[0], "f": mig_file.split('/')[mig_file.count('/')], "s": success, "t": table, "z": size })
        dbcon.commit()
    else:
        print 'No migration file found for this target/game'
        sys.exit(-1)    

def update_schema_version():
    global host, port, db_name, user_name, ver_rank, inst_rank, mig, mig_file, success, mig, table, start_time, description

    exec_time = int(time.time() - start_time)
    dbcon = psycopg2.connect(dbname=db_name, user=user_name, password=pw, host=host, port=port)
    cur = dbcon.cursor()
    cur.execute("UPDATE public.%(t)s SET script = '%(f)s', success = %(s)s, execution_time = %(x)s, description = $$%(d)s$$ WHERE version = '%(v)s' and installed_on=(select max(installed_on) from public.%(t)s where version='%(v)s') ;" % {"f": mig_file.split('/')[mig_file.count('/')], "s": success, "v": mig, "t": table, "x": exec_time, "d": description })
    dbcon.commit()


def parse_json(mig_file):
	str = mig_file.split('__')[1].split('.sql')[0]
	sf = open(mig_file).read()
	pos = sf.find('/*')
	if pos >= 0:
		cm = sf[pos:sf.find('*/')]
	else:
		return 'No comments found';
	pos = cm.find('{')
	if pos >= 0:
		cm = cm[pos:(cm.rfind('}')+1)]
	else:
		return 'Json without finishing bracket';
	import json
	json_str = cm.replace('\r', '\\r')
	json_str = cm.replace('\n', '\\n')	#we want to save CR in json as is
	#print json_str
	json_str = json.loads(json_str)
	UseDescription(json_str)
	WarnAndPause(json_str)

def WarnAndPause(act):
	if 'Pause' in act:
		if act['Pause']['Action'] == True :
			os.system('echo "\033[1;33;41m This version contains warning: \033[0;30;41m'+act['Pause']['Message']+' \033[0m"')
			wait = raw_input("\033[0;34;47m \"Ctrl+C\" to stop or \"Enter\" to Continue  \033[0m")
			#print('' + len(wait) + '')
			#exit(1)

def UseDescription(str):
	global description
	description = mig_file.split('__')[1].split('.sql')[0]
	if 'Description' in str:
		description = str['Description']
	print '\033[0;30;47m ::description found:   \033[0m \033[0;33;40m' + description + " \033[0m"

def roll_on_grants():
    global host, port, db_name, user_name, inst_rank, init_rank
    scripts = ['']
    if (target>0 or game>0) and inst_rank != init_rank: # and db_name  == 'odobo_cloud'
        scripts = ['../scripts/permissions/cloud_grant/pilot.sql']
        print chr(10)+'---------------------    Working on permissions for CLOUD DataBase   ---------------------'+chr(10)
    if op_target>0 and inst_rank != init_rank: #db_name  == 'operator_cloud':
        scripts = ['../scripts/permissions/operator_grant/step1.sql','../scripts/permissions/operator_grant/step2.sql']
        print chr(10)+'---------------------    Working on permissions for OPERATOR DataBase   ---------------------'+chr(10)
    if loc_target>0 and inst_rank != init_rank: #db_name  == 'operator_cloud':
        scripts = ['../scripts/permissions/localisation_grant/step1.sql','../scripts/permissions/localisation_grant/step2.sql']
        print chr(10)+'---------------------    Working on permissions for LOCALISATION DataBase   ---------------------'+chr(10)
    if fin_target>0 and inst_rank != init_rank: #db_name  == 'operator_cloud':
        scripts = ['../scripts/permissions/finance_grant/grants.sql']
        print chr(10)+'---------------------    Working on permissions for FINANCE DataBase   ---------------------'+chr(10)
    if wallet_target>0 and inst_rank != init_rank: #db_name  == 'operator_cloud':
        scripts = ['../scripts/permissions/wallet_grant/step1.sql','../scripts/permissions/wallet_grant/step2.sql']
        print chr(10)+'---------------------    Working on permissions for WALLET DataBase   ---------------------'+chr(10)
    if not game_target>0:
        for i in scripts:
            if len(i) < 1 :
                print chr(9) + ':: No permission scripts executed...'
            else:
                print chr(10) + chr(9) + ':: ' + i + ' permission scripts executed'
                q = "psql -h %(h)s -p %(p)s -f %(ss)s %(d)s %(u)s" % {"h":host, "p": port, "d":db_name,"u":user_name, "t": table, "ss":i}
                os.system(q)

def direction(dirname):
    print dirname
    Para = '/odb_database'
    Donde = os.getcwd()
    if Para in Donde:
        Strpos = Donde.find(Para) + len(Para)
        Pwd = Donde[:Strpos]
        DirectoryStructure  = {'tools': 'tools/', 'versions':'versions/', 'pythetic_fail':'scripts/replication/pythetic_fail/', 'deploy_tool':'tools/deploy_tool/', 'deploy_\s':'tools/deploy_tool/log/', 'games/game_100':'games/game_100/'} 
        return Pwd + '/' + DirectoryStructure[dirname]
    else:
        print Para+' not found in CWD, you should be inside to avoid mistake in detecting working directories ...'
        #exit(1)

def init():
    global host, port, db_name, user_name, ver_rank, inst_rank, mig, mig_file, success, dir, table, target, op_target, init_rank
    
    dbcon = psycopg2.connect(dbname=db_name, user=user_name, password=pw, host=host, port=port)
    cur = dbcon.cursor()
    cur.execute("SELECT schemaname FROM pg_tables WHERE tablename = '%(t)s' LIMIT 1;" % {"t": table})
    dep = cur.fetchone()
    if dep is None:
        cur.execute("CREATE TABLE public.%(t)s (\
            version_rank    integer                      not null,\
            installed_rank  integer                      not null,\
            version         character varying(50)        not null,\
            description     character varying(512)       not null,\
            type            character varying(20)        not null,\
            script          character varying(1000)      not null,\
            checksum        integer                      ,\
            installed_by    character varying(30)        not null,\
            installed_on    timestamp without time zone  not null default now(),\
            execution_time  integer                      not null,\
            success         boolean                      not null,\
            wp_sprint       varchar(200),\
            war_file        varchar(200),\
            snapshot        varchar(200),\
            rc              varchar(200),\
            release         varchar(200),\
            jira_ticket     varchar(200)\
            );" % {"t": table})
        dbcon.commit()
        mig, ver_rank, inst_rank = 0, 0, 0
        mig_file = '<< Flyway Init >>'
        success = True
        insert_schema_version()
    elif target > 0 or op_target > 0:    
    	cur.execute("alter table public.schema_version alter column description type character varying (512);")
    	dbcon.commit()
        cur.execute("SELECT column_name\
                       FROM information_schema.columns\
                      WHERE table_schema='public' AND table_name='schema_version' AND column_name = 'wp_sprint';")
        new_col = cur.fetchone()
        if new_col is not None:
            new_col = new_col[0]
        if new_col != 'wp_sprint':
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN wp_sprint   VARCHAR(200)")
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN war_file    VARCHAR(200)")
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN snapshot    VARCHAR(200)")
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN rc          VARCHAR(200)")
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN release     VARCHAR(200)")
            cur.execute("ALTER TABLE public.schema_version ADD COLUMN jira_ticket VARCHAR(200)")
            dbcon.commit()

    with settings(warn_only=True):
        mig_query = "psql -h %(h)s -p %(p)s -tc 'SELECT version, version_rank, installed_rank FROM public.%(t)s WHERE installed_rank = (SELECT MAX(installed_rank) FROM public.%(t)s WHERE success is true) and success is true ORDER BY version_rank;' %(d)s %(u)s" % {"h":host, "p": port, "d":db_name,"u":user_name, "t": table}
        mig_tup = local(mig_query, capture=True)    
        if table == 'schema_version' and target > 0:
            dir = 'versions'
        elif table == 'schema_version' and op_target > 0:
            dir = 'versions_operator'
        elif table == 'schema_version' and wallet_target > 0:
            dir = 'versions_wallet'
        elif table == 'schema_version' and loc_target > 0:
            dir = 'versions_loc'
        elif table == 'schema_version' and fin_target > 0:
            dir = 'versions_finance'
        else:
            dir = 'games/' + table
        if mig_tup:
            mig, ver_rank, inst_rank = mig_tup.split("|")[0], mig_tup.split("|")[1], mig_tup.split("|")[2]
            init_rank   =   inst_rank
            #mig_file = local("ls "+direction('versions')+"/V%(m)s__*" % {"m": int(mig), "d": dir}, capture=True)
            mig_file = local("ls ../%(d)s/V%(m)s__*" % {"m": int(mig), "d": dir}, capture=True)
        else:
            print 'Error determining version from table: %(t)s' % {"t": table}
            sys.exit(-1)
        print '\033[0;32;40m Current schema version: \033[0m \033[0;31;40m %(m)s \033[0m' % {"m": mig}
        print mig_file
    dbcon.commit()
    cur.close()
    dbcon.close()

def deploy():
    global host, lockfile, port, db_name, user_name, mig, mig_file, ver_rank, inst_rank, dir, target, op_target, wallet_target, loc_target, fin_target, success, game, game_target, start_time, description
    
    im = int(mig)
    if target > 0:
        t = int(target)
    elif op_target > 0:
        t = int(op_target)
    elif wallet_target > 0:
        t = int(wallet_target)
    elif game_target > 0:
        t = int(game_target)
    elif loc_target > 0:
        t = int(loc_target)
    elif fin_target > 0:
        t = int(fin_target)
    else:
        t = 999
    if t < im:
        print ' |~\ _|)| _ |_|'
        print ' |_/}_| |(_) _|'
        print 'ERROR: target must be greater than current versions. %(t)s < %(m)s' % {"t": t, "m": im}
        parser.print_help()
        exit(-1)
    if mig == 0:
        insert_schema_version()
    for i in range(t - im):
        start_time = time.time()
        im = im + 1   
        ver_rank = str(int(ver_rank) + 1)
        inst_rank = str(int(inst_rank) + 1)
        mig = im
        with settings(warn_only=True):     
            mig_file = local("ls ../%(d)s/V%(m)s__*" % {"m": im, "d": dir}, capture=True)
            mig_file = mig_file
            highlight_version = '\033[0;32;40m' + re.sub(r'V([0-9]{1,})__', r'V\033[0;31;40m\1\033[0m\033[0;32;40m__', mig_file) + '\033[0m '
            print highlight_version
        if mig_file:
            parse_json(mig_file)
            insert_schema_version()
            print 'Deploying file: %(f)s' % {"f": mig_file}
            deploy_op = local("psql -h %(h)s -f %(f)s -p %(p)s %(d)s %(u)s 2>&1" % {"h":host, "f": mig_file, "p": port, "d":db_name,"u":user_name}, capture=True)
            print deploy_op
            print deploy_op.stderr;
            if "ERROR" in deploy_op or "ROLLBACK" in deploy_op:
                print ' |~\ _|)| _ |_|'
                print ' |_/}_| |(_) _|'
                print 'ERROR or ROLLBACK from psql detected. exiting.'
                success = False
                update_schema_version()
                exit(-1)
            else:
                success = True
                update_schema_version()
                success = False
        else:
            print 'Notice: target option higher than migration files located in odb_database/%(d)s. Successfully deployed to version %(m)s' % {"m": im-1, "d": dir}
            exit(-1)
            
parser = OptionParser(usage = use)
parser.add_option("-t", "--target",
                 action="store",  
                 dest="target", help="Cloud version to deploy up to")
parser.add_option("-o", "--operator_target",
                 action="store",  
                 dest="op_target", help="Operator version to deploy up to")
parser.add_option("-w", "--wallet_target",
                 action="store",  
                 dest="wallet_target", help="Wallet version to deploy up to")
parser.add_option("-c", "--loc_target",
                 action="store",  
                 dest="loc_target", help="Localisation version to deploy up to")
parser.add_option("-m", "--fin_target",
                 action="store",  
                 dest="fin_target", help="Finance database schema version to deploy up to")
parser.add_option("-g", "--game",
                 action="store",  
                 dest="game", help="Game id to deploy up to (Game OR Version must be specified)")
parser.add_option("-f", "--gametarget",
                 action="store",  
                 dest="game_target", help="Game target version")
parser.add_option("-s", "--hostname",
                 action="store",  default="localhost",
                 dest="host", help="Database Hostname. Default is localhost")
parser.add_option("-l", "--lockfile",
                 action="store",  default="/tmp/",
                 dest="lockfile", help="Postgres lock file.")
parser.add_option("-p", "--port",
                 action="store",  default="5432",
                 dest="port", help="Port which postgres runs on.")
options, args = parser.parse_args()
target = options.target
op_target = options.op_target
wallet_target = options.wallet_target
loc_target = options.loc_target
fin_target = options.fin_target
port =  options.port
game = options.game
game_target = options.game_target

if options.host == "localhost":
    host = options.lockfile 
else:
    lockfile = options.host 
    host = options.host
try:
    db_name = "{0}".format(args[0])
    user_name = "{0}".format(args[1])
except:
    print ' |~\ _|)| _ |_|'
    print ' |_/}_| |(_) _|'
    print 'ERROR: arguments missing'
    parser.print_help()
    exit(-1)
if (target == 0 or not target) and (game == 0 or not game) and (op_target == 0 or not op_target) and (wallet_target == 0 or not wallet_target) and (loc_target == 0 or not loc_target) and (fin_target == 0 or not fin_target):
    print ' |~\ _|)| _ |_|'
    print ' |_/}_| |(_) _|'
    print 'ERROR: target or game must be assigned'
    parser.print_help()
    exit(-1)
elif ( target > 0 and game > 0 ) or ( op_target > 0 and game > 0 ) or ( target > 0 and op_target > 0 ):
    print ' |~\ _|)| _ |_|'
    print ' |_/}_| |(_) _|'
    print 'ERROR: Please only specify target, op_target or game individually, not both.'
    parser.print_help()
    exit(-1)
if game > 0:
    table = 'game_%(g)s' % {"g": game}
else:
    table = 'schema_version'
if sys.stdin.isatty():
	pw = getpass.getpass()
else:
	pw=sys.stdin.readline().rstrip()
###	pw = getpass.getpass()
init()
deploy()
roll_on_grants()

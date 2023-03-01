# Renew database  -- Not working now! use delete_nautobot.py, this will destroy the containers
### Backup empty DB:
    pg_dump -U nautobot nautobot > nautobot_empty.sql

### Restore empty DB:

        dropdb -U nautobot nautobot --force
        psql -U nautobot -c 'create database nautobot'
        psql -U nautobot nautobot < nautobot_empty.sql